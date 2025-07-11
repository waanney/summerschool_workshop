from __future__ import annotations

import re
from typing import List, Sequence
from dataclasses import dataclass, field

import numpy as np
import spacy
from sentence_transformers import SentenceTransformer

from pathlib import Path
import docx2txt, PyPDF2

def load_txt(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")

def load_pdf(path: str | Path) -> str:
    text = ""
    with open(path, "rb") as f:
        for page in PyPDF2.PdfReader(f).pages:
            text += page.extract_text() or ""
    return text

def load_docx(path: str | Path) -> str:
    return docx2txt.process(str(path))

@dataclass
class SemanticSplitter:
    model_name: str = "bkai-foundation-models/vietnamese-bi-encoder"
    language: str = "vi"  # "en" or "vi"
    max_tokens: int = 200
    min_similarity: float = 0.6
    overlap: int = 0

    _nlp: spacy.language.Language = field(init=False, repr=False)
    _model: SentenceTransformer = field(init=False, repr=False)

    def __post_init__(self):
        if self.language == "vi":
            # Use blank Vietnamese pipeline + sentencizer
            self._nlp = spacy.blank("vi")
            self._nlp.add_pipe(
                "sentencizer", config={"punct_chars": [".", "!", "?", "…"]}
            )
            if self.model_name == "sentence-transformers/all-MiniLM-L6-v2":
                self.model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        else:
            self._nlp = spacy.blank("en")
            self._nlp.add_pipe("sentencizer")

        self._model = SentenceTransformer(self.model_name)

    def split(self, text: str) -> List[str]:
        sentences = self._sentences(text)
        if not sentences:
            return []

        sims = self._pairwise_similarities(self._embeddings(sentences))
        chunks: List[List[str]] = [[]]
        counts: List[int] = [0]

        for i, sent in enumerate(sentences):
            tokens = self._estimate_tokens(sent)
            same_topic = not chunks[-1] or sims[i - 1] >= self.min_similarity
            fits = counts[-1] + tokens <= self.max_tokens

            if same_topic and fits:
                chunks[-1].append(sent)
                counts[-1] += tokens
            else:
                overlap_sents = chunks[-1][-self.overlap :] if self.overlap else []
                chunks.append(overlap_sents + [sent])
                counts.append(
                    sum(map(self._estimate_tokens, overlap_sents)) + tokens
                )

        return [" ".join(c).strip() for c in chunks if c]

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        return len(re.findall(r"\w+", text))

    def _sentences(self, text: str) -> List[str]:
        return [s.text.strip() for s in self._nlp(text.strip()).sents if s.text.strip()]

    def _embeddings(self, sents: Sequence[str]) -> np.ndarray:
        return self._model.encode(sents, convert_to_numpy=True, normalize_embeddings=True)

    @staticmethod
    def _pairwise_similarities(embeds: np.ndarray) -> np.ndarray:
        if embeds.shape[0] < 2:
            return np.array([])
        return np.sum(embeds[:-1] * embeds[1:], axis=1)
