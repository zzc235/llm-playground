import os
from dotenv import load_dotenv
import os
import logging
import argparse
from dotenv import load_dotenv
from llm_client import call_llm  # 导入刚才写的函数

# 1. 初始化日志 (解决图里的第4题)
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

load_dotenv()

def main():
    # 读取输入
     # 设置命令行参数解析
    parser = argparse.ArgumentParser(description="自动化剧本处理工具")
    parser.add_argument("--input", default="input.txt", help="输入文件路径 (默认: input.txt)")
    parser.add_argument("--output", default="output.txt", help="输出文件路径 (默认: output.txt)")
    args = parser.parse_args() # 解析参数

    logging.info(f"开始处理，输入文件: {args.input}，输出文件: {args.output}")

    # 读取输入 (改成使用传入的参数)
    with open(args.input, "r", encoding="utf-8") as f:
        user_input = f.read()

    # 调用 LLM
    answer = call_llm(user_input)

    # 写入输出 (改成使用传入的参数)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(answer)
        
    logging.info(f"完成，结果已经写入 {args.output} 文件中")
if __name__ == "__main__":
    main()