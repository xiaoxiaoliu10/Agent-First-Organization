import logging
import time
from pathlib import Path
from typing import List, Set, Tuple
import requests
import pickle

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import networkx as nx


logger = logging.getLogger(__name__)

CHROME_DRIVER_VERSION = "125.0.6422.7"

class URLObject:
    def __init__(self, id: str, url: str):
        self.id = id
        self.url = url

    @classmethod
    def from_dict(self, data):
        return URLObject(data["id"], data["url"])


class CrawledURLObject(URLObject):
    def __init__(
        self,
        id: str,
        url: str,
        content: str,
        metadata={},
        is_error=False,
        error_message=None,
    ):
        super().__init__(id, url)
        self.content = content
        self.metadata = metadata
        self.is_error = is_error
        self.error_message = error_message


class Loader:
    def __init__(self, source: str, max_num: int):
        self.doc_source = source
        self.max_num = max_num

    def crawl_urls(self, url_objects: list[URLObject]) -> List[CrawledURLObject]:
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

                # text_output = soup.get_text(separator=" ", strip=True)
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
    
    def _check_url(self, full_url, base_url):
        kw_list = ['.pdf', '.jpg', '.png', '.docx', '.xlsx', '.pptx', '.zip', ".jpeg"]
        if full_url.startswith(base_url) and full_url and not any(kw in full_url for kw in kw_list) and full_url != base_url:
            return True
        return False


    def get_outsource_links(self, curr_url: str, base_url: str):
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

    def get_all_urls(self):
        logger.info(f"Getting all pages for base url: {self.doc_source}, maximum number is: {self.max_num}")
        urls_visited = []
        base_url = self.doc_source.split("#")[0].rstrip("/")
        urls_to_visit = [base_url]
        
        while urls_to_visit:
            if len(urls_visited) >= self.max_num:
                break
            current_url = urls_to_visit.pop(0)
            if current_url not in urls_visited:
                urls_visited.append(current_url)
                new_urls = self.get_outsource_links(current_url, base_url)
                urls_to_visit.extend(new_urls)
                urls_to_visit = list(set(urls_to_visit))

        return sorted(urls_visited[:self.max_num])

    def get_candidates_websites(self, urls: List[CrawledURLObject]) -> List[str]:
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
        if self.max_num > 50:
            limit = self.max_num // 5
        else:
            limit = 10
        top_10_websites = sorted_pr[:limit]
        urls_candidates = [self.graph.nodes[url_id] for url_id, _ in top_10_websites] 
        return urls_candidates
    
    def save(self, docs):
        pickle.dump(docs, open("agentorg/orchestrator/examples/documents.pkl", "wb"))
    
    def load(self):
        if Path("agentorg/orchestrator/examples/documents.pkl").exists():
            crawled_docs = pickle.load(open("agentorg/orchestrator/examples/documents.pkl", "rb"))
        else:
            all_urls = self.get_all_urls()
            url_objects = [URLObject(str(idx), url) for idx, url in enumerate(all_urls)]
            crawled_docs = self.crawl_urls(url_objects)
            self.save(crawled_docs)
        top_urls = self.get_candidates_websites(crawled_docs)
        return top_urls
        