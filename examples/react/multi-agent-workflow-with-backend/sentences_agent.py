import asyncio
import re
from typing import Any

from common import SENTENCES_AGENT_ADDR
from naylence.agent import BaseAgent, configs


class SentencesAgent(BaseAgent):
    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> dict[str, Any] | str:
        # Simulate processing delay
        await asyncio.sleep(0.2)
        
        # Extract text from payload
        text = payload.get("text", "") if isinstance(payload, dict) else ""

        # Split into sentences (simple regex: split on . ! ?)
        sentences = re.split(r"[.!?]+", text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # Get first 3 sentences as preview
        preview = sentences[:3]

        return {"preview": preview, "totalSentences": len(sentences)}


if __name__ == "__main__":
    asyncio.run(
        SentencesAgent().aserve(
            SENTENCES_AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
