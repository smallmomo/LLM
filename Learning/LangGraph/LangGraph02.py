from langchain.agents import create_agent
from langchain_community.chat_models import ChatTongyi
from langchain_core.tools import tool
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

@tool
def add(a: float, b: float) -> float:
    """两数相加"""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """两数相乘"""
    return a * b

# 创建模型
llm = ChatTongyi(model="qwen-plus", temperature=0.7)

# 创建 ReAct Agent
agent = create_agent(
    model=llm,
    tools=[add, multiply],
    system_prompt= "你是一个数学计算助手。")


# 使用
result = agent.invoke({
    "messages": [{"role": "user", "content": "计算 (10 + 5) × 3"}]
})
print(result["messages"][-1].content)