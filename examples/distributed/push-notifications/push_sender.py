import asyncio

from common import SENDER_AGENT_ADDR
from naylence.fame.core import FameFabric

from naylence.agent import (
    BackgroundTaskAgent,
    TaskPushNotificationConfig,
    TaskSendParams,
    dev_mode,
)


class PushSender(BackgroundTaskAgent):
    def __init__(self):
        super().__init__()
        self._push_notification_configs: dict[str, TaskPushNotificationConfig] = {}

    async def run_background_task(self, params: TaskSendParams):
        print(f"{self.__class__.__name__} running task {params.id}")
        fabric = FameFabric.current()
        config = self._push_notification_configs.get(params.id)
        for i in range(1, 10):
            if config:
                notification = {"task_id": params.id, "message": f"Notification #{i}"}
                await fabric.send_message(
                    config.pushNotificationConfig.url,
                    notification,
                )
                print(f"{self.__class__.__name__} sent notification {notification}")
            await asyncio.sleep(0.2)
        print(f"{self.__class__.__name__} completed task {params.id}")

    async def register_push_endpoint(
        self, config: TaskPushNotificationConfig
    ) -> TaskPushNotificationConfig:
        print(f"Configured push notification endpoint {config} for task {config.id}")
        self._push_notification_configs[config.id] = config
        return config


if __name__ == "__main__":
    asyncio.run(
        PushSender().aserve(
            address=SENDER_AGENT_ADDR,
            root_config=dev_mode.NODE_CONFIG,
            log_level="info",
        )
    )
