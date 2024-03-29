from langchain.vectorstores.pinecone import Pinecone
from pinecone_index import get_index
from langchain.agents import Tool
from embedding_model import get_embedding_model
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


vectordb = Pinecone(index=get_index('index1'),embedding=get_embedding_model().embed_query, text_key="text")

prompt = PromptTemplate.from_template(template="use this tool only for fetching data on brightspeed")

def get_vectordb_tool():

    tool = Tool(
        func = vectordb.similarity_search,
        name="brightspeed data",
        description="contains info related to brightspeed. Use this tool only when the questions are related to Brightspeed",
        retriever_top_k=3
    )

    return tool
