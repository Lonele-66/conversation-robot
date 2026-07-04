import os
import json
from dotenv import load_dotenv
import dashscope

load_dotenv()

api_key = os.getenv("API_KEY")
dashscope.api_key = api_key


def call_llm(messages):
    conversation = ""
    for msg in messages:
        if msg["role"] == "system":
            conversation += f"系统: {msg['content']}\n"
        elif msg["role"] == "user":
            conversation += f"用户: {msg['content']}\n"
        else:
            conversation += f"助手: {msg['content']}\n"
    conversation += "助手:"
    
    response = dashscope.Generation.call(
        model=dashscope.Generation.Models.qwen_turbo,
        prompt=conversation,
        temperature=0
    )
    if response.status_code == 200:
        return response.output.text.strip()
    else:
        raise Exception(f"API调用失败: {response.message}")


def weather(city):
    weather_data = {
        "北京": "晴，温度25-32°C",
        "上海": "多云，温度28-35°C",
        "广州": "雷阵雨，温度26-30°C",
        "深圳": "阴，温度27-33°C",
        "成都": "小雨，温度20-25°C",
    }
    return weather_data.get(city, f"未查询到{city}的天气信息")


def calculator(expression):
    try:
        result = eval(expression)
        return f"计算结果: {result}"
    except Exception as e:
        return f"计算错误: {str(e)}"


tools = [
    {
        "name": "weather",
        "description": "查询指定城市的天气情况，输入城市名称",
        "function": weather
    },
    {
        "name": "calculator",
        "description": "执行数学计算，输入格式为数学表达式，如 '2 + 3 * 4'",
        "function": calculator
    }
]

tool_description = "\n".join([f"- {tool['name']}: {tool['description']}" for tool in tools])

system_prompt = f"""你是一个智能助手，可以使用以下工具：
{tool_description}

如果需要使用工具，请按照以下格式输出：
调用工具：工具名称(参数)

例如：调用工具：weather(北京)

如果不需要使用工具，可以直接回答用户的问题。"""

messages = [{"role": "system", "content": system_prompt}]

print("工具调用演示！输入 'exit' 退出。")
while True:
    user_input = input("\n你: ")
    if user_input.lower() == "exit":
        print("再见！")
        break

    messages.append({"role": "user", "content": user_input})
    response = call_llm(messages)
    print(f"AI思考: {response}")

    if "调用工具" in response:
        try:
            start = response.find("调用工具：") + 5
            tool_call = response[start:].strip()
            tool_name = tool_call[:tool_call.find("(")]
            param = tool_call[tool_call.find("(")+1:tool_call.find(")")]

            for tool in tools:
                if tool["name"] == tool_name:
                    tool_result = tool["function"](param)
                    print(f"工具返回: {tool_result}")
                    messages.append({"role": "assistant", "content": response})
                    messages.append({"role": "user", "content": f"工具返回结果: {tool_result}"})
                    final_response = call_llm(messages)
                    print(f"AI最终回答: {final_response}")
                    messages.append({"role": "assistant", "content": final_response})
                    break
        except Exception as e:
            print(f"工具调用错误: {str(e)}")
            messages.append({"role": "assistant", "content": response})
    else:
        messages.append({"role": "assistant", "content": response})