import asyncio
from naylence.fame.sentinel import Sentinel
from naylence.agent import configs


if __name__ == "__main__":
    asyncio.run(
        Sentinel.aserve(root_config=configs.SENTINEL_CONFIG, log_level="info")
    )

