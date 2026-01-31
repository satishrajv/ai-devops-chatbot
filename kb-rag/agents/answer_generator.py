"""
Agent 3: Answer Generator
Generates answers using LLM with retrieved context
"""

import logging
from typing import List, Dict
from openai import OpenAI
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from prompts import (
    SYSTEM_PROMPT_DEVOPS_ASSISTANT,
    ANSWER_GENERATION_TEMPLATE,
    FALLBACK_NO_CONTEXT_MESSAGE,
    detect_question_type,
    get_prompt_template,
    format_prompt
)

logger = logging.getLogger(__name__)


class AnswerGeneratorAgent:
    """Generates answers using OpenAI LLM with RAG context"""

    def __init__(self, openai_api_key: str, model: str = "gpt-4o-mini"):
        self.client = OpenAI(api_key=openai_api_key)
        self.model = model

    def generate_answer(self, user_question: str, retrieved_chunks: List[Dict], temperature: float = 0.3) -> Dict:
        """
        Generate answer using LLM with retrieved context

        Args:
            user_question: Original user question
            retrieved_chunks: Chunks from RAG retriever
            temperature: LLM temperature (0-1)

        Returns:
            Dict with final_answer, sources, and metadata
        """
        logger.info(f"[Answer Generator] Generating answer with {len(retrieved_chunks)} chunks")

        try:
            # Build context from retrieved chunks
            context = self._build_context(retrieved_chunks)
            logger.debug(f"Context length: {len(context)} characters")

            # Detect question type and get appropriate template
            question_type = detect_question_type(user_question)
            logger.info(f"Detected question type: {question_type}")

            # Get template and create prompt
            template = get_prompt_template(question_type)
            prompt = format_prompt(template, context=context, question=user_question)

            # Call OpenAI
            logger.info(f"Calling OpenAI {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT_DEVOPS_ASSISTANT
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature
            )

            answer = response.choices[0].message.content

            # Extract sources
            sources = self._extract_sources(retrieved_chunks)

            logger.info(f"Generated answer: {len(answer)} characters")
            logger.debug(f"Tokens used - Prompt: {response.usage.prompt_tokens}, Completion: {response.usage.completion_tokens}")

            return {
                'final_answer': answer,
                'sources': sources,
                'chunks_used': len(retrieved_chunks),
                'tokens_used': {
                    'prompt': response.usage.prompt_tokens,
                    'completion': response.usage.completion_tokens,
                    'total': response.usage.total_tokens
                }
            }

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}", exc_info=True)
            raise

    def generate_fallback(self, user_question: str) -> Dict:
        """
        Generate fallback response when no relevant chunks found

        Args:
            user_question: Original user question

        Returns:
            Dict with fallback answer
        """
        logger.warning("[Answer Generator] No relevant chunks found - generating fallback")

        # Use centralized fallback message
        fallback_answer = FALLBACK_NO_CONTEXT_MESSAGE

        return {
            'final_answer': fallback_answer,
            'sources': [],
            'chunks_used': 0,
            'is_fallback': True
        }

    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks"""
        context_parts = []

        for i, chunk in enumerate(chunks, 1):
            context_parts.append(
                f"[Document {i}: {chunk['filename']}]\n"
                f"{chunk['text']}\n"
            )

        return "\n---\n\n".join(context_parts)

    def _create_prompt(self, question: str, context: str) -> str:
        """
        Create prompt for LLM (legacy method - now using prompts.py)

        Note: This method is deprecated. Use format_prompt() from prompts.py instead.
        Kept for backwards compatibility.
        """
        logger.warning("Using deprecated _create_prompt method. Consider using prompts.py")
        return format_prompt(ANSWER_GENERATION_TEMPLATE, context=context, question=question)

    def _extract_sources(self, chunks: List[Dict]) -> List[str]:
        """Extract unique source filenames"""
        sources = []
        seen = set()

        for chunk in chunks:
            filename = chunk['filename']
            if filename not in seen:
                sources.append({
                    'filename': filename,
                    'chunk_id': chunk['chunk_id'],
                    'relevance': 1 - chunk['distance']  # Higher = more relevant
                })
                seen.add(filename)

        return sources
