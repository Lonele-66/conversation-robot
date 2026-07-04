import os
import json
from dotenv import load_dotenv
import dashscope

load_dotenv()

api_key = os.getenv("API_KEY")
dashscope.api_key = api_key

DOCUMENTS_DIR = "documents"
VECTOR_DB_DIR = "vector_db"


def load_txt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    return [{"content": content, "metadata": {"source": file_path, "type": "txt"}}]


def load_pdf_file(file_path):
    try:
        from pypdf import PdfReader
        reader = PdfReader(file_path)
        docs = []
        for page_num, page in enumerate(reader.pages):
            content = page.extract_text()
            if content:
                docs.append({
                    "content": content,
                    "metadata": {"source": file_path, "type": "pdf", "page": page_num + 1}
                })
        return docs
    except ImportError:
        print("需要安装 pypdf: pip install pypdf")
        return []


def load_docx_file(file_path):
    try:
        from docx import Document
        doc = Document(file_path)
        content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
        return [{"content": content, "metadata": {"source": file_path, "type": "docx"}}]
    except ImportError:
        print("需要安装 python-docx: pip install python-docx")
        return []


def load_documents(dir_path):
    documents = []
    if not os.path.exists(dir_path):
        print(f"目录 {dir_path} 不存在，创建示例文档")
        os.makedirs(dir_path, exist_ok=True)
        
        with open(os.path.join(dir_path, "example.txt"), "w", encoding="utf-8") as f:
            f.write("张三的爸爸是里斯\n李四今年25岁\n王五喜欢打篮球")
        
        with open(os.path.join(dir_path, "company.txt"), "w", encoding="utf-8") as f:
            f.write("公司成立于2020年\n公司地址在北京市朝阳区\n公司有200名员工")
    
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if filename.endswith(".txt"):
            documents.extend(load_txt_file(file_path))
        elif filename.endswith(".pdf"):
            documents.extend(load_pdf_file(file_path))
        elif filename.endswith(".docx"):
            documents.extend(load_docx_file(file_path))
    
    print(f"共加载 {len(documents)} 个文档")
    return documents


def split_text(documents, chunk_size=500, chunk_overlap=50):
    split_docs = []
    for doc in documents:
        content = doc["content"]
        if len(content) <= chunk_size:
            split_docs.append(doc)
        else:
            chunks = []
            for i in range(0, len(content), chunk_size - chunk_overlap):
                chunk = content[i:i + chunk_size]
                chunks.append({
                    "content": chunk,
                    "metadata": doc["metadata"]
                })
            split_docs.extend(chunks)
    print(f"拆分后共 {len(split_docs)} 个文本块")
    return split_docs


def get_embedding(text):
    response = dashscope.TextEmbedding.call(
        model=dashscope.TextEmbedding.Models.text_embedding_v1,
        input=text
    )
    if response.status_code == 200:
        return response.output["embeddings"][0]["embedding"]
    else:
        raise Exception(f"Embedding API调用失败: {response.message}")


def save_vectors(documents):
    os.makedirs(VECTOR_DB_DIR, exist_ok=True)
    
    vectors = []
    for i, doc in enumerate(documents):
        embedding = get_embedding(doc["content"])
        vectors.append({
            "id": str(i),
            "embedding": embedding,
            "content": doc["content"],
            "metadata": doc["metadata"]
        })
        print(f"已处理 {i + 1}/{len(documents)}")
    
    with open(os.path.join(VECTOR_DB_DIR, "vectors.json"), "w", encoding="utf-8") as f:
        json.dump(vectors, f, ensure_ascii=False, indent=2)
    
    print(f"向量已保存到 {VECTOR_DB_DIR}/vectors.json")
    return vectors


def load_vectors():
    vectors_file = os.path.join(VECTOR_DB_DIR, "vectors.json")
    if os.path.exists(vectors_file):
        with open(vectors_file, "r", encoding="utf-8") as f:
            vectors = json.load(f)
        if vectors and isinstance(vectors, list) and len(vectors) > 0:
            print(f"从本地加载了 {len(vectors)} 个向量")
            return vectors
        else:
            print("本地向量文件为空，需要重新构建知识库")
            return None
    return None


def cosine_similarity(vec1, vec2):
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    magnitude1 = (sum(a * a for a in vec1)) ** 0.5
    magnitude2 = (sum(b * b for b in vec2)) ** 0.5
    if magnitude1 == 0 or magnitude2 == 0:
        return 0
    return dot_product / (magnitude1 * magnitude2)


def retrieve(question, vectors, top_k=3):
    question_embedding = get_embedding(question)
    
    similarities = []
    for vec in vectors:
        sim = cosine_similarity(question_embedding, vec["embedding"])
        similarities.append((sim, vec))
    
    similarities.sort(reverse=True, key=lambda x: x[0])
    top_docs = [item[1] for item in similarities[:top_k]]
    
    print(f"\n检索到 {len(top_docs)} 个相关文档:")
    for i, doc in enumerate(top_docs):
        print(f"{i + 1}. 相似度: {doc['embedding'][0][:5]}... 来源: {doc['metadata'].get('source', 'unknown')}")
    
    return top_docs


def generate_answer(question, context_docs):
    context = "\n\n".join([doc["content"] for doc in context_docs])
    
    if context.strip():
        prompt = f"""基于以下参考资料回答用户的问题。如果参考资料中没有相关信息，请直接回答，不要说"我不知道"。

参考资料:
{context}

用户问题: {question}

请根据参考资料回答问题，如果参考资料中没有相关信息，请直接回答用户的问题:"""
    else:
        prompt = f"""请回答用户的问题: {question}"""
    
    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_turbo,
        prompt=prompt,
        temperature=0.7
    )
    
    if response.status_code == 200:
        return response.output.text
    else:
        return f"LLM调用失败: {response.message}"


def rag_pipeline(question):
    vectors = load_vectors()
    
    if vectors is None:
        print("未找到本地向量，开始构建知识库...")
        documents = load_documents(DOCUMENTS_DIR)
        split_docs = split_text(documents)
        vectors = save_vectors(split_docs)
    
    context_docs = retrieve(question, vectors)
    answer = generate_answer(question, context_docs)
    
    return answer


if __name__ == "__main__":
    print("RAG文档问答系统")
    print("=" * 50)
    
    while True:
        question = input("\n请输入你的问题 (输入 'exit' 退出): ")
        if question.lower() == "exit":
            print("再见！")
            break
        
        try:
            answer = rag_pipeline(question)
            print(f"\n回答: {answer}")
        except Exception as e:
            print(f"\n错误: {str(e)}")