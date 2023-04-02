
import json
import logging
import multiprocessing
import requests

from tqdm import tqdm
from typing import List
from urllib.parse import urlparse
from bs4 import BeautifulSoup

from llama_index import Document
from llama_index.node_parser.node_utils import get_nodes_from_document
from llama_index.langchain_helpers.text_splitter import TokenTextSplitter
from llama_index.data_structs.node_v2 import Node
from llama_index import LLMPredictor, GPTFaissIndex, PromptHelper, ServiceContext
from langchain.llms import OpenAIChat

from crawler import http_get_with_caching

logger = logging.getLogger(__name__)
file_handler = logging.FileHandler('./db/logs/index.log', encoding='utf-8')
format = logging.Formatter('%(asctime)s [%(name)s] [%(levelname)s] %(message)s')
file_handler.setFormatter(format)
logger.addHandler(file_handler)
lock_logger = multiprocessing.Lock()

# with open('./valid_urls.jsonl', 'r') as f:
#     urls = f.readlines()
# urls = [json.loads(l) for l in urls]

# --- temp funcs ---
def url_filter(url):
    if ('do=diff&rev' in url) and ('howto.info.bit.edu.cn' in url):
        return False
    if ('cs.bit.edu.cn' not in url):
        return False
    else:
        return True

def get_urls_from_log():
    with open('./db/urls-0401.txt', 'r', encoding='utf-8') as f:
        log_lines = f.readlines()
    urls = []
    for u in log_lines:
        temp = u.split(':')
        if 'Succeed' in temp[2]:
            url = ':'.join(temp[3:]).strip()
            if url_filter(url):
                urls.append(url)
    print(len(urls))
    return urls
# --- end ---


text_splitter = TokenTextSplitter()
def process_url(url):
    try:
        page_content = requests.get(url, urlparse(url).netloc).content
        # TODO: 判别内容种类并使用不同的解析方法 e.g. HTML, pdf, MS doc, excel, image, video...
        soup = BeautifulSoup(page_content, "html.parser")
        data = soup.get_text(separator=' ', strip=True)
        extra_info = {"URL": url}
        doc = Document(data, extra_info=extra_info)
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
    with multiprocessing.Pool(processes=12) as pool:
        results = list(tqdm(pool.imap_unordered(process_url, urls), total=len(urls), colour='magenta'))
        for doc, nodes in results:
            if doc is not None:
                all_documents.append(doc)
            if nodes is not None:
                all_nodes.extend(nodes)
    print('num of documents:', len(all_documents))
    print('num of nodes:', len(all_nodes))
    return all_documents, all_nodes


def build_index(nodes):
    # define LLM
    openai_llm = OpenAIChat(
        model_name="gpt-3.5-turbo",
        temperature=0,
    )
    llm_predictor = LLMPredictor(llm=openai_llm)

    # define prompt helper
    # set maximum input size
    max_input_size = 4096
    # set number of output tokens
    num_output = 256
    # set maximum chunk overlap
    max_chunk_overlap = 20
    prompt_helper = PromptHelper(max_input_size, num_output, max_chunk_overlap)

    service_context = ServiceContext.from_defaults(llm_predictor=llm_predictor, prompt_helper=prompt_helper)

    # construct index
    index = GPTFaissIndex(nodes, service_context=service_context, faiss_index=None)
    # index = GPTFaissIndex.from_documents(all_documents, service_context=service_context)

    index.save_to_disk('index.json', encoding='utf-8')


if __name__ == '__main__':
    data = get_urls_from_log()
    build_documents(data)
