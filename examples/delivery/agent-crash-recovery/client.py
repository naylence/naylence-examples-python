import asyncio

from common import AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import dev_mode
from naylence.fame.util.logging import enable_logging

enable_logging(log_level="warning")


async def main():
    async with FameFabric.create(root_config=dev_mode.CLIENT_CONFIG) as fabric:
        print("Sending message to MessageAgent...")
        ack_frame = await fabric.send_message(AGENT_ADDR, "Hello, World!")
        print("Acknowledgment received:", ack_frame)


if __name__ == "__main__":
    asyncio.run(main())
