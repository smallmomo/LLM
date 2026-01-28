from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os

# 加载 .env
load_dotenv()

# ========== 第一步：生成新闻正文 ==========
news_gen_prompt = PromptTemplate.from_template(
    "请根据以下新闻标题撰写一段简短的新闻内容（100字以内）：\n\n标题：{title}"
)

model = init_chat_model(
    model=os.getenv("QWEN_MODEL"),
    model_provider="openai",
    base_url=os.getenv("SILICONFLOW_BASE_URL"),
    api_key=os.getenv("SILICONFLOW_API_KEY"),
)

news_chain = news_gen_prompt | model

# ========== 第二步：结构化提取 ==========
class NewsSummary(BaseModel):
    time: str = Field(description="事件发生的时间")
    location: str = Field(description="事件发生的地点")
    event: str = Field(description="发生的具体事件")

# 让模型直接输出结构化结果
structured_model = model.with_structured_output(NewsSummary)

summary_prompt = PromptTemplate.from_template(
    "请从下面这段新闻内容中提取关键信息：\n\n{news}"
)

summary_chain = summary_prompt | structured_model

# ========== 组合 Chain ==========
full_chain = news_chain | summary_chain

# 调用
result = full_chain.invoke({"title": "苹果公司在加州发布新款AI芯片"})

print(result)
print(type(result))  # NewsSummary
