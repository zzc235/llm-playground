import os
import logging
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

# 1. 加载环境变量
load_dotenv()

# 2. 获取日志记录器 (不要用 print，用 logging)
logger = logging.getLogger(__name__)

# 3. 初始化 OpenAI 客户端
# 注意：这里把 Base_URL 改成了 base_url (PEP 8规范，对应你图里的尾巴2)
api_key = os.getenv("DEEPSEEK_API_KEY")
base_url = os.getenv("BASE_URL")
model_name = os.getenv("MODEL_NAME", "deepseek-chat") # 给个默认值，防止取不到

if not api_key:
    logger.error("未找到 DEEPSEEK_API_KEY，请检查 .env 文件！")

client = OpenAI(api_key=api_key, base_url=base_url)

# 4. 重试装饰器 (对应你图里的要求3：重试封装成装饰器)
# 这里的参数意思是：最多重试3次，每次等待时间翻倍（1秒、2秒、4秒），最大不超过10秒
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=10),
    reraise=True # 重试3次都失败后，把错误抛出去，不要吞掉
)
def call_llm(user_input: str, system_prompt: str = "你是一个专业的AI助手。") -> str:
    """
    核心通用接口：负责与 LLM 交互并返回文本结果。
    """
    logger.info("开始请求 LLM API...")
    
    prompt = f"(请逐条核对以下笔记，指出错误和可改进之处)\n\n{user_input}"
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        
        # 5. 处理 None 值 (对应你图里的尾巴3：response.choices[0].message.content 可能是 None)
        answer = response.choices[0].message.content
        
        if answer is None:
            logger.warning("LLM 返回了空内容 (None)")
            return "AI没有返回有效内容。"
            
        logger.info("LLM API 请求成功！")
        return answer

    except Exception as e:
        # 如果发生异常，日志记录一下，然后抛出去让装饰器捕获并重试
        logger.error(f"请求 LLM API 失败: {e}")
        raise e