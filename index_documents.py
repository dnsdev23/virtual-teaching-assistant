# 檔案：index_documents.py
# 說明：一個獨立的腳本，用來讀取 PDF 文件並建立知識庫索引。

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

DATA_PATH = "data/"
DB_PATH = "chroma_db"

def create_vector_db():
    """從 PDF 文件建立向量資料庫。"""
    print("開始建立向量資料庫...")
    
    loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    documents = loader.load()

    if not documents:
        print(f"在 '{DATA_PATH}' 資料夾中找不到 PDF 文件。")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(documents)
    print(f"文件已成功切割成 {len(chunks)} 個區塊。")

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    print("正在將文件區塊嵌入並儲存到 ChromaDB...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=DB_PATH
    )
    print(f"向量資料庫已成功建立並儲存在 '{DB_PATH}'。")

if __name__ == "__main__":
    create_vector_db()
