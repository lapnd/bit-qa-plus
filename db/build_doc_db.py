
import json
import logging
import multiprocessing
import requests
import pickle
import os

from tqdm import tqdm
from typing import List
from urllib.parse import urlparse
from bs4 import BeautifulSoup

import tiktoken
from llama_index import Document
from llama_index.node_parser.node_utils import get_nodes_from_document
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.data_structs.node_v2 import Node

from simple_cache import cache

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('./db/logs/index.log', encoding='utf-8')
format = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
file_handler.setFormatter(format)
logger.addHandler(file_handler)

use_multiprocess = False
lock_logger = multiprocessing.Lock()
if use_multiprocess:
    num_processes = os.cpu_count() - 1

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'

text_splitter = TokenTextSplitter()


@cache('./db/cache_http_get/')
def url2content(url: str) -> bytes:
    page_content = requests.get(url, headers={'User-Agent': user_agent}, timeout=5).content
    # response = requests.get(url, headers={'User-Agent': user_agent}, timeout=5)
    # page_content = response.content.decode(encoding=response.apparent_encoding)
    return page_content


def process_url(url, type='html'):
    """url -> http response -> elements -> document"""
    try:
        page_content = url2content(url)
        # TODO: (unstructured.partition)判别内容种类并使用不同的解析方法 e.g. HTML, pdf, MS doc, excel, image, video...
        if type == 'html':
            soup = BeautifulSoup(page_content, "html.parser")
            text = soup.get_text(separator=' ', strip=True)
        elif type == 'unk':
            pass

        doc = Document(text, extra_info={"URL": url})
        nodes = get_nodes_from_document(doc, text_splitter)
        return doc, nodes
    except requests.RequestException as e:
        with lock_logger:
            logger.warning('network error: %s. %s', url, str(e))
    except ValueError as e:
        with lock_logger:
            logger.error('parse failed: %s. %s', url, str(e))
    except KeyboardInterrupt:
        raise KeyboardInterrupt()
    except Exception as e:
        with lock_logger:
            logger.error('unknown error: %s. %s', url, str(e))
    return None, None


def build_documents(urls):
    # Build documents of urls. Parse document into nodes.
    all_documents: List[Document] = []
    all_nodes: List[Node] = []
    if use_multiprocess:
        with multiprocessing.Pool(processes=num_processes) as pool:
            results = list(tqdm(pool.imap_unordered(process_url, urls), total=len(urls), colour='magenta'))
            for doc, nodes in results:
                if doc is not None:
                    all_documents.append(doc)
                if nodes is not None:
                    all_nodes.extend(nodes)
    else:
        for u in tqdm(urls, colour='blue'):
            doc, nodes = process_url(url=u)
            if doc:
                all_documents.append(doc)
            if nodes:
                all_nodes.extend(nodes)
    url2content.save_cache()
    print('num of documents:', len(all_documents))
    print('num of nodes:', len(all_nodes))
    return all_documents, all_nodes


def main():
    with open('./db/urls-0402.json', 'r') as f:
        data = json.loads(f.read())
    # data = data[:1000]

    d, n = build_documents(data)
    with open('./db/documents.pkl', 'wb') as file:
        pickle.dump(d, file)
    with open('./db/doc_nodes.pkl', 'wb') as file:
        pickle.dump(n, file)

    num_tokens = 0
    encoding = tiktoken.get_encoding('cl100k_base')
    for node in n:
        num_tokens += len(encoding.encode(node.text))
    print(num_tokens) # 213423647


if __name__ == '__main__':
    main()
