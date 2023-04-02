"""Simple web crawler"""
import logging
import requests
from typing import List
from tqdm import tqdm
from urllib import parse
from bs4 import BeautifulSoup
from url_normalize import url_normalize


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'

logger = logging.getLogger('crawler')
file_handler = logging.FileHandler('./db/logs/urls.log', encoding='utf-8')
format = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(format)
logger.addHandler(file_handler)
logger.setLevel(logging.INFO)


seed_url = 'http://www.bit.edu.cn/'
seed_name = 'bit.edu.cn'
non_html_exts = set([
    'exe', 'apk', 'rar', 'zip', '7z', 'tgz',
    'png', 'jpeg', 'jpg', 'gif', 'mp3', 'mp4', 'mov', 'mpeg', 'avi', 'tif', '3gp', 'swf', 'wmv',
    'ai', 'dwg', 'vcf',
    'pptx', 'ppt', 'xls', 'xlsx', 'docx', 'doc', 'pdf', 'wps', 'pps', 'rtf','pptx',
    'eml', 'mht',
])
skipping_domain_names = set([
    'journal.bit.edu.cn',
    'ico.bit.edu.cn',
])
skipping_patterns = [
    'csvrlab.bit.edu.cn/course_cs_exp_intro.php',
    'login?service=',
    'login?locale=',
    'do=diff&rev',
]
visited = set()


# @Cache(cache_path='./db/cache_http_get/{netloc}/{_hash}.pkl', args_to_ignore=('url'))
def http_get_with_caching(url, netloc):
    """cache the request; save content if succeed."""
    try:
        response = requests.get(url, headers={'User-Agent': user_agent}, timeout=5)
        if response.status_code == 200:
            logger.info(f'Succeed: {url}')
            # with open('./valid_urls.jsonl', 'a') as f:
            #     f.write(json.dumps(url)+'\n')
            return response.content
        else:
            logger.info(f'Fail(Status {response.status_code}): {url}')
    except Exception as e:
        logger.info(f'Fail({type(e).__name__}): {url}')
    return None


def validate_url(url: str):
    try:
        # remove fragment & normalize
        parse_result = parse.urlparse(url)._replace(fragment='')
        url = url_normalize(parse_result.geturl())
    except:
        return None
    if seed_name not in parse_result.netloc:
        return None
    if parse_result.scheme == 'mailto':
        return None
    if parse_result.netloc in skipping_domain_names:
        return None
    if url.split('.')[-1].lower() in non_html_exts:
        return None
    if parse_result.path.endswith('login'):
        return None
    for p in skipping_patterns:
        if p in url:
            return None
    if url in visited:
        return None
    
    return url



def get_links(url: str) -> List[str]:
    links = []
    try:
        parse_result = parse.urlparse(url)
        content_bytes = http_get_with_caching(url, parse_result.netloc.replace(':', '-'))
        soup = BeautifulSoup(content_bytes, 'html.parser')

        # find all links with 'bit.edu.cn'
        for link in soup.find_all('a'):
            # append href to links if valid
            href = link.get('href')
            valid_url = validate_url(href)
            if valid_url is not None:
                links.append(valid_url)
                continue
            # handle relative path
            full_url = parse.urljoin(url, href)
            valid_url = validate_url(full_url)
            if valid_url is not None:
                links.append(valid_url)
    except:
        pass
    return links


def crawl(start_url):
    queue = [start_url]
    pbar = tqdm(desc='')
    while queue:
        url = queue.pop(0)
        pbar.set_postfix({'in_queue': len(queue), 'visited': len(visited)})

        if url not in visited:
            visited.add(url)
            links = get_links(url)
            queue.extend(links)

        pbar.update(1)
    pbar.close()


if __name__ == '__main__':
    urls = crawl(seed_url)
