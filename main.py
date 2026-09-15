import os
from dotenv import load_dotenv
from openai import OpenAI
load_dotenv()
api_key = os.getenv("DEEPSEEK_API_KEY")
Base_URL= os.getenv("BASE_URL")
model = os.getenv("MODEL_NAME")
client = OpenAI(api_key=api_key,base_url=Base_URL)
with open("input.txt", "r",encoding="utf-8") as f:
    user_input = f.read()
    prompt = f"请逐条核对以下笔记，指出错误和可改进之处"+f"\n{user_input}"
response = client.chat.completions.create(
    model=model,
    messages= [
    {"role": "system", "content": "你的名字叫测试集1号"},{"role":"user","content":prompt} 

    ])

answer = response.choices[0].message.content
with open("output.txt", "w",encoding ="utf-8") as f:
    f.write(answer)
print("完成，结果已经写入output.txt文件中")


