import asyncio
from naylence.fame.sentinel import Sentinel
from naylence.agent import dev_mode


if __name__ == "__main__":
    asyncio.run(Sentinel.aserve(root_config=dev_mode.SENTINEL_CONFIG, log_level="info"))
