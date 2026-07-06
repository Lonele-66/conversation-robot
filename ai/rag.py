import os
import json
import numpy as np
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

VECTOR_DB_DIR = os.path.join(os.path.dirname(__file__), "../vector_db")
DOCUMENTS_DIR = os.path.join(os.path.dirname(__file__), "../documents")
os.makedirs(VECTOR_DB_DIR, exist_ok=True)
os.makedirs(DOCUMENTS_DIR, exist_ok=True)

class RAGSystem:
    def __init__(self):
        self.vectors = []
        self.embedding_model = None
        self._init_embedding()
        self._auto_load_documents()
    
    def _init_embedding(self):
        try:
            import dashscope
            self.embedding_model = dashscope
            self.embedding_model.api_key = os.getenv("DASHSCOPE_API_KEY")
        except ImportError:
            raise ImportError("Please install dashscope: pip install dashscope")
    
    def _auto_load_documents(self):
        if not self._load_vectors():
            from .document_loader import DocumentLoader
            loader = DocumentLoader()
            docs = []
            
            for filename in os.listdir(DOCUMENTS_DIR):
                file_path = os.path.join(DOCUMENTS_DIR, filename)
                if os.path.isfile(file_path):
                    file_ext = filename.split(".")[-1].lower()
                    if file_ext in ["txt", "pdf", "docx"]:
                        try:
                            file_docs = loader.load(file_path, file_ext)
                            docs.extend(file_docs)
                        except Exception as e:
                            print(f"Failed to load {filename}: {e}")
            
            if docs:
                self.add_documents(docs)
    
    def get_embedding(self, text: str) -> List[float]:
        if not self.embedding_model:
            self._init_embedding()
        
        response = self.embedding_model.TextEmbedding.call(
            model=self.embedding_model.TextEmbedding.Models.text_embedding_v1,
            input=text
        )
        
        if response.status_code == 200:
            return response.output["embeddings"][0]["embedding"]
        else:
            raise Exception(f"Embedding API error: {response.message}")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        if np.linalg.norm(vec1) == 0 or np.linalg.norm(vec2) == 0:
            return 0.0
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))
    
    def add_documents(self, documents: List[Dict]):
        for doc in documents:
            content = doc.get("content", "")
            if content:
                embedding = self.get_embedding(content)
                self.vectors.append({
                    "content": content,
                    "embedding": embedding,
                    "metadata": doc.get("metadata", {})
                })
        self._save_vectors()
    
    def _save_vectors(self):
        vectors_file = os.path.join(VECTOR_DB_DIR, "vectors.json")
        with open(vectors_file, "w", encoding="utf-8") as f:
            json.dump(self.vectors, f, ensure_ascii=False, indent=2)
    
    def _load_vectors(self):
        vectors_file = os.path.join(VECTOR_DB_DIR, "vectors.json")
        if os.path.exists(vectors_file):
            with open(vectors_file, "r", encoding="utf-8") as f:
                vectors = json.load(f)
            if vectors and isinstance(vectors, list) and len(vectors) > 0:
                self.vectors = vectors
                return True
        return False
    
    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        if not self.vectors:
            self._load_vectors()
        
        if not self.vectors:
            return []
        
        query_embedding = self.get_embedding(query)
        similarities = []
        
        for i, vec in enumerate(self.vectors):
            sim = self.cosine_similarity(query_embedding, vec["embedding"])
            similarities.append((i, sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for idx, sim in similarities[:top_k]:
            vec = self.vectors[idx]
            results.append({
                "content": vec["content"],
                "similarity": sim,
                "metadata": vec["metadata"]
            })
        
        return results
    
    def query(self, question: str) -> Tuple[str, List[str], float]:
        results = self.search(question, top_k=3)
        
        if not results:
            return self._generate_answer(question, []), [], 0.0
        
        context = "\n\n".join([r["content"] for r in results])
        sources = [r["metadata"].get("source", "unknown") for r in results]
        confidence = results[0]["similarity"] if results else 0.0
        
        answer = self._generate_answer(question, results)
        
        return answer, sources, confidence
    
    def _generate_answer(self, question: str, context_docs: List[Dict]) -> str:
        context = "\n\n".join([doc["content"] for doc in context_docs])
        
        if context.strip():
            prompt = f"""你是四川大学锦江学院的智能问答助手，专门为学生提供校园信息查询服务。

参考资料:
{context}

用户问题: {question}

请根据参考资料回答用户的问题，回答要简洁明了，格式清晰。如果参考资料中有多个相关信息，请分点列出。

回答格式要求:
1. 直接回答问题，不要使用Markdown格式
2. 如果有多个答案，用"- "开头的列表形式
3. 在回答末尾标注来源信息，格式为：【来源: 文件名】

如果参考资料中没有相关信息，请礼貌地告诉用户无法找到相关信息。"""
        else:
            prompt = f"""你是四川大学锦江学院的智能问答助手。

用户问题: {question}

请回答用户的问题。如果无法回答，请礼貌地说明。"""
        
        response = self.embedding_model.Generation.call(
            model=self.embedding_model.Generation.Models.qwen_turbo,
            prompt=prompt,
            temperature=0.7
        )
        
        if response.status_code == 200:
            return response.output.text
        else:
            return f"LLM调用失败: {response.message}"
    
    def get_document_sources(self) -> List[str]:
        sources = set()
        for vec in self.vectors:
            source = vec["metadata"].get("source", "")
            if source:
                sources.add(os.path.basename(source))
        return sorted(list(sources))
