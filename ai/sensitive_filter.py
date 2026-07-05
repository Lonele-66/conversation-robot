import os
import json
from typing import List, Dict, Tuple

class SensitiveFilter:
    def __init__(self):
        self.sensitive_words = []
        self._load_sensitive_words()
    
    def _load_sensitive_words(self):
        words_file = os.path.join(os.path.dirname(__file__), "../data/sensitive_words.json")
        if os.path.exists(words_file):
            with open(words_file, "r", encoding="utf-8") as f:
                self.sensitive_words = json.load(f)
        else:
            self.sensitive_words = [
                "色情", "暴力", "赌博", "毒品", "政治",
                "恐怖", "邪教", "反动", "违法", "犯罪",
                "辱骂", "歧视", "仇恨", "造谣", "诈骗"
            ]
            self._save_sensitive_words()
    
    def _save_sensitive_words(self):
        data_dir = os.path.join(os.path.dirname(__file__), "../data")
        os.makedirs(data_dir, exist_ok=True)
        words_file = os.path.join(data_dir, "sensitive_words.json")
        with open(words_file, "w", encoding="utf-8") as f:
            json.dump(self.sensitive_words, f, ensure_ascii=False, indent=2)
    
    def add_sensitive_word(self, word: str):
        if word not in self.sensitive_words:
            self.sensitive_words.append(word)
            self._save_sensitive_words()
    
    def remove_sensitive_word(self, word: str):
        if word in self.sensitive_words:
            self.sensitive_words.remove(word)
            self._save_sensitive_words()
    
    def check(self, text: str) -> Tuple[bool, List[str]]:
        found_words = []
        for word in self.sensitive_words:
            if word in text:
                found_words.append(word)
        return len(found_words) > 0, found_words
    
    def filter(self, text: str) -> str:
        for word in self.sensitive_words:
            text = text.replace(word, "*" * len(word))
        return text
    
    def get_all_words(self) -> List[str]:
        return self.sensitive_words
