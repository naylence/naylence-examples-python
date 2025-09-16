from __future__ import annotations

import asyncio
from common import AGENT_ADDR

from naylence.fame.core import FameFabric, generate_id

from naylence.agent import (
    Agent,
    DataPart,
    TaskArtifactUpdateEvent,
    TaskIdParams,
    TaskStatusUpdateEvent,
    make_task_params,
)
from naylence.agent.configs import CLIENT_CONFIG


async def main():
    async with FameFabric.create(root_config=CLIENT_CONFIG):
        agent = Agent.remote_by_address(AGENT_ADDR)
        task_id = generate_id()

        await agent.start_task(make_task_params(id=task_id))

        updates = await agent.subscribe_to_task_updates(make_task_params(id=task_id))

        async for evt in updates:
            if isinstance(evt, TaskStatusUpdateEvent):
                print(f"[STATUS] {evt.status.state}")
            elif isinstance(evt, TaskArtifactUpdateEvent):
                part = evt.artifact.parts[0]
                assert isinstance(part, DataPart)
                progress = part.data["progress"]
                print(f"[DATA ] progress: {progress}")
                if progress >= 0.5:
                    print(f"Canceling task {task_id}")
                    await agent.cancel_task(TaskIdParams(id=task_id))


if __name__ == "__main__":
    asyncio.run(main())
