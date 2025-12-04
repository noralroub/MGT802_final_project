"""QA system for generating answers using LLM with retrieved context."""

import logging
from typing import List, Dict
from openai import OpenAI
from config import OPENAI_API_KEY
from core.retrieval import RAGPipeline

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


class QASystem:
    """Question-Answering system using RAG + LLM."""

    def __init__(self, pdf_path: str = None, collection_name: str = "medical_papers", model: str = "gpt-3.5-turbo"):
        """
        Initialize QA system.

        Args:
            pdf_path: Path to PDF to ingest (optional, can be set later)
            collection_name: Chroma collection name
            model: OpenAI model to use (gpt-3.5-turbo or gpt-4)
        """
        self.model = model
        self.pipeline = RAGPipeline(collection_name=collection_name)
        self.pdf_ingested = False

        if pdf_path:
            self.ingest_pdf(pdf_path)

        logger.info(f"Initialized QASystem with model: {model}")

    def ingest_pdf(self, pdf_path: str) -> Dict:
        """
        Ingest a PDF for question answering.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Ingestion result with metadata
        """
        try:
            result = self.pipeline.ingest_pdf(pdf_path)
            self.pdf_ingested = True
            logger.info(f"Ingested PDF: {pdf_path}")
            return result
        except Exception as e:
            logger.error(f"Error ingesting PDF: {e}")
            raise

    def _create_system_prompt(self) -> str:
        """Create system prompt for medical expert role."""
        return """You are an expert medical research analyst specializing in cardiovascular trials and clinical research.

Your role:
- Answer questions based ONLY on the provided context
- Be precise and cite specific numbers/statistics when available
- If information is not in the context, say "The context does not contain information about..."
- Format numerical results clearly with units and percentages
- Distinguish between trial arms (semaglutide vs. placebo) when comparing results

Guidelines:
- Keep answers concise and focused
- Use medical terminology accurately
- When describing outcomes, include both numbers and percentages
- Highlight statistically significant findings"""

    def _create_user_prompt(self, query: str, context: str) -> str:
        """
        Create user prompt with context and query.

        Args:
            query: User question
            context: Retrieved context chunks

        Returns:
            Formatted user prompt
        """
        return f"""Based on the following context from a cardiovascular trial paper, answer this question:

QUESTION: {query}

CONTEXT:
{context}

Please provide a clear, accurate answer based on the context provided."""

    def _format_context(self, retrieved_chunks: List[Dict]) -> str:
        """
        Format retrieved chunks into readable context.

        Args:
            retrieved_chunks: List of retrieved chunks with metadata

        Returns:
            Formatted context string
        """
        formatted_parts = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            similarity = chunk.get("similarity", 0)
            doc = chunk.get("document", "")
            formatted_parts.append(f"[Source {i}, relevance: {similarity:.2%}]\n{doc}\n")

        return "\n".join(formatted_parts)

    def generate_answer(self, query: str, top_k: int = 3, temperature: float = 0.7) -> Dict:
        """
        Generate an answer to a question using RAG + LLM.

        Args:
            query: Question to answer
            top_k: Number of chunks to retrieve
            temperature: LLM temperature (0-1, higher = more creative)

        Returns:
            Dictionary with answer, context, and metadata
        """
        if not self.pdf_ingested:
            raise ValueError("PDF not ingested. Call ingest_pdf() first.")

        try:
            # Step 1: Retrieve relevant chunks
            logger.info(f"Retrieving chunks for query: {query[:50]}...")
            retrieved_chunks = self.pipeline.retrieve(query, top_k=top_k)

            if not retrieved_chunks:
                return {
                    "answer": "No relevant information found in the document.",
                    "context": "",
                    "query": query,
                    "num_sources": 0,
                    "model": self.model
                }

            # Step 2: Format context
            context = self._format_context(retrieved_chunks)

            # Step 3: Create prompts
            system_prompt = self._create_system_prompt()
            user_prompt = self._create_user_prompt(query, context)

            # Step 4: Call LLM
            logger.info(f"Calling {self.model} for answer generation...")
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=500
            )

            answer = response.choices[0].message.content

            return {
                "answer": answer,
                "context": context,
                "query": query,
                "num_sources": len(retrieved_chunks),
                "model": self.model,
                "temperature": temperature,
                "tokens_used": response.usage.total_tokens if response.usage else None
            }

        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            raise

    def generate_answer_with_sources(self, query: str, top_k: int = 3) -> Dict:
        """
        Generate an answer with detailed source citations.

        Args:
            query: Question to answer
            top_k: Number of chunks to retrieve

        Returns:
            Dictionary with answer, sources, and metadata
        """
        result = self.generate_answer(query, top_k=top_k)

        # Extract source information
        sources = []
        retrieved_chunks = self.pipeline.retrieve(query, top_k=top_k)
        for i, chunk in enumerate(retrieved_chunks, 1):
            sources.append({
                "source_id": i,
                "similarity": chunk.get("similarity", 0),
                "preview": chunk.get("document", "")[:200] + "..."
            })

        result["sources"] = sources
        return result

    def batch_query(self, queries: List[str], top_k: int = 3) -> List[Dict]:
        """
        Answer multiple questions.

        Args:
            queries: List of questions
            top_k: Number of chunks to retrieve per query

        Returns:
            List of answer results
        """
        results = []
        for query in queries:
            try:
                result = self.generate_answer(query, top_k=top_k)
                results.append(result)
            except Exception as e:
                logger.error(f"Error answering query '{query}': {e}")
                results.append({
                    "query": query,
                    "answer": f"Error: {str(e)}",
                    "error": True
                })

        return results

    def get_system_info(self) -> Dict:
        """Get information about the QA system."""
        collection_info = self.pipeline.get_collection_info()
        return {
            "model": self.model,
            "pdf_ingested": self.pdf_ingested,
            "collection": collection_info,
            "api_key_configured": bool(OPENAI_API_KEY)
        }
