import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class QuestionRewriter:
    def __init__(self):
        try:
            import dashscope
            self.llm = dashscope
            self.llm.api_key = os.getenv("DASHSCOPE_API_KEY")
        except ImportError:
            self.llm = None
    
    def rewrite(self, question: str, context: Optional[List[str]] = None) -> str:
        if not self.llm:
            return question
        
        context_text = "\n".join(context) if context else ""
        
        prompt = f"""请将用户的问题重写为更清晰、更完整的问题，便于检索和回答。
        
原始问题: {question}

上下文: {context_text}

重写后的问题:"""
        
        try:
            response = self.llm.Generation.call(
                model=self.llm.Generation.Models.qwen_turbo,
                prompt=prompt,
                temperature=0.3
            )
            
            if response.status_code == 200:
                return response.output.text.strip()
        except Exception:
            pass
        
        return question
    
    def expand(self, question: str) -> List[str]:
        if not self.llm:
            return [question]
        
        prompt = f"""请为以下问题生成3-5个相关的扩展问题，用于多维度检索。
        
原始问题: {question}

扩展问题（每行一个）:"""
        
        try:
            response = self.llm.Generation.call(
                model=self.llm.Generation.Models.qwen_turbo,
                prompt=prompt,
                temperature=0.5
            )
            
            if response.status_code == 200:
                lines = response.output.text.strip().split("\n")
                return [line.strip().replace("- ", "").replace("* ", "") for line in lines if line.strip()]
        except Exception:
            pass
        
        return [question]
