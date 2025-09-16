import asyncio
from typing import Any

from common import ANALYSIS_AGENT_ADDR, SENTIMENT_AGENT_ADDR, SUMMARIZER_AGENT_ADDR

from naylence.agent import Agent, BaseAgent, configs


class AnalysisAgent(BaseAgent):
    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> dict[str, Any] | str:
        result = await Agent.broadcast(
            [SUMMARIZER_AGENT_ADDR, SENTIMENT_AGENT_ADDR], payload
        )
        return {
            "summary": result[0][1],
            "sentiment": result[1][1],
        }


if __name__ == "__main__":
    asyncio.run(
        AnalysisAgent().aserve(
            ANALYSIS_AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
