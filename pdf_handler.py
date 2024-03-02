from langchain.text.splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from llm_chains import load_vectordb, load_embedding
import pypdfium2 as pypdf

def get_pdf_texts(pdfs_bytes):
    return [extract_text_from_pdf(pdf_bytes) for pdf_bytes in pdfs_bytes]

def extract_text_from_pdf(pdf_bytes):
    with pypdf.PdfDocument(pdf_bytes) as pdf_file:
        return "\n".join(pdf_file.get_page(page_no).get_textpage().get_text_range() for page_no in range(len(pdf_file)))
    
def get_text_chunks(texts):
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=50, separator=["\n", "\n\n"])
    return [splitter.split_text(text) for text in texts]

def get_document_chunks(text_list):
    documents = []
    for text in text_list:
        for chunk in get_text_chunks(text):
            documents.append(Document(page_content = chunk))
        return documents

def add_documents_to_db(pdfs_bytes):
    texts = get_pdf_texts(pdfs_bytes)
    documents = get_document_chunks(texts)
    vector_db = load_vectordb(load_embedding())
    vector_db.add_documents (documents)