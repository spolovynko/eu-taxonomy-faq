from functools import lru_cache

from eu_taxonomy_rag.agent.generation import OpenAIClient
from eu_taxonomy_rag.agent.rag_agent import RAGAgent
from eu_taxonomy_rag.agent.retrieval import QdrantVectorStore, Retriever
from eu_taxonomy_rag.config import get_settings
from eu_taxonomy_rag.data_ingestion.openai_embedder import OpenAIEmbedder


class AgentFactory:
    @lru_cache(maxsize=1)
    def create(self) -> RAGAgent:
        settings = get_settings()

        embedder = OpenAIEmbedder(
            base_url=settings.embedding_base_url,
            api_key=settings.embedding_api_key,
            model=settings.embedding_model,
            batch_size=settings.embedding_batch_size,
        )
        vector_store = QdrantVectorStore(
            url=settings.qdrant_url,
            collection_name=settings.qdrant_collection,
        )
        retriever = Retriever(
            embedder=embedder,
            vector_store=vector_store,
        )
        llm_client = OpenAIClient(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            model=settings.llm_model,
            temperature=settings.llm_temperature,
        )

        return RAGAgent(
            retriever=retriever,
            llm_client=llm_client,
            top_k=settings.top_k,
        )


agent_factory = AgentFactory()
