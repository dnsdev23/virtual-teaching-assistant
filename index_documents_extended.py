# 檔案：index_documents_extended.py
# 說明：擴展版的文件索引腳本，支援 PDF 和 Markdown 檔案

import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

DATA_PATH = "data/"
DB_PATH = "chroma_db"

def create_vector_db():
    """從 PDF 和 Markdown 文件建立向量資料庫。"""
    print("開始建立向量資料庫...")
    
    all_documents = []
    
    # 載入 PDF 檔案
    pdf_loader = DirectoryLoader(DATA_PATH, glob='*.pdf', loader_cls=PyPDFLoader)
    pdf_documents = pdf_loader.load()
    if pdf_documents:
        print(f"找到 {len(pdf_documents)} 個 PDF 文件")
        all_documents.extend(pdf_documents)
    else:
        print("未找到 PDF 文件")
    
    # 載入 Markdown 檔案
    md_loader = DirectoryLoader(DATA_PATH, glob='*.md', loader_cls=TextLoader)
    try:
        md_documents = md_loader.load()
        if md_documents:
            print(f"找到 {len(md_documents)} 個 Markdown 文件")
            all_documents.extend(md_documents)
        else:
            print("未找到 Markdown 文件")
    except Exception as e:
        print(f"載入 Markdown 檔案時發生錯誤: {e}")

    if not all_documents:
        print(f"在 '{DATA_PATH}' 資料夾中找不到任何文件。")
        return

    print(f"總共載入 {len(all_documents)} 個文件")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_documents(all_documents)
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
