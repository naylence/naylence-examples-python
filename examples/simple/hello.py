import asyncio
from typing import Any

from naylence.fame.core import FameFabric
from naylence.agent import BaseAgent
from naylence.fame.util.logging import enable_logging

enable_logging(log_level="warning")


class HelloAgent(BaseAgent):

    async def on_message(self, message: Any) -> Any:
        print(f"Agent received message: {message}")


async def main():
    # --- Start a FameFabric session and serve the agent ---
    async with FameFabric.create() as fabric:
        agent_address = await fabric.serve(HelloAgent())
        await fabric.send_message(agent_address, "Hello, World")


# Entry point for running this script directly.
if __name__ == "__main__":
    asyncio.run(main())
