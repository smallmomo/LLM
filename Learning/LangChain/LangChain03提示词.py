from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
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

prompt_template = ChatPromptTemplate([
    ("system", "你是一个乐意助人的助手，请根据用户的问题给出回答"),
    ("user", "这是用户的问题： {topic}， 请用 yes 或 no 来回答")
])

# 直接使用模型 + 输出解析器
bool_qa_chain = prompt_template | model | StrOutputParser()
# 测试
question = "请问 1 + 1 是否 大于 2？"
result = bool_qa_chain.invoke({'topic':question})
print(result)
