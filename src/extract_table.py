import pdfplumber
import pandas as pd

# extract_table_from_pdf
def extract_table_from_pdf(pdf_path, bank_name):

    dfs = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            tables = page.extract_tables()
            for table in tables:
                df = pd.DataFrame(table[1:], columns=table[0])  # Assuming the first row is the header
                dfs.append(df)

    result = pd.concat(dfs[2:], axis=0, ignore_index=True)
    return result


# Load the PDF file
# pdf_document = "./sample_pdfs/sample1.pdf"  # Replace with your PDF file path
# df=pdf_to_dataframe(pdf_document)
#
# a= df["Açıklama"].tolist()
#
# print(df)
# print(a)
# #
# # List to store DataFrames
# dfs = []
#
# with pdfplumber.open(pdf_document) as pdf:
#     for i, page in enumerate(pdf.pages):
#         tables = page.extract_tables()
#         for table in tables:
#             df = pd.DataFrame(table[1:], columns=table[0])  # Assuming the first row is the header
#             dfs.append(df)


# result = pd.concat(dfs[2:], axis=0, ignore_index=True)
#
# print(result)
#
