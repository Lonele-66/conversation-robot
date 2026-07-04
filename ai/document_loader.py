import os
from typing import List, Dict

class DocumentLoader:
    def __init__(self):
        self.supported_types = ["txt", "pdf", "docx"]
    
    def load(self, file_path: str, file_type: str = None) -> List[Dict]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_type is None:
            file_type = self._detect_file_type(file_path)
        
        if file_type not in self.supported_types:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        loaders = {
            "txt": self._load_txt,
            "pdf": self._load_pdf,
            "docx": self._load_docx
        }
        
        return loaders[file_type](file_path)
    
    def _detect_file_type(self, file_path: str) -> str:
        _, ext = os.path.splitext(file_path)
        return ext.lower().lstrip(".")
    
    def _load_txt(self, file_path: str) -> List[Dict]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()
        
        chunks = self._split_text(content)
        return [{
            "content": chunk,
            "metadata": {
                "source": file_path,
                "file_type": "txt",
                "chunk_index": i
            }
        } for i, chunk in enumerate(chunks)]
    
    def _load_pdf(self, file_path: str) -> List[Dict]:
        try:
            from PyPDF2 import PdfReader
        except ImportError:
            raise ImportError("Please install pypdf: pip install pypdf")
        
        reader = PdfReader(file_path)
        content = ""
        
        for page in reader.pages:
            text = page.extract_text()
            if text:
                content += text + "\n\n"
        
        chunks = self._split_text(content)
        return [{
            "content": chunk,
            "metadata": {
                "source": file_path,
                "file_type": "pdf",
                "chunk_index": i
            }
        } for i, chunk in enumerate(chunks)]
    
    def _load_docx(self, file_path: str) -> List[Dict]:
        try:
            from docx import Document
        except ImportError:
            raise ImportError("Please install python-docx: pip install python-docx")
        
        doc = Document(file_path)
        content = ""
        
        for para in doc.paragraphs:
            content += para.text + "\n\n"
        
        chunks = self._split_text(content)
        return [{
            "content": chunk,
            "metadata": {
                "source": file_path,
                "file_type": "docx",
                "chunk_index": i
            }
        } for i, chunk in enumerate(chunks)]
    
    def _split_text(self, text: str, chunk_size: int = 500, chunk_overlap: int = 50) -> List[str]:
        chunks = []
        start = 0
        text_len = len(text)
        
        while start < text_len:
            end = start + chunk_size
            if end < text_len:
                last_period = text.rfind(".", start, end)
                last_newline = text.rfind("\n", start, end)
                split_pos = max(last_period, last_newline)
                if split_pos > start + chunk_overlap:
                    end = split_pos + 1
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            start = end - chunk_overlap
        
        return chunks