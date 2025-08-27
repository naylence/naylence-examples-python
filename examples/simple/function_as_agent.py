import asyncio
from datetime import datetime, timezone
from typing import Any

from naylence.fame.core import FameFabric

from naylence.agent import Agent


async def main():
    async with FameFabric.create() as fabric:

        async def time_agent(payload: Any, id: Any) -> Any:
            return datetime.now(timezone.utc).isoformat()

        agent_address = await fabric.serve(Agent.from_handler(time_agent))
        remote = Agent.remote_by_address(agent_address)

        result = await remote.run_task(payload="Hello")
        print(f"Time: {result}")


if __name__ == "__main__":
    asyncio.run(main())
