import re
from typing import List, Dict, Optional

class AnswerFormatter:
    def __init__(self):
        self.formats = {
            "plain": self._format_plain,
            "markdown": self._format_markdown,
            "html": self._format_html,
            "summary": self._format_summary
        }
    
    def format(self, answer: str, format_type: str = "markdown", sources: Optional[List[str]] = None) -> str:
        if format_type not in self.formats:
            format_type = "markdown"
        
        return self.formats[format_type](answer, sources)
    
    def _format_plain(self, answer: str, sources: Optional[List[str]] = None) -> str:
        result = answer
        if sources:
            result += "\n\n来源: " + ", ".join(sources)
        return result
    
    def _format_markdown(self, answer: str, sources: Optional[List[str]] = None) -> str:
        result = answer
        
        result = re.sub(r'([^\n])\n([^\n])', r'\1\n\n\2', result)
        
        result = re.sub(r'^\s*\d+\.\s', r'1.', result)
        result = re.sub(r'^(\d+)\.\s', r'\n\1.', result)
        
        if sources:
            result += "\n\n---\n\n**来源:**\n"
            for i, source in enumerate(sources, 1):
                result += f"- {source}\n"
        
        return result
    
    def _format_html(self, answer: str, sources: Optional[List[str]] = None) -> str:
        paragraphs = answer.split('\n\n')
        html_paragraphs = []
        
        for para in paragraphs:
            if para.strip():
                html_paragraphs.append(f"<p>{para.strip()}</p>")
        
        result = "\n".join(html_paragraphs)
        
        if sources:
            result += """
<div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid #eee;">
    <strong>来源:</strong>
    <ul>
"""
            for source in sources:
                result += f"        <li>{source}</li>\n"
            result += "    </ul>\n</div>"
        
        return result
    
    def _format_summary(self, answer: str, sources: Optional[List[str]] = None) -> str:
        lines = answer.split('\n')
        main_points = []
        
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                main_points.append(line)
        
        if len(main_points) > 3:
            result = "核心要点:\n"
            for i, point in enumerate(main_points[:3], 1):
                result += f"{i}. {point[:100]}...\n"
        else:
            result = answer
        
        if sources:
            result += "\n\n参考来源: " + ", ".join(sources)
        
        return result
    
    def get_available_formats(self) -> List[str]:
        return list(self.formats.keys())
