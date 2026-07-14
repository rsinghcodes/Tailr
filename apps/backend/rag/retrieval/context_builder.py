from domain.shared.vector_store import RetrievalResult


class ContextBuilder:
    """Service to format retrieved resume chunks into a structured text context block."""

    def build_context(self, retrieval_results: list[RetrievalResult]) -> str:
        """Formats a list of retrieval results into a clean markdown block.

        Args:
            retrieval_results: The list of ranked RetrievalResult objects.

        Returns:
            A formatted markdown string.
        """
        if not retrieval_results:
            return "No relevant context found from the candidate's resume."

        lines = [
            "### Candidate Resume Context",
            "Below are the relevant segments extracted from the candidate's resume, ordered by relevance:",
            ""
        ]

        for idx, res in enumerate(retrieval_results, 1):
            category = res.chunk.metadata.category
            score_text = f"Relevance Score: {res.score:.1f}" if res.score <= 5.0 else "Match Rank"
            
            lines.append(f"#### Segment {idx}: {category} ({score_text})")
            lines.append("```")
            lines.append(res.chunk.content)
            lines.append("```")
            if res.reason:
                lines.append(f"*Assessment: {res.reason}*")
            lines.append("")

        return "\n".join(lines).strip()
