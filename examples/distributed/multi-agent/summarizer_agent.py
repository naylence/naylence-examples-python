import asyncio
from typing import Any

from common import SUMMARIZER_AGENT_ADDR, get_model_name, get_openai_client

from naylence.agent import BaseAgent, configs


client = get_openai_client()


class SummarizerAgent(BaseAgent):
    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> dict[str, Any] | str:
        response = await client.chat.completions.create(
            model=get_model_name(),
            messages=[{"role": "user", "content": f"Summarize this:\n\n{payload}"}],
        )
        return response.choices[0].message.content.strip()  # type: ignore


if __name__ == "__main__":
    asyncio.run(
        SummarizerAgent().aserve(
            SUMMARIZER_AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="info"
        )
    )
