from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
)

response = llm.invoke([
    HumanMessage(content="Reply with exactly: Groq connection successful")
])

print(response.content)