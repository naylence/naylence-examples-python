import asyncio
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from common import AGENT_ADDR
from naylence.fame.service import operation

from naylence.agent import BaseAgent, configs


class RecordModel(BaseModel):
    value: str = Field(..., description="Stored value")
    created: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Record creation timestamp",
    )


class StorageAgent(BaseAgent):
    def __init__(self, name: str | None = None):
        super().__init__(name)
        self._store = None

    async def start(self):
        assert self.storage_provider
        self._store = await self.storage_provider.get_kv_store(
            RecordModel, namespace="storage_agent_namespace"
        )

    @operation
    async def store_value(self, key: str, value: str) -> RecordModel:
        assert self._store
        record = RecordModel(value=value)
        await self._store.set(key, record)
        return record

    @operation
    async def retrieve_value(self, key: str) -> RecordModel | None:
        assert self._store
        model = await self._store.get(key)
        if model is None:
            return None
        return model

    @operation(streaming=True)
    async def retrieve_all_values(self):
        assert self._store
        models = await self._store.list()
        for k, v in models.items():
            yield k, v


if __name__ == "__main__":
    asyncio.run(
        StorageAgent().aserve(
            AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="warning"
        )
    )
