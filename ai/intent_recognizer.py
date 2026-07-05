import os
import json
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class IntentRecognizer:
    def __init__(self):
        self.intents = [
            {
                "name": "question",
                "description": "用户提问，需要基于文档内容回答",
                "keywords": ["什么", "怎么", "如何", "为什么", "多少", "谁", "哪个", "哪里", "何时", "是否"]
            },
            {
                "name": "chat",
                "description": "闲聊对话，不需要参考文档",
                "keywords": ["你好", "嗨", "在吗", "聊聊天", "说说", "谈谈"]
            },
            {
                "name": "upload",
                "description": "上传文档",
                "keywords": ["上传", "加载", "导入", "文件"]
            },
            {
                "name": "summarize",
                "description": "总结文档内容",
                "keywords": ["总结", "概述", "概括", "摘要"]
            },
            {
                "name": "search",
                "description": "搜索文档内容",
                "keywords": ["搜索", "查找", "找一下"]
            },
            {
                "name": "unknown",
                "description": "无法识别的意图",
                "keywords": []
            }
        ]
    
    def recognize(self, text: str) -> Dict:
        scores = []
        
        for intent in self.intents:
            if intent["name"] == "unknown":
                continue
            
            score = 0
            for keyword in intent["keywords"]:
                if keyword in text:
                    score += 1
            
            scores.append((intent["name"], score, intent["description"]))
        
        scores.sort(key=lambda x: x[1], reverse=True)
        
        if scores[0][1] > 0:
            return {
                "intent": scores[0][0],
                "score": scores[0][1],
                "description": scores[0][2]
            }
        
        return {
            "intent": "unknown",
            "score": 0,
            "description": "无法识别的意图"
        }
    
    def get_intents(self) -> List[Dict]:
        return self.intents
