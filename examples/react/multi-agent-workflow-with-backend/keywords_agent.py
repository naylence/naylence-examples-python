import asyncio
import re
from typing import Any
from collections import Counter

from common import KEYWORDS_AGENT_ADDR
from naylence.agent import BaseAgent, configs


class KeywordsAgent(BaseAgent):
    # Common words to exclude
    STOP_WORDS = {
        "the",
        "be",
        "to",
        "of",
        "and",
        "a",
        "in",
        "that",
        "have",
        "i",
        "it",
        "for",
        "not",
        "on",
        "with",
        "he",
        "as",
        "you",
        "do",
        "at",
        "this",
        "but",
        "his",
        "by",
        "from",
        "they",
        "we",
        "say",
        "her",
        "she",
        "or",
        "an",
        "will",
        "my",
        "one",
        "all",
        "would",
        "there",
        "their",
        "what",
        "so",
        "up",
        "out",
        "if",
        "about",
        "who",
        "get",
        "which",
        "go",
        "me",
        "when",
        "make",
        "can",
        "like",
        "time",
        "no",
        "just",
        "him",
        "know",
        "take",
        "people",
        "into",
        "year",
        "your",
        "good",
        "some",
        "could",
        "them",
        "see",
        "other",
        "than",
        "then",
        "now",
        "look",
        "only",
        "come",
        "its",
        "over",
        "think",
        "also",
        "back",
        "after",
        "use",
        "two",
        "how",
        "our",
        "work",
        "first",
        "well",
        "way",
        "even",
        "new",
        "want",
        "because",
        "any",
        "these",
        "give",
        "day",
        "most",
        "us",
        "is",
        "was",
        "are",
        "been",
        "has",
        "had",
        "were",
        "said",
        "did",
    }

    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> dict[str, Any] | str:
        # Simulate processing delay
        await asyncio.sleep(0.25)
        
        # Extract text from payload
        text = payload.get("text", "") if isinstance(payload, dict) else ""

        # Extract words (lowercase, alphanumeric only)
        words = re.findall(r"\b[a-z]+\b", text.lower())

        # Filter out stop words and count
        filtered_words = [w for w in words if w not in self.STOP_WORDS and len(w) > 2]
        word_counts = Counter(filtered_words)

        # Get top 10 most common
        top_words = [
            {"word": word, "count": count} for word, count in word_counts.most_common(10)
        ]

        return {"topWords": top_words}


if __name__ == "__main__":
    asyncio.run(
        KeywordsAgent().aserve(
            KEYWORDS_AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
