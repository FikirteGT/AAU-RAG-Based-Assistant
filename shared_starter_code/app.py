import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

# # 1. Add this import at the top
# from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()


# # ... after your app = FastAPI() line ...

# # 2. Add these lines to allow the UI to connect
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# ---------- Vector Database Setup ----------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = None


def load_and_process_docs():
    docs = []
    folder = "../docs"

    if not os.path.exists(folder):
        print(f"⚠️ Warning: Folder '{folder}' not found.")
        return []

    for file in os.listdir(folder):
        path = os.path.join(folder, file)
        try:
            if file.endswith(".pdf"):
                loader = PyPDFLoader(path)
                docs.extend(loader.load())
            elif file.endswith(".txt"):
                loader = TextLoader(path)
                docs.extend(loader.load())
        except Exception as e:
            print(f"❌ Failed to load {file}: {e}")
    return docs


@app.on_event("startup")
def startup_event():
    global vectorstore
    print("🔄 Initializing Vector Store...")
    documents = load_and_process_docs()

    if documents:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=700,
            chunk_overlap=100)
        chunks = splitter.split_documents(documents)
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory="./chroma_db"
        )
        print("✅ Vector store initialized successfully.")
    else:
        print("⚠️ No documents found. Ensure your 'docs' folder has files.")


# ---------- Updated LLM ----------
llm = ChatGroq(
    model_name="llama-3.1-8b-instant",  # <--- Fixed Model Name
    temperature=0
)


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask_question(q: Question):
    if vectorstore is None:
        raise HTTPException(
            status_code=503, detail="Vector store not initialized.")

    try:
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        docs = retriever.invoke(q.question)  # <--- Fixed invoke method

        context = "\n\n".join([doc.page_content for doc in docs])

        prompt = f"""
You are an assistant for Addis Ababa University.
Answer the question ONLY using the provided context.

If the answer is not in the context:
say "I could not find the answer in the provided documents."

Context:
{context}

Question:
{q.question}"""

        response = llm.invoke(prompt)
        sources = list(
            set([os.path.basename(doc.metadata.get("source", "unknown")) for doc in docs]))

        return {"answer": response.content, "sources": sources}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
