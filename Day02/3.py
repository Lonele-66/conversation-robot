import os
import json
from dotenv import load_dotenv
import dashscope

load_dotenv()

api_key = os.getenv("API_KEY")
dashscope.api_key = api_key

MEMORY_FILE = "conversation_memory.json"
MAX_MESSAGES = 20


def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("messages", [])
        except:
            return []
    return []


def save_memory(messages):
    recent_messages = messages[-MAX_MESSAGES:]
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump({"messages": recent_messages}, f, ensure_ascii=False, indent=2)


def call_llm(messages):
    conversation = ""
    for msg in messages:
        if msg["role"] == "user":
            conversation += f"用户: {msg['content']}\n"
        else:
            conversation += f"助手: {msg['content']}\n"
    conversation += "助手:"
    
    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_turbo,
        prompt=conversation,
        temperature=0.7
    )
    if response.status_code == 200:
        return response.output.text.strip()
    else:
        raise Exception(f"API调用失败: {response.message}")


messages = load_memory()

print("欢迎来到会话记忆聊天！输入 'exit' 退出。")
while True:
    user_input = input("\n你: ")
    if user_input.lower() == "exit":
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})
    messages = messages[-MAX_MESSAGES:]

    response = call_llm(messages)
    print(f"AI: {response}")

    messages.append({"role": "assistant", "content": response})
    messages = messages[-MAX_MESSAGES:]

    save_memory(messages)
    print(f"\n已保存 {len(messages)} 条消息（最多保留 {MAX_MESSAGES} 条）")