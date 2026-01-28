from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import init_chat_model
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

parser = StrOutputParser()

prompt = ChatPromptTemplate.from_messages([
    SystemMessage(content="你叫杨紫，是著名女演员。"),
    MessagesPlaceholder(variable_name="messages"),
])

chain = prompt | model | parser

messages_list = []  # 初始化历史
print("🔹 输入 exit 结束对话")
while True:
    user_query = input("你：")
    if user_query.lower() in {"exit", "quit"}:
        break

    # 1) 追加用户消息
    messages_list.append(HumanMessage(content=user_query))

    # 2) 调用模型
    # assistant_reply = chain.invoke({"messages": messages_list})
    # print("杨紫：", assistant_reply)

    # 2) 调用模型 流式
    assistant_reply = ''
    print('杨紫:', end=' ')
    for chunk in chain.stream({"messages": messages_list}):
        assistant_reply += chunk
        print(chunk, end="", flush=True)
    print()


    # 3) 追加 AI 回复
    messages_list.append(AIMessage(content=assistant_reply))

    # 4) 仅保留最近 50 条
    messages_list = messages_list[-50:]
