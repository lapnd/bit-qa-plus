

from llama_index import LLMPredictor, PromptHelper, ServiceContext, LangchainEmbedding
from llama_index import GPTWeaviateIndex
from langchain.embeddings.cohere import CohereEmbeddings
from langchain.llms import OpenAIChat


def build_index(nodes):
    
    openai_llm = OpenAIChat(
        openai_api_key='fake',
        model_name="gpt-3.5-turbo",
        temperature=0,
    )
    llm_predictor = LLMPredictor(llm=openai_llm)

    prompt_helper = PromptHelper(
        max_input_size=4096, # llm total tokens
        num_output=256, # tokens reserved for output
        max_chunk_overlap=20, # maximum chunk overlap for the LLM
    )

    embedding_model = LangchainEmbedding(CohereEmbeddings(
        model='multilingual-22-12',
        cohere_api_key='fake'
    ))

    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, 
        prompt_helper=prompt_helper,
        embed_model=embedding_model
    )

    # construct index
    index = GPTWeaviateIndex(
        nodes=nodes,
        service_context=service_context,
        weaviate_client=None,
        class_prefix='test',
    )

    index.save_to_disk('index.json', encoding='utf-8')
    