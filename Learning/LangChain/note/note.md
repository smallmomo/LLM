

# 1、 ChatPromptTemplate 和 PromptTemplate 的区别

`ChatPromptTemplate` 和 `PromptTemplate` 都是 **LangChain** 里用来“构造 Prompt（提示词）”的核心类，但**使用场景和抽象层级不同**。可以把它们理解成：

> **PromptTemplate = 给「普通文本模型 / 单条文本输入」用的模板**
> **ChatPromptTemplate = 给「聊天模型 / 多角色消息」用的模板**

下面我从 **定位、结构、用法、适用场景** 四个维度给你一次性讲清楚。

---

## 一、核心区别一览（先给结论）

| 对比项     | PromptTemplate          | ChatPromptTemplate                  |
| ------- | ----------------------- | ----------------------------------- |
| 适用模型    | LLM（text-in → text-out） | ChatModel（message-in → message-out） |
| 输出结果    | `String`                | `List[BaseMessage]`                 |
| 是否支持角色  | ❌ 不支持                   | ✅ 支持 system / human / ai            |
| 抽象层级    | 低（纯字符串模板）               | 高（结构化消息模板）                          |
| 是否推荐新项目 | ⚠️ 不推荐（除非用旧 LLM）        | ✅ **推荐**                            |

---

## 二、PromptTemplate：字符串级 Prompt

### 1️⃣ 定位

`PromptTemplate` 本质就是一个 **字符串格式化工具**：

* 最终产物：**一段 String**
* 不关心 system / user / assistant
* 适合 **老式 Completion 模型** 或你手动拼 Prompt

---

### 2️⃣ 示例

```python
from langchain.prompts import PromptTemplate

prompt = PromptTemplate(
    template="请用{language}解释什么是{topic}",
    input_variables=["language", "topic"]
)

result = prompt.format(
    language="中文",
    topic="Java 的 volatile 关键字"
)

print(result)
```

输出：

```
请用中文解释什么是 Java 的 volatile 关键字
```

---

### 3️⃣ 特点总结

✅ 简单
❌ 没有角色概念
❌ 不符合 ChatGPT / GPT-4 / GPT-4o 等模型的输入结构
❌ system prompt 只能“硬编码进字符串”

---

## 三、ChatPromptTemplate：消息级 Prompt（主流）

### 1️⃣ 定位

`ChatPromptTemplate` 是为 **Chat Model（如 ChatOpenAI）设计的**：

* Prompt = **一组有角色的消息**
* 天然支持 system / human / ai
* 与 OpenAI Chat API 的 message 结构 **完全一致**

---

### 2️⃣ 示例（标准用法）

```python
from langchain.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个精通 JVM 的 Java 架构师"),
    ("human", "请用{language}解释 {topic}")
])

messages = prompt.format_messages(
    language="中文",
    topic="volatile 关键字"
)

print(messages)
```

输出是 **消息对象列表**：

```
[
  SystemMessage("你是一个精通 JVM 的 Java 架构师"),
  HumanMessage("请用中文解释 volatile 关键字")
]
```

---

### 3️⃣ 直接对接 ChatModel

```python
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI()
response = llm(messages)
```

⚠️ **注意**：ChatModel 接收的是 `messages`，不是 String

---

## 四、为什么 LangChain 更推荐 ChatPromptTemplate？

### 1️⃣ 与现代大模型输入结构一致

OpenAI / Claude / Gemini：

```json
[
  { "role": "system", "content": "..." },
  { "role": "user", "content": "..." }
]
```

👉 `ChatPromptTemplate` 是 **一比一映射**

---

### 2️⃣ system prompt 不再“伪装成字符串”

❌ PromptTemplate（不推荐）：

```text
你是一个专家，请严格回答。
用户问题：xxx
```

✅ ChatPromptTemplate（推荐）：

```python
("system", "你是一个专家")
("human", "xxx")
```

**模型理解能力完全不同**

---

### 3️⃣ 更适合复杂 Agent / Chain / Tool 场景

* Agent
* Tool Calling
* Memory
* 多轮对话
* RAG

👉 **全部默认用 ChatPromptTemplate**

---

## 五、两者可以互相替代吗？

### ❌ 不建议反向替代

| 场景                           | 结论                      |
| ---------------------------- | ----------------------- |
| 用 ChatModel + PromptTemplate | ⚠️ 勉强可用，但丢角色            |
| 用 LLM + ChatPromptTemplate   | ❌ 不行                    |
| 新项目                          | ✅ 直接 ChatPromptTemplate |

---

## 六、什么时候还会用 PromptTemplate？

仅在以下情况👇：

1. 使用 **非 Chat 的 LLM**
2. 只需要 **拼一段字符串**
3. 维护老项目 / 老代码
4. 非对话型一次性文本生成

否则，一律用 `ChatPromptTemplate`

---

## 七、一句话总结（给你记忆用）

> **PromptTemplate = 字符串模板（老时代）**
> **ChatPromptTemplate = 结构化消息模板（Chat 时代，主流）**

---

如果你愿意，我也可以结合你现在做的 **策略模式 / 校验规则 / RAG / Agent 场景**，直接帮你设计一个 **生产级 ChatPromptTemplate 示例**（包括 system 约束 + Few-shot）。
