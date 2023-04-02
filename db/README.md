# Website Crawler

URL filter criteria:

1. 解析 `urllib.parse.urlparse(url)` 不抛出异常
2. 'bit.edu.cn' 包含于 network location 部分
3. URL scheme 不为 mailto
4. URL 不以常见文件扩展名为结尾 e.g. `.pdf`, `.mp4` (从名称推断其应该为 HTML 格式)
5. 域名不在 `skipping_domain_names` 中
6. URL 不包含某些特殊的 pattern, 例如 path 不能以 login 为结尾，不收集系统登录页面
7. 通过 HTTP GET 访问后未抛出异常且状态码为 200
8. URL network location 不包含 @

URL 收集 1.0

- 爬取全部域名包含 `bit.edu.cn` 的网页 URL
- 跳过两个与文献库相关的网站 'journal.bit.edu.cn', 'ico.bit.edu.cn'
- 收集时间 2023-04-01 22:47 - 2023-04-02 03:53
- 共访问 414,391 个不同的 URL，成功访问 375,916 个网页
- 经筛选去重等预处理后 (`url_preprocess.ipynb`)，得到 112,486 个 URL
- 保存于 `db/urls-0402.json`
