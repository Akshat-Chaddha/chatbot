from langgraph.graph import StateGraph, START ,END
from typing import TypedDict ,Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_huggingface import ChatHuggingFace , HuggingFaceEndpoint
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os
from langgraph.checkpoint.memory import MemorySaver , InMemorySaver

load_dotenv()
token = os.getenv("HF_API_KEY")


class chat_state(TypedDict):
    messages : Annotated[list[BaseMessage],add_messages]

llm = HuggingFaceEndpoint(
    repo_id ="meta-llama/Llama-3.1-8B-Instruct",
    huggingfacehub_api_token=token,
    task = "text-generation",
)

llm = ChatHuggingFace(llm=llm)

def chat_node(state :chat_state):

    messages = state['messages']

    response = llm.invoke(messages)

    return{"messages": [response]}

checkpointer = InMemorySaver()
graph = StateGraph(chat_state)

graph.add_node('chat_node' , chat_node)
graph.add_edge(START , 'chat_node')
graph.add_edge('chat_node' , END)

chatbot = graph.compile(checkpointer=checkpointer)

def _chunk_text(chunk):
    content = getattr(chunk, 'content', chunk)
    if isinstance(content, list):
        return ''.join(
            block.get('text', '') if isinstance(block, dict) else str(block)
            for block in content
        )
    return str(content)


def stream_chat(messages: list[HumanMessage], config=None):
    for chunk in llm.stream(messages, config=config, stream=True):
        yield _chunk_text(chunk)
