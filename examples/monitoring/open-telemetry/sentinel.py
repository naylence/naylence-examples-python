import asyncio
from naylence.fame.sentinel import Sentinel


if __name__ == "__main__":
    asyncio.run(Sentinel.aserve(log_level="warning"))
