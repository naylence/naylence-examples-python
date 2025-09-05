import asyncio

from common import AGENT_ADDR
from naylence.fame.core import FameFabric, generate_id

from naylence.agent import (
    Agent,
    DataPart,
    TaskArtifactUpdateEvent,
    TaskStatusUpdateEvent,
    dev_mode,
    make_task_params,
)


async def main():
    async with FameFabric.create(root_config=dev_mode.CLIENT_CONFIG):
        agent = Agent.remote_by_address(AGENT_ADDR)
        task_id = generate_id()

        # fire off the task
        await agent.start_task(make_task_params(id=task_id))

        # subscribe to the stream
        updates = await agent.subscribe_to_task_updates(make_task_params(id=task_id))

        async for evt in updates:
            if isinstance(evt, TaskStatusUpdateEvent):
                print(f"[STATUS] {evt.status.state}")
            elif isinstance(evt, TaskArtifactUpdateEvent):
                part = evt.artifact.parts[0]
                assert isinstance(part, DataPart)
                print(f"[DATA ] {part.data['progress']}")


if __name__ == "__main__":
    asyncio.run(main())
