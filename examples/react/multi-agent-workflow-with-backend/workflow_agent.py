import asyncio
from typing import Any

from common import (
    WORKFLOW_AGENT_ADDR,
    STATS_AGENT_ADDR,
    KEYWORDS_AGENT_ADDR,
    SENTENCES_AGENT_ADDR,
)

from naylence.agent import Agent, BaseAgent, configs


class WorkflowAgent(BaseAgent):
    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> dict[str, Any] | str:
        # Extract text from payload
        text = payload.get("text", "") if isinstance(payload, dict) else ""

        # Fan out to all worker agents using broadcast
        results = await Agent.broadcast(
            [STATS_AGENT_ADDR, KEYWORDS_AGENT_ADDR, SENTENCES_AGENT_ADDR], {"text": text}
        )

        # Return aggregated result
        return {
            "stats": results[0][1],
            "keywords": results[1][1],
            "sentences": results[2][1],
        }


if __name__ == "__main__":
    asyncio.run(
        WorkflowAgent().aserve(
            WORKFLOW_AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
