from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

PROMPT_TEMPLATE = """
Ты ассистент, отвечающий на вопросы людей. \\
Используй написанный ниже контекст, чтобы ответить на поставленный вопрос. \\
Если ты не знаешь ответа на вопрос, просто скажи, что не знаешь. \\
Отвечай кратко, используй не более чем один абзац.
Вопрос: {question}
Контекст: {context}
Ответ:
"""

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "Answer in Russian."),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
