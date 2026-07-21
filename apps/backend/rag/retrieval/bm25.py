import math
import re


class BM25Scorer:
    """Lightweight, in-memory implementation of the BM25 (Okapi) ranking algorithm."""

    def __init__(self, corpus: list[str], k1: float = 1.5, b: float = 0.75):
        """Initializes the BM25 scorer with a corpus of document texts.

        Args:
            corpus: A list of document texts (e.g. chunk contents).
            k1: BM25 scale parameter (default: 1.5).
            b: BM25 length normalization parameter (default: 0.75).
        """
        self.k1 = k1
        self.b = b
        self.corpus_size = len(corpus)
        
        # Tokenize the corpus
        self.doc_tokens = [self._tokenize(doc) for doc in corpus]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_length = sum(self.doc_lengths) / max(self.corpus_size, 1)

        # Calculate Document Frequencies (DF) for IDF calculation
        self.doc_frequencies: dict[str, int] = {}
        for tokens in self.doc_tokens:
            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.doc_frequencies[token] = self.doc_frequencies.get(token, 0) + 1

    def _tokenize(self, text: str) -> list[str]:
        """Splits text into lower-cased alphanumeric word tokens.

        Args:
            text: Input string.

        Returns:
            A list of lowercased string word tokens.
        """
        # Convert to lowercase and find all word sequences
        words = re.findall(r'\b\w+\b', text.lower())
        return words

    def _calculate_idf(self, word: str) -> float:
        """Calculates Inverse Document Frequency (IDF) for a term using the BM25 formula.

        Args:
            word: The term/word token.

        Returns:
            The float IDF score.
        """
        df = self.doc_frequencies.get(word, 0)
        # standard BM25 IDF with smoothing
        numerator = self.corpus_size - df + 0.5
        denominator = df + 0.5
        return math.log(max(numerator / denominator, 0.0001) + 1.0)

    def score(self, query: str) -> list[float]:
        """Calculates BM25 relevance scores for all documents in the corpus against a query.

        Args:
            query: The search query text.

        Returns:
            A list of float BM25 scores parallel to the corpus index.
        """
        query_tokens = self._tokenize(query)
        scores = []

        for doc_idx, tokens in enumerate(self.doc_tokens):
            doc_len = self.doc_lengths[doc_idx]
            
            # Count term frequencies in this document
            tf_map: dict[str, int] = {}
            for token in tokens:
                tf_map[token] = tf_map.get(token, 0) + 1

            doc_score = 0.0
            for q_term in query_tokens:
                tf = tf_map.get(q_term, 0)
                if tf == 0:
                    continue

                idf = self._calculate_idf(q_term)
                
                # BM25 term score formula
                numerator = tf * (self.k1 + 1)
                denominator = tf + self.k1 * (1 - self.b + self.b * (doc_len / max(self.avg_doc_length, 1)))
                
                doc_score += idf * (numerator / denominator)

            scores.append(doc_score)

        return scores
