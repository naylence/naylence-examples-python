import asyncio

from common import AGENT_ADDR

from naylence.agent import (
    Artifact,
    BackgroundTaskAgent,
    DataPart,
    TaskSendParams,
    configs,
)


class StatusAgent(BackgroundTaskAgent):
    async def run_background_task(self, params: TaskSendParams):
        # simulate 5 steps of work with progress messages
        for i in range(1, 6):
            await asyncio.sleep(0.5)
            await self.update_task_artifact(
                params.id,
                Artifact(parts=[DataPart(data={"progress": f"step {i}/5 complete"})]),
            )


if __name__ == "__main__":
    asyncio.run(
        StatusAgent().aserve(
            AGENT_ADDR, root_config=configs.NODE_CONFIG, log_level="warning"
        )
    )
