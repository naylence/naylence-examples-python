import asyncio
from naylence.fame.sentinel import Sentinel


PEER_SENTINEL_CONFIG = {
    "node": {
        "type": "Sentinel",
        "peers": [{"direct_url": "${env:FAME_PEER_WS_URL}"}],
        "listeners": [
            {
                "type": "WebSocketListener",
                "port": "${env:FAME_SENTINEL_PORT:8000}",
            },
        ],
        "security": {"type": "SecurityProfile", "profile": "open"},
    },
}

if __name__ == "__main__":
    asyncio.run(Sentinel.aserve(root_config=PEER_SENTINEL_CONFIG, log_level="warning"))
