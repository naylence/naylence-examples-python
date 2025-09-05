import asyncio
from typing import Dict, List

from openai import BaseModel
from pydantic import Field

from common import AGENT_ADDR, get_openai_client, get_model_name

from naylence.fame.service import operation
from naylence.agent import (
    BaseAgent,
    Task,
    TaskSendParams,
    TaskState,
    dev_mode,
    make_task,
    first_data_part,
)
from naylence.fame.util import logging

logger = logging.getLogger(__name__)


client = get_openai_client()


class ConversationState(BaseModel):
    system_prompt: str
    history: List[Dict[str, str]] = Field(default_factory=list)
    max_history_length: int = 10


class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self._states: Dict[str, ConversationState] = {}

    async def start_task(self, params: TaskSendParams) -> Task:
        if params.id in self._states:
            raise ValueError(f"Duplicate task: {params.id}")

        self._states[params.id] = ConversationState.model_validate(
            first_data_part(params.message)
        )

        logger.info("started_conversation", task_id=params.id)

        return make_task(id=params.id, state=TaskState.WORKING, payload="")

    @operation
    async def run_turn(self, task_id: str, user_message: str) -> str:
        state = self._states.get(task_id)
        if not state:
            raise ValueError(f"Invalid task: {task_id}")

        state.history.append({"role": "user", "content": user_message})

        # how many back-and-forths to keep?
        n = state.max_history_length or 10
        messages = [{"role": "system", "content": state.system_prompt}]
        messages += state.history[-n:]

        # call the LLM
        resp = await client.chat.completions.create(
            model=get_model_name(),
            messages=messages,  # type: ignore
        )

        answer = resp.choices[0].message.content or ""

        state.history.append({"role": "assistant", "content": answer})
        # trim so we don’t grow unbounded
        state.history = state.history[-(n * 2) :]

        return answer

    @operation
    async def end_conversation(self, task_id: str):
        self._states.pop(task_id, None)
        logger.info("finished_conversation", task_id=task_id)


if __name__ == "__main__":
    asyncio.run(
        ChatAgent().aserve(
            AGENT_ADDR, root_config=dev_mode.NODE_CONFIG, log_level="info"
        )
    )
