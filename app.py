import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from langchain_core.messages import SystemMessage
from langchain_core.output_parsers import StrOutputParser
import nltk

nltk.download('punkt')

st.title("🧑‍💻 RAG System on “Leave No Context Behind” Research Paper")

def initialize_models():
    chat_model = ChatGoogleGenerativeAI(google_api_key='AIzaSyAv7U2SmYx631xboBkBi3zi_Go7Kh-ijF4', model="gemini-1.5-pro-latest")
    embedding_model = GoogleGenerativeAIEmbeddings(google_api_key='AIzaSyAv7U2SmYx631xboBkBi3zi_Go7Kh-ijF4', model="models/embedding-001")
    connection = Chroma(persist_directory="chroma_db_", embedding_function=embedding_model)
    retriever = connection.as_retriever(search_kwargs={"k": 5})
    return chat_model, embedding_model, retriever

chat_model, embedding_model, retriever = initialize_models()

user_query = st.text_input("Please Enter your question")

chat_template = ChatPromptTemplate.from_messages([
    SystemMessage(content="You are a Helpful AI Bot. You take the context and question from user. Your answer should be based on the specific context."),
    HumanMessagePromptTemplate.from_template("Answer the question based on the given context.\nContext: {Context}\nQuestion: {question}\nAnswer:")
])

output_parser = StrOutputParser()

def format_docs(docs):
    formatted_content = "\n\n".join(doc.page_content.strip() for doc in docs if doc.page_content.strip())
    return formatted_content if formatted_content else "No relevant context found."

rag_chain = (
    {"Context": retriever | format_docs, "question": RunnablePassthrough()}
    | chat_template
    | chat_model
    | output_parser
)

if st.button("Result"):
    if user_query:
        response = rag_chain.invoke(user_query)
        st.write(response)
