from langchain.chat_models import init_chat_model
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import ResponseSchema, StructuredOutputParser
from dotenv import load_dotenv  # 导入读取env的库
import os
# 加载.env文件中的环境变量
load_dotenv()  # 默认读取项目根目录的.env文件
schemas = [ # 构建结构化数据模板
    ResponseSchema(name="name", description="用户的姓名"),
    ResponseSchema(name="age", description="用户的年龄")
]

parser = StructuredOutputParser.from_response_schemas(schemas) # 根据模板生成解析器


model = init_chat_model(
    model=os.getenv("QWEN_MODEL"),  # 从env读取模型名
    model_provider="openai",
    base_url=os.getenv("SILICONFLOW_BASE_URL"),  # 从env读取base_url
    api_key=os.getenv("SILICONFLOW_API_KEY"),  # 从env读取api_key
)

prompt = PromptTemplate.from_template(
    "请根据以下内容提取用户信息，并返回 JSON 格式：\n{input}\n\n{format_instructions}"
) # 这是另一种使用占位符的提示词模板表示方式

chain = (
    prompt.partial(format_instructions=parser.get_format_instructions())
    | model
    | parser
)

result = chain.invoke({"input": "用户叫李雷，今年25岁，是一名工程师。"}) # 输入input, format_instructions前面已经赋值
print(result)
