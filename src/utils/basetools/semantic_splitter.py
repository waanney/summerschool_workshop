"""
Semantic text splitting module.

This module provides functionality for splitting text into semantically coherent chunks
using sentence transformers and spaCy for natural language processing. It supports
multilingual text with configurable chunk sizes and similarity thresholds.
"""

from __future__ import annotations

import re
from typing import List, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

import numpy as np
import spacy
from sentence_transformers import SentenceTransformer
import docx2txt
import PyPDF2


class Language(str, Enum):
    """Enum for supported languages."""

    VIETNAMESE = "vi"
    ENGLISH = "en"
    MULTILINGUAL = "multi"


class FileType(str, Enum):
    """Enum for supported file types."""

    TXT = "txt"
    PDF = "pdf"
    DOCX = "docx"


def load_txt(path: str | Path) -> str:
    """
    Load text content from a .txt file.

    Args:
        path: Path to the text file

    Returns:
        str: Content of the text file

    Raises:
        FileNotFoundError: If the file doesn't exist
        UnicodeDecodeError: If the file encoding is not UTF-8
    """
    return Path(path).read_text(encoding="utf-8")


def load_pdf(path: str | Path) -> str:
    """
    Load text content from a .pdf file.

    Args:
        path: Path to the PDF file

    Returns:
        str: Extracted text content from all pages

    Raises:
        FileNotFoundError: If the file doesn't exist
        PyPDF2.PdfReadError: If the PDF is corrupted or unreadable
    """
    text: str = ""
    with open(path, "rb") as f:
        for page in PyPDF2.PdfReader(f).pages:
            text += page.extract_text() or ""
    return text


def load_docx(path: str | Path) -> str:
    """
    Load text content from a .docx file.

    Args:
        path: Path to the DOCX file

    Returns:
        str: Extracted text content from the document

    Raises:
        FileNotFoundError: If the file doesn't exist
        docx2txt.Docx2txtError: If the DOCX file is corrupted
    """
    result: str = docx2txt.process(str(path))
    return result if isinstance(result, str) else ""


@dataclass
class SemanticSplitter:
    """
    Semantic text splitter for creating coherent text chunks.

    This class splits text into semantically meaningful chunks based on sentence
    similarity and token limits. It uses sentence transformers for embedding
    and spaCy for sentence tokenization.
    """

    model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    language: Language = Language.MULTILINGUAL
    max_tokens: int = 200
    min_similarity: float = 0.6
    overlap: int = 0

    _nlp: spacy.language.Language = field(init=False, repr=False)
    _model: SentenceTransformer = field(init=False, repr=False)

    def __post_init__(self) -> None:
        """Initialize spaCy pipeline and sentence transformer model."""
        if self.language == Language.VIETNAMESE:
            # Use blank Vietnamese pipeline + sentencizer
            self._nlp = spacy.blank("vi")
            self._nlp.add_pipe(
                "sentencizer", config={"punct_chars": [".", "!", "?", "…"]}
            )
            if self.model_name == "all-MiniLM-L6-v2":
                self.model_name = (
                    "paraphrase-multilingual-MiniLM-L12-v2"
                )
        elif self.language == Language.ENGLISH:
            # Use blank English pipeline + sentencizer
            self._nlp = spacy.blank("en")
            self._nlp.add_pipe("sentencizer")
        elif self.language == Language.MULTILINGUAL:
            # Use blank multilingual pipeline + sentencizer
            self._nlp = spacy.blank("xx")  # Universal language code
            self._nlp.add_pipe(
                "sentencizer", config={"punct_chars": [".", "!", "?", "…"]}
            )
        else:
            self._nlp = spacy.blank("en")
            self._nlp.add_pipe("sentencizer")

        self._model = SentenceTransformer(self.model_name)

    def split(self, text: str) -> List[str]:
        """
        Split text into semantically coherent chunks.

        Args:
            text: Input text to be split

        Returns:
            List[str]: List of text chunks

        Raises:
            ValueError: If text is empty or None
        """
        if not text or not text.strip():
            return []

        sentences: List[str] = self._sentences(text)
        if not sentences:
            return []

        sims: np.ndarray = self._pairwise_similarities(self._embeddings(sentences))
        chunks: List[List[str]] = [[]]
        counts: List[int] = [0]

        for i, sent in enumerate(sentences):
            tokens: int = self._estimate_tokens(sent)
            same_topic: bool = not chunks[-1] or sims[i - 1] >= self.min_similarity
            fits: bool = counts[-1] + tokens <= self.max_tokens

            if same_topic and fits:
                chunks[-1].append(sent)
                counts[-1] += tokens
            else:
                overlap_sents: List[str] = (
                    chunks[-1][-self.overlap :] if self.overlap else []
                )
                chunks.append(overlap_sents + [sent])
                counts.append(sum(map(self._estimate_tokens, overlap_sents)) + tokens)

        return [" ".join(c).strip() for c in chunks if c]

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        Estimate the number of tokens in a text string.

        Args:
            text: Text to estimate tokens for

        Returns:
            int: Estimated number of tokens
        """
        return len(re.findall(r"\w+", text))

    def _sentences(self, text: str) -> List[str]:
        """
        Extract sentences from text using spaCy.

        Args:
            text: Text to extract sentences from

        Returns:
            List[str]: List of sentence strings
        """
        return [s.text.strip() for s in self._nlp(text.strip()).sents if s.text.strip()]

    def _embeddings(self, sents: Sequence[str]) -> np.ndarray:
        """
        Generate embeddings for a sequence of sentences.

        Args:
            sents: Sequence of sentence strings

        Returns:
            np.ndarray: Array of sentence embeddings
        """
        return self._model.encode(sents, convert_to_numpy=True, normalize_embeddings=True)  # type: ignore

    @staticmethod
    def _pairwise_similarities(embeds: np.ndarray) -> np.ndarray:
        """
        Calculate pairwise similarities between consecutive embeddings.

        Args:
            embeds: Array of embeddings

        Returns:
            np.ndarray: Array of similarity scores between consecutive embeddings
        """
        if embeds.shape[0] < 2:
            return np.array([], dtype=np.float32)
        return np.sum(embeds[:-1] * embeds[1:], axis=1)
