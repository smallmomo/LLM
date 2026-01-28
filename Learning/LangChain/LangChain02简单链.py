from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser # 导入标准输出组件
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

# 搭建链条，把model和字符串输出解析器组件连接在一起
basic_qa_chain = model | StrOutputParser()

# 查看输出结果
question = "你好，请你介绍一下你自己。"
result = basic_qa_chain.invoke(question)

print(result)
