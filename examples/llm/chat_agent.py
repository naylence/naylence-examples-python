import asyncio
import os
from typing import Dict, List

from naylence.fame.core import FameFabric, generate_id
from openai import AsyncOpenAI

from naylence.agent import (
    Agent,
    BaseAgent,
    Task,
    TaskSendParams,
    TaskState,
    first_text_part,
    make_task,
)

# shared OpenAI client
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Set OPENAI_API_KEY first.")
client = AsyncOpenAI(api_key=openai_api_key)


class ChatAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        # history per sessionId
        self._histories: Dict[str, List[Dict[str, str]]] = {}

    async def start_task(self, params: TaskSendParams) -> Task:
        # identify conversation
        session = params.sessionId
        history = self._histories.setdefault(session, [])

        # pull out the user text
        user_msg = params.message.parts[0]
        text = getattr(user_msg, "text", "") or ""

        history.append({"role": "user", "content": text})

        # how many back-and-forths to keep?
        n = params.historyLength or 10
        messages = [{"role": "system", "content": "You are a helpful assistant."}]
        messages += history[-n:]

        # call the LLM
        resp = await client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,  # type: ignore
        )
        answer = resp.choices[0].message.content or ""

        history.append({"role": "assistant", "content": answer})
        # trim so we don’t grow unbounded
        self._histories[session] = history[-(n * 2) :]

        # return a Task with the same sessionId
        return make_task(
            id=params.id,
            session_id=session,
            state=TaskState.COMPLETED,
            payload=answer,
        )


async def main():
    # spin up Fame
    async with FameFabric.create() as fabric:
        agent_addr = await fabric.serve(ChatAgent())
        remote = Agent.remote_by_address(agent_addr)

        # fixed session for this REPL
        session_id = generate_id()

        print("🔹 Chat (type 'exit' to quit)")
        loop = asyncio.get_event_loop()
        while True:
            try:
                question = await loop.run_in_executor(None, input, "Q> ")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                break

            if not (q := question.strip()) or q.lower() in ("exit", "quit"):
                break

            # send via A2A start_task, supplying our session_id and historyLength=10
            task = await remote.start_task(
                id=generate_id(),
                payload=q,
                session_id=session_id,
                history_length=10,
            )

            # extract the assistant’s reply
            text = first_text_part(task.status.message)  # TextPart guaranteed
            print(f"A> {text}\n")


if __name__ == "__main__":
    asyncio.run(main())
