"""crawl file links from given list of urls"""
import multiprocessing
import requests
import json
import logging
import time
from functools import wraps
from tqdm import tqdm
from typing import List
from urllib import parse

from bs4 import BeautifulSoup
from url_normalize import url_normalize


logger = logging.getLogger('crawler')
file_handler = logging.FileHandler('./db/logs/file-urls.log', encoding='utf-8')
format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(format)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)
lock_logger = multiprocessing.Lock()

seed_name = 'bit.edu.cn'
unstructured_supported_file_exts = set([
    'docx', 'doc', 'pptx', 'ppt', 'pdf', 'txt',
])
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'

visited = set()


# def retry(wait_sec, retries):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args, **kwargs):
#             for i in range(retries):
#                 try:
#                     return func(*args, **kwargs)
#                 except:
#                     time.sleep(wait_sec)
#             return func(*args, **kwargs)
#         return wrapper
#     return decorator


# @retry(5, 5)
def http_get(url):
    try:
        response = requests.get(url, headers={'User-Agent': user_agent}, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            with lock_logger:
                logger.info(f'Fail(Status {response.status_code}): {url}')
    except Exception as e:
        with lock_logger:
            logger.info(f'Fail({type(e).__name__}): {url}')
    return None


def get_ext(url: str):
    parse_result = parse.urlparse(url)._replace(fragment='')
    url = url_normalize(parse_result.geturl())
    return url.split('.')[-1].lower()

def is_file_url(url: str):
    if url is None or len(url) == 0:
        return False
    try:
        # remove fragment & normalize
        parse_result = parse.urlparse(url)._replace(fragment='')
        url = url_normalize(parse_result.geturl())
    except:
        return False
    if seed_name not in parse_result.netloc:
        return False
    if parse_result.scheme == 'mailto':
        return False
    if url in visited:
        return False
    if url.split('.')[-1].lower() in unstructured_supported_file_exts:
        return True
    return False

    
def get_files(url: str) -> List[dict]:
    files = []
    try:
        content_bytes = http_get(url)
        if content_bytes is None:
            return files
        soup = BeautifulSoup(content_bytes, 'html.parser')

        # find all links with 'bit.edu.cn'
        for link in soup.find_all('a'):
            # append href to links if valid
            href = link.get('href')
            full_url = parse.urljoin(url, href)
            # log file urls (but do not http-get)
            if is_file_url(href):
                files.append({'name': link.text.strip(), 'url': href, 'from': url})
            elif is_file_url(full_url):
                files.append({'name': link.text.strip(), 'url': full_url, 'from': url})

    except Exception as e:
        print(f'error when scraping {url}: {str(e)}')
        pass
    return files


def main(from_path='./db/urls-0402.json', save_path='./db/filelinks.json'):
    with open(from_path, 'r') as f:
        urls = json.loads(f.read())

    with multiprocessing.Pool(processes=15) as pool:
        results = list(tqdm(pool.imap_unordered(get_files, urls), total=len(urls), colour='magenta'))
    all_files = []
    # for u in urls:
    #     all_files.extend(get_files(u))
    for f in results:
        all_files.extend(f)
    
    print(len(all_files))
    tuple_set = set()
    unique_filelinks = []
    for f in all_files:
        id = f['name']+' : '+f['url']+' : '+f['from']
        if id in tuple_set:
            continue
        tuple_set.add(id)
        f['format'] = get_ext(f['url'])
        unique_filelinks.append(f)
    print(len(unique_filelinks))
    
    with open(save_path, 'w') as f:
        json.dump(unique_filelinks, f, indent=4)


if __name__ == '__main__':
    main()
