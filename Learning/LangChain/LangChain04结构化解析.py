from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# 加载 .env
load_dotenv()

# 1️⃣ 用 Pydantic 定义结构化输出
class UserInfo(BaseModel):
    name: str = Field(description="用户的姓名")
    age: int = Field(description="用户的年龄")

# 2️⃣ 初始化模型
model = init_chat_model(
    model=os.getenv("QWEN_MODEL"),
    model_provider="openai",
    base_url=os.getenv("SILICONFLOW_BASE_URL"),
    api_key=os.getenv("SILICONFLOW_API_KEY"),
)

# 3️⃣ 让模型“天生”输出结构化数据
structured_model = model.with_structured_output(UserInfo)

# 4️⃣ Prompt（不再需要 format_instructions）
prompt = PromptTemplate.from_template(
    "请根据以下内容提取用户信息：\n{input}"
)

# 5️⃣ LCEL Chain
chain = prompt | structured_model

# 6️⃣ 调用
result = chain.invoke({"input": "用户叫李雷，今年25岁，是一名工程师。"})

print(result)
print(type(result))  # <class '__main__.UserInfo'>
