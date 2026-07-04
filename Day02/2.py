import os
import json
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


format_instructions = """请按照以下JSON格式输出：
{
    "title": "回答的标题",
    "content": "详细的回答内容",
    "tags": "相关标签，用逗号分隔"
}"""

prompt_template = "请回答用户的问题，并按照指定格式输出。\n\n{format_instructions}\n\n用户问题: {question}"

user_input = input("请输入你的问题: ")
prompt_text = prompt_template.format(format_instructions=format_instructions, question=user_input)
llm_response = call_llm(prompt_text)

try:
    start = llm_response.find("{")
    end = llm_response.rfind("}") + 1
    response_json = llm_response[start:end]
    response = json.loads(response_json)
    
    print("\n解析后的回答:")
    print(f"标题: {response['title']}")
    print(f"内容: {response['content']}")
    print(f"标签: {response['tags']}")
except:
    print("\n原始回复:")
    print(llm_response)