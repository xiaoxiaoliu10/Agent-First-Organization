import logging
import time
from pathlib import Path
from typing import List
import requests
import pickle
import uuid
import argparse
import os

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import networkx as nx
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


# Configure logging
logging.basicConfig(
    level=logging.INFO,  
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

CHROME_DRIVER_VERSION = "125.0.6422.7"

class URLObject:
    def __init__(self, id: str, url: str):
        self.id = id
        self.url = url
        
class LocalObject:
    def __init__(self, id: str, location: str):
        self.id = id
        self.location = location
        
class CrawledObject():
    def __init__(
        self,
        id: str,
        location: str,
        content: str,
        metadata={},
        is_chunk=False,
        is_error=False,
        error_message=None,
    ):
        self.id = id
        self.location = location
        self.content = content
        self.metadata = metadata
        self.is_chunk = is_chunk
        self.is_error = is_error
        self.error_message = error_message
        
class CrawledURLObject(CrawledObject):
    def __init__(
        self,
        id: str,
        url: str,
        content: str,
        metadata={},
        is_chunk=False,
        is_error=False,
        error_message=None,
    ):
        super().__init__(id, url, content, metadata, is_chunk, is_error, error_message)
        self.url = url
        
class CrawledLocalObject(CrawledObject):
    def __init__(
        self,
        id: str,
        location: str,
        content: str,
        metadata={},
        is_chunk=False,
        is_error=False,
        error_message=None,
    ):
        super().__init__(id, location, content, metadata, is_chunk, is_error, error_message)

class Loader:
    def __init__(self):
        pass

    def to_crawled_url_objs(self, url_list: List[str]) -> List[CrawledURLObject]:    
        url_objs = [URLObject(str(uuid.uuid4()), url) for url in url_list]
        crawled_url_objs = self.crawl_urls(url_objs)
        return crawled_url_objs

    def crawl_urls(self, url_objects: list[URLObject]) -> List[CrawledURLObject]:
        logger.info(f"Start crawling {len(url_objects)} urls")
        options = webdriver.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-infobars")
        options.add_argument("--remote-debugging-pipe")
        chrome_driver_path = Path(ChromeDriverManager(driver_version=CHROME_DRIVER_VERSION).install())
        options.binary_location = str(chrome_driver_path.parent.absolute())
        logger.info(f"chrome binary location: {options.binary_location}")
        driver = webdriver.Chrome(options=options)

        docs: List[CrawledURLObject] = []
        for url_obj in url_objects:
            try:
                logger.info(f"loading url: {url_obj.url}")
                driver.get(url_obj.url)
                time.sleep(2)
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                text_list = []
                for string in soup.strings:        
                    if string.find_parent("a"):
                        href = urljoin(url_obj.url, string.find_parent("a").get("href"))
                        if href.startswith(url_obj.url):
                            text = f"{string} {href}"
                            text_list.append(text)
                    elif string.strip():
                        text_list.append(string)
                text_output = "\n".join(text_list)
                
                title = url_obj.url
                for title in soup.find_all("title"):
                    title = title.get_text()
                    break

                docs.append(
                    CrawledURLObject(
                        id=url_obj.id,
                        url=url_obj.url,
                        content=text_output,
                        metadata={"title": title, "source": url_obj.url},
                    )
                )

            except Exception as err:
                logger.info(f"error crawling {url_obj}")
                logger.error(err)
                docs.append(
                    CrawledURLObject(
                        id=url_obj.id,
                        url=url_obj.url,
                        content=None,
                        metadata={"title": url_obj.url, "source": url_obj.url},
                        is_error=True,
                        error_message=str(err),
                    )
                )
        driver.quit()
        return docs

    def get_all_urls(self, base_url: str, max_num: int) -> List[str]:
        logger.info(f"Getting all pages for base url: {base_url}, maximum number is: {max_num}")
        urls_visited = []
        base_url = base_url.split("#")[0].rstrip("/")
        urls_to_visit = [base_url]
        
        while urls_to_visit:
            if len(urls_visited) >= max_num:
                break
            current_url = urls_to_visit.pop(0)
            if current_url not in urls_visited:
                urls_visited.append(current_url)
                new_urls = self.get_outsource_urls(current_url, base_url)
                urls_to_visit.extend(new_urls)
                urls_to_visit = list(set(urls_to_visit))
        logger.info(f"URLs visited: {urls_visited}")
        return sorted(urls_visited[:max_num])
    
    def get_outsource_urls(self, curr_url: str, base_url: str):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15'
        } 
        new_urls = list()
        try:
            response = requests.get(curr_url, headers=headers, timeout=10)
            # Check if the request was successful
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all("a"):
                    try:
                        full_url = urljoin(curr_url, link.get("href"))
                        full_url = full_url.split("#")[0].rstrip("/")
                        if self._check_url(full_url, base_url):
                            new_urls.append(full_url)
                    except Exception as err:
                        logger.error(f"Fail to process sub-url {link.get('href')}: {err}")
            else:
                logger.error(f"Failed to retrieve page {curr_url}, status code: {response.status_code}")
        except Exception as err:
            logger.error(f"Fail to get the page from {curr_url}: {err}")
        return list(set(new_urls))
    
    def _check_url(self, full_url, base_url):
        kw_list = ['.pdf', '.jpg', '.png', '.docx', '.xlsx', '.pptx', '.zip', ".jpeg"]
        if full_url.startswith(base_url) and full_url and not any(kw in full_url for kw in kw_list) and full_url != base_url:
            return True
        return False

    def get_candidates_websites(self, urls: List[CrawledURLObject], top_k: int) -> List[str]:
        """Based on the pagerank algorithm of the crawled websites, return the top 10 websites. 
        The reason why we can do that is because we have the hreqs of the including <a> tags in the content of the website.
        So we can use that to construct the edges and then use the tool from networkx to get the pagerank of the websites.
        """
        
        nodes = []
        edges = []
        url_to_id_mapping = {}
        for url in urls:
            url_to_id_mapping[url.url] = url.id

        for url in urls:
            if url.is_error:
                continue
            for url_key in url_to_id_mapping:
                if url_key in url.content:
                    edge = [url.id, url_to_id_mapping[url_key]]
                    edges.append(edge)

            node = [url.id, {"url": url.url, "content": url.content, "metadata": url.metadata}]
            nodes.append(node)
        
        self.graph = nx.DiGraph(name="website graph")
        self.graph.add_nodes_from(nodes)
        self.graph.add_edges_from(edges)
        pr = nx.pagerank(self.graph, alpha=0.9)
        # sort the pagerank values in descending order
        sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)
        logger.info(f"pagerank results: {sorted_pr}")
        # get the top websites
        top_k_websites = sorted_pr[:top_k]
        urls_candidates = [self.graph.nodes[url_id] for url_id, _ in top_k_websites]
        urls_cleaned = [doc for doc in urls_candidates if doc]
        return urls_cleaned
    
    def to_crawled_local_objs(self, file_list: List[str]) -> List[CrawledLocalObject]:    
        local_objs = [LocalObject(str(uuid.uuid4()), file) for file in file_list]
        crawled_local_objs = [self.crawl_local(local_obj) for local_obj in local_objs]
        crawled_local_objs = list(filter(None, crawled_local_objs))
        return crawled_local_objs
    
    def crawl_local(self, local_obj: LocalObject) -> CrawledLocalObject:
        ## TODO: implement the local file crawling
        ext = os.path.splitext(local_obj.location)[1]
        logging.info(f"Crawling local file: {local_obj.location} with extension {ext}")
        
        if ext == ".txt" or ext == '.md':
            return CrawledLocalObject(
                local_obj.id,
                local_obj.location,
                content=open(local_obj.location, "r", encoding="utf-8").read(),
                metadata={"title": os.path.basename(local_obj.location), "source": local_obj.location},
            )
            
        elif ext == '.html':
            html = open(local_obj.location, "r", encoding="utf-8").read()
            soup = BeautifulSoup(html, "html.parser")

            text_list = []
            for string in soup.strings:        
                if string.find_parent("a"):
                    href = string.find_parent("a").get("href")
                    text = f"{string} {href}"
                    text_list.append(text)
                elif string.strip():
                    text_list.append(string)
            text_output = "\n".join(text_list)
            
            title = os.path.basename(local_obj.location)
            for title in soup.find_all("title"):
                title = title.get_text()
                break

            return CrawledLocalObject(
                    id=local_obj.id,
                    location=local_obj.location,
                    content=text_output,
                    metadata={"title": title, "source": local_obj.location},
                )
            
        elif ext =='pdf':
            # TODO
            pass
        
        return None
    
    @staticmethod
    def save(file_path: str, docs: List[CrawledObject]):
        with open(file_path, "wb") as f:
            pickle.dump(docs, f)
    
    @classmethod
    def chunk(cls, crawled_objs: List[CrawledObject]) -> List[CrawledObject]:
        text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(encoding_name="cl100k_base", chunk_size=200, chunk_overlap=40)
        docs = []
        langchain_docs = []
        for crawled_obj in crawled_objs:
            if crawled_obj.is_error or crawled_obj.content is None:
                logger.info(f"Skip source: {crawled_obj.location} because of error or no content")
                continue
            elif crawled_obj.is_chunk:
                logger.info(f"Skip source: {crawled_obj.location} because it has been chunked")
                docs.append(crawled_obj)
                continue
            splitted_text = text_splitter.split_text(crawled_obj.content)
            for i, txt in enumerate(splitted_text):
                doc = CrawledObject(
                    id=crawled_obj.id+"_"+str(i),
                    location=crawled_obj.location,
                    content=txt,
                    metadata=crawled_obj.metadata,
                    is_chunk=True,
                )
                docs.append(doc)
                langchain_docs.append(Document(page_content=txt, metadata={"source": crawled_obj.location}))
        return langchain_docs

