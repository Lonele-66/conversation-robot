import os
from dotenv import load_dotenv
import dashscope

load_dotenv()

api_key = os.getenv("API_KEY")
dashscope.api_key = api_key


def call_llm(prompt):
    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_turbo,
        prompt=prompt,
        temperature=0.7
    )
    if response.status_code == 200:
        return response.output.text
    else:
        raise Exception(f"API调用失败: {response.message}")


user_input = input("请输入你的问题: ")
response = call_llm(user_input)
print(f"\n大模型回复: {response}")