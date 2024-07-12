
import camelot
import pandas as pd

# Load the PDF file
pdf_document = "./sample_pdfs/sample1.pdf"  # Replace with your PDF file path

# Extract tables from each page
tables = camelot.read_pdf(pdf_document, pages='all')

dfs = []

# Extract tables and convert them to DataFrames
for table in tables:
    dfs.append(table.df)

# Now `dfs` is a list of DataFrames, where each DataFrame represents a table from the PDF

# Example: Display the first table
print(dfs[0])




# # Save tables to separate CSV files
# for i, table in enumerate(tables):
#     table.to_csv(f"table_page_{i+1}.csv")
#
# # Optionally, save all tables into one Excel file with separate sheets
# with pd.ExcelWriter("extracted_tables.xlsx") as writer:
#     for i, table in enumerate(tables):
#         table.df.to_excel(writer, sheet_name=f"Page_{i+1}", index=False)
#
# print("Tables extracted and saved successfully.")
#






# import tiktoken
# from typing import List, Dict
# from abc import ABC, abstractmethod
# from langchain_community.document_loaders import PyPDFLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_community.vectorstores.chroma import Chroma
# from langchain_openai import ChatOpenAI
# from langchain.prompts import ChatPromptTemplate
# from langchain_core.messages.human import HumanMessage
# from langchain_core.messages.system import SystemMessage
# from langchain_community.llms import Ollama
# from langchain_openai import OpenAIEmbeddings
# import json
# from askgpt import askgpt, askllama
# from langchain.schema import Document
#
#
# class PDFProcessor:
#     def __init__(self, pdf_loader: PyPDFLoader):
#         self.pdf_loader = pdf_loader
#
#     def load_pdf(self) -> List[Document]:
#         return self.pdf_loader.load()
#
#     def split_text(self, documents: List[Document]) -> List[Document]:
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=750,
#             chunk_overlap=100,
#             length_function=len,
#             add_start_index=True,
#         )
#         return text_splitter.split_documents(documents)
#
#     def split_text_with_prefix(self, documents: List[Document], prefix: str) -> List[Document]:
#         text_splitter = RecursiveCharacterTextSplitter(
#             chunk_size=750,
#             chunk_overlap=100,
#             length_function=len,
#             add_start_index=True,
#         )
#         chunks = text_splitter.split_documents(documents)
#         for chunk in chunks:
#             chunk.page_content = prefix + '\n' + chunk.page_content
#         return chunks