import asyncio

from common import AGENT_ADDR

from naylence.agent import (
    Artifact,
    BackgroundTaskAgent,
    DataPart,
    TaskSendParams,
    TaskState,
    dev_mode,
)


class CancellableAgent(BackgroundTaskAgent):
    async def run_background_task(self, params: TaskSendParams) -> None:
        max_steps = 10
        for i in range(1, max_steps):
            task_state = await self.get_task_state(params.id)
            if task_state == TaskState.CANCELED:
                break
            progress = i / max_steps
            print(f"Task {params.id} progress changed to: {progress}")
            await self.update_task_artifact(
                params.id,
                Artifact(parts=[DataPart(data={"progress": progress})]),
            )
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(
        CancellableAgent().aserve(
            AGENT_ADDR, root_config=dev_mode.NODE_CONFIG, log_level="info"
        )
    )
