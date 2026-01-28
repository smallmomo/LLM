from langchain.chat_models import init_chat_model
from dotenv import load_dotenv  # 导入读取env的库
import os
# 加载.env文件中的环境变量
load_dotenv()  # 默认读取项目根目录的.env文件

model = init_chat_model(
    model=os.getenv("QWEN_MODEL"),  # 从env读取模型名
    model_provider="openai",
    base_url=os.getenv("SILICONFLOW_BASE_URL"),  # 从env读取base_url
    api_key=os.getenv("SILICONFLOW_API_KEY"),  # 从env读取api_key
)

question = "你好，请问你是"

result = model.invoke(question) #将question问题传递给model组件, 同步调用大模型生成结果

print(result)
