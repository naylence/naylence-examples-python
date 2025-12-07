import asyncio
import re
from typing import Any

from common import STATS_AGENT_ADDR
from naylence.agent import BaseAgent, configs


class StatsAgent(BaseAgent):
    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> dict[str, Any] | str:
        # Simulate processing delay
        await asyncio.sleep(0.25)
        
        # Extract text from payload
        text = payload.get("text", "") if isinstance(payload, dict) else ""

        # Calculate basic text statistics
        char_count = len(text)
        word_count = len(text.split()) if text.strip() else 0

        # Count sentences (simple regex: split on . ! ?)
        sentences = re.split(r"[.!?]+", text)
        sentence_count = len([s for s in sentences if s.strip()])

        # Calculate reading time (average 200 words per minute)
        reading_time_minutes = round(word_count / 200, 1) if word_count > 0 else 0

        return {
            "charCount": char_count,
            "wordCount": word_count,
            "sentenceCount": sentence_count,
            "readingTimeMinutes": reading_time_minutes,
        }


if __name__ == "__main__":
    asyncio.run(
        StatsAgent().aserve(
            STATS_AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
