# BitQA的相关开发流程

克隆地址：

`git clone https://github.com/habaneraa/bit-qa-plus`

创建新的代码分支：

`git checkout -b <your_branch_name>`

修改、提交、推送三件套

`git add .`

`git commit -m "ADD: BitQA Git Develop Readme"`

`git push --set-upstream origin <your_branch_name>`

下方会有一个pull_request的链接

```shell
Total 0 (delta 0), reused 0 (delta 0), pack-reused 0
remote: 
remote: Create a pull request for 'yidi_first_merge_request' on GitHub by visiting:
remote:      https://github.com/habaneraa/bit-qa-plus/pull/new/yidi_first_merge_request
remote: 
To github.com:habaneraa/bit-qa-plus.git
 * [new branch]      yidi_first_merge_request -> yidi_first_merge_request
branch 'yidi_first_merge_request' set up to track 'origin/yidi_first_merge_request'.
```

进入链接后创建pull request，然后Enjoy！

# 技术方案

- [LangChain](https://python.langchain.com/en/latest/index.html)
- [LlamaIndex](https://gpt-index.readthedocs.io/en/latest/). [A blog by the creator of LlamaIndex](https://medium.com/@jerryjliu98/how-unstructured-and-llamaindex-can-help-bring-the-power-of-llms-to-your-own-data-3657d063e30d)
- [Multilingual embedding model from Cohere](https://txt.cohere.ai/multilingual/), [integrated by LangChain](https://python.langchain.com/en/latest/modules/models/text_embedding/examples/cohere.html)
