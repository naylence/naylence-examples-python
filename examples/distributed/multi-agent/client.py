import asyncio
import json

from common import ANALYSIS_AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import Agent, dev_mode

text_to_analyze = """
    I just watched the new sci-fi film “Galactic Frontier” and I have mixed feelings.
    The visuals were stunning and the world-building immersive, but the plot felt predictable
    and some characters lacked depth. Overall, it was an entertaining experience but not
    groundbreaking.
"""


async def main():
    async with FameFabric.create(root_config=dev_mode.CLIENT_CONFIG):
        agent = Agent.remote_by_address(ANALYSIS_AGENT_ADDR)
        result = await agent.run_task(payload=text_to_analyze)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
