import asyncio

from common import AGENT_ADDR
from naylence.fame.service import operation

from naylence.agent import BaseAgent, BaseAgentState, configs


class CustomAgentState(BaseAgentState):
    value: str | None = None


class PersistentAgent(BaseAgent[CustomAgentState]):
    @operation
    async def store_value(self, value: str) -> CustomAgentState:
        async with self.state as state:
            state.value = value
            return state

    @operation
    async def retrieve_value(self) -> CustomAgentState | None:
        async with self.state as state:
            return state


if __name__ == "__main__":
    asyncio.run(
        PersistentAgent().aserve(
            AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="warning"
        )
    )
