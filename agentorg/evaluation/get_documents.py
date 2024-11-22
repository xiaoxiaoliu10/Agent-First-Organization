import os
import sys
import json
import pickle
from pathlib import Path
from os.path import dirname, abspath

sys.path.insert(0, dirname(dirname(abspath(__file__))))
from utils.loader import Loader

def get_domain_info(documents):
    summary = None
    for doc in documents:
        if doc['URL'] == 'summary':
            summary = doc['content']
            break
    return summary

def load_docs(document_dir, doc_config, limit=10):
        if document_dir is not None:
            filepath = os.path.join(document_dir, "documents.pkl")
            source = doc_config['docs']['source']
            num_docs = doc_config['docs']['num']
            loader = Loader()
            if Path(filepath).exists():
                crawled_urls = pickle.load(open(os.path.join(document_dir, "documents.pkl"), "rb"))
            else:
                urls = loader.get_all_urls(source, num_docs)
                crawled_urls = loader.to_crawled_obj(urls)
                Loader.save(filepath, crawled_urls)
            documents = loader.get_candidates_websites(crawled_urls, limit)
        else:
            documents = ""
        return documents

if __name__ == "__main__":
    doc_config = json.load(open('./temp_files/richtech_config.json'))
    docs = load_docs('./temp_files', doc_config, 10)