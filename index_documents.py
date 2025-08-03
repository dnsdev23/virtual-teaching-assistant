# 檔案：index_documents.py
# 說明：重大更新！此腳本現在會掃描 data/ 下的章節子資料夾，
#       並為每一個章節建立獨立的 ChromaDB 資料庫。

import os
import shutil
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()

ROOT_DATA_PATH = "materials/"
ROOT_DB_PATH = "chroma_db"

def create_vector_db_for_chapters():
    """
    掃描 data/ 下的所有章節資料夾，並為每個章節建立獨立的向量資料庫。
    章節資料夾內應包含 'materials' 和 'question_bank' 子資料夾。
    """
    print("開始建立章節化向量資料庫...")

    # 如果根資料庫資料夾存在，先清空以確保索引最新
    if os.path.exists(ROOT_DB_PATH):
        print(f"正在清空舊的資料庫 '{ROOT_DB_PATH}'...")
        shutil.rmtree(ROOT_DB_PATH)
    os.makedirs(ROOT_DB_PATH)

    # 取得所有章節資料夾的名稱
    try:
        chapters = [d for d in os.listdir(ROOT_DATA_PATH) if os.path.isdir(os.path.join(ROOT_DATA_PATH, d))]
    except FileNotFoundError:
        print(f"錯誤: 根資料夾 '{ROOT_DATA_PATH}' 不存在。請建立它並放入章節資料夾。")
        return

    if not chapters:
        print(f"在 '{ROOT_DATA_PATH}' 中找不到任何章節資料夾。")
        return

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    # 為每個章節建立資料庫
    for chapter in chapters:
        print(f"\n--- 正在處理章節: {chapter} ---")
        chapter_data_path = os.path.join(ROOT_DATA_PATH, chapter)
        chapter_db_path = os.path.join(ROOT_DB_PATH, chapter)

        # 檢查 'materials' 和 'question_bank' 資料夾是否存在
        materials_path = os.path.join(chapter_data_path, 'materials')
        question_bank_path = os.path.join(chapter_data_path, 'question_bank')
        
        all_documents = []
        
        if os.path.exists(materials_path):
            print(f"正在讀取 '{materials_path}'...")
            # Load PDF files
            loader_materials_pdf = DirectoryLoader(materials_path, glob='*.pdf', loader_cls=PyPDFLoader, silent_errors=True)
            all_documents.extend(loader_materials_pdf.load())
            # Load Markdown files
            loader_materials_md = DirectoryLoader(materials_path, glob='*.md', loader_cls=TextLoader, silent_errors=True)
            all_documents.extend(loader_materials_md.load())
        else:
            print(f"警告: 在 '{chapter}' 中找不到 'materials' 資料夾。")

        if os.path.exists(question_bank_path):
            print(f"正在讀取 '{question_bank_path}'...")
            # Load PDF files
            loader_qb_pdf = DirectoryLoader(question_bank_path, glob='*.pdf', loader_cls=PyPDFLoader, silent_errors=True)
            all_documents.extend(loader_qb_pdf.load())
            # Load Markdown files
            loader_qb_md = DirectoryLoader(question_bank_path, glob='*.md', loader_cls=TextLoader, silent_errors=True)
            all_documents.extend(loader_qb_md.load())
        else:
            print(f"警告: 在 '{chapter}' 中找不到 'question_bank' 資料夾。")

        if not all_documents:
            print(f"在 '{chapter}' 的子資料夾中找不到任何文件，跳過此章節。")
            continue

        # 切割文件
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        chunks = text_splitter.split_documents(all_documents)
        print(f"文件已成功切割成 {len(chunks)} 個區塊。")

        # 建立並儲存該章節的 ChromaDB
        print(f"正在為 '{chapter}' 建立向量索引...")
        vector_store = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=chapter_db_path
        )
        print(f"章節 '{chapter}' 的向量資料庫已成功建立於 '{chapter_db_path}'。")

    print("\n所有章節處理完畢！")

if __name__ == "__main__":
    create_vector_db_for_chapters()
