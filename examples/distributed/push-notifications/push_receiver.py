import asyncio
from typing import Any

from common import RECEIVER_AGENT_ADDR, SENDER_AGENT_ADDR
from naylence.fame.core import generate_id

from naylence.agent import (
    Agent,
    BackgroundTaskAgent,
    PushNotificationConfig,
    TaskPushNotificationConfig,
    TaskSendParams,
    dev_mode,
)


class PushReceiver(BackgroundTaskAgent):
    def __init__(self):
        super().__init__()
        self._notifications_per_task: dict[str, list] = {}

    async def run_background_task(self, params: TaskSendParams) -> Any:
        agent = Agent.remote_by_address(SENDER_AGENT_ADDR)
        task_id = generate_id()
        self._notifications_per_task[task_id] = []
        # Configure push notifications BEFORE starting the task
        await agent.register_push_endpoint(
            TaskPushNotificationConfig(
                id=task_id,
                pushNotificationConfig=PushNotificationConfig(url=RECEIVER_AGENT_ADDR),
            )
        )
        await agent.run_task(id=task_id)
        return {"notifications": self._notifications_per_task[task_id]}

    async def on_message(self, message: dict):
        print(f"{self.__class__.__name__} got notification: {message}")
        task_id = message["task_id"]
        notifications = self._notifications_per_task[task_id]
        notifications.append(message["message"])


if __name__ == "__main__":
    asyncio.run(
        PushReceiver().aserve(
            address=RECEIVER_AGENT_ADDR,
            root_config=dev_mode.NODE_CONFIG,
            log_level="info",
        )
    )
