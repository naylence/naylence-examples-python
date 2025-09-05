import asyncio

from common import AGENT_ADDR
from naylence.fame.core import FameFabric, generate_id

from naylence.agent import Agent, dev_mode


async def main():
    async with FameFabric.create(root_config=dev_mode.NODE_CONFIG):
        agent = Agent.remote_by_address(AGENT_ADDR)

        conversation_id = generate_id()

        await agent.start_task(
            id=conversation_id,
            history_length=10,
            payload={"system_prompt": "You are a helpful assistant speaking Pirate"},
        )

        print("🔹 Chat (type 'exit' to quit)")
        loop = asyncio.get_event_loop()
        question = ""
        while True:
            text = await agent.run_turn(conversation_id, question)
            print(f"A> {text}\n")

            try:
                question = await loop.run_in_executor(None, input, "Q> ")
            except (EOFError, KeyboardInterrupt):
                print("\nGoodbye!")
                await agent.end_conversation(conversation_id)
                break

            if not (q := question.strip()) or q.lower() in ("exit", "quit"):
                await agent.end_conversation(conversation_id)
                break


if __name__ == "__main__":
    asyncio.run(main())
