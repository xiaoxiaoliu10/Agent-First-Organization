import pickle
from typing import List

from langchain_community.document_loaders import SeleniumURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


class DocumentLoader:
    def __init__(self):
        pass

    @staticmethod
    def save_object(obj: List[Document], filename="../data/documents.pkl"):
        with open(filename, 'wb') as f:  # Overwrites any existing file.
            pickle.dump(obj, f)

    @staticmethod
    def load_url(url):
        # load website
        loader = SeleniumURLLoader([url])
        documents = loader.load()
        content = documents[0].page_content
        # chunk data
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(encoding_name="cl100k_base", chunk_size=400, chunk_overlap=50)
        splitted_text = text_splitter.split_text(content)
        # create document
        doc_collection = []
        for txt in splitted_text:
            doc = Document(page_content=txt, metadata={"source": url})
            doc_collection.append(doc)
        print(doc_collection)
        DocumentLoader.save_object(doc_collection)

        return
    
loader = DocumentLoader()
loader.load_url("https://www.richtechrobotics.com")
