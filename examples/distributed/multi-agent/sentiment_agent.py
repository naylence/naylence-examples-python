import asyncio
from typing import Any

from common import SENTIMENT_AGENT_ADDR, get_model_name, get_openai_client

from naylence.agent import BaseAgent, dev_mode

client = get_openai_client()


class SentimentAgent(BaseAgent):
    async def run_task(
        self,
        payload: dict[str, Any] | str | None,
        id: str | None,
    ) -> dict[str, Any] | str:
        response = await client.chat.completions.create(
            model=get_model_name(),
            messages=[
                {
                    "role": "user",
                    "content": f"Rate the sentiment of this on a scale 1-5 (number only):\n\n{payload}",
                }
            ],
        )
        return response.choices[0].message.content.strip()  # type: ignore


if __name__ == "__main__":
    asyncio.run(
        SentimentAgent().aserve(
            SENTIMENT_AGENT_ADDR, root_config=dev_mode.NODE_CONFIG, log_level="info"
        )
    )
