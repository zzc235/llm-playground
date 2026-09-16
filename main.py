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
    {"role": "system", "content": "你将担任一名老练的油气工程师，你的任务是核对我发送给你的笔记中的内容 要求1:不得覆盖原内容 要求2:对于存疑内容标记 ***等待人工查验 要求3:输出格式为原始内容+换行后的修改内容括号包起来+待查验"},{"role":"user","content":prompt} 

    ])

answer = response.choices[0].message.content
with open("output.txt", "w",encoding ="utf-8") as f:
    f.write(answer)
print("完成，结果已经写入output.txt文件中")


