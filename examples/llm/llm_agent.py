import asyncio
import os
from typing import Any

from naylence.fame.core import FameFabric
from openai import AsyncOpenAI

from naylence.agent import Agent


# ----------------------------------------------------------------------------
# 1) Create a shared AsyncOpenAI client (reuse across calls).
# ----------------------------------------------------------------------------
# Make sure your OPENAI_API_KEY is set in env, e.g.:
#   export OPENAI_API_KEY="sk-…"
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    raise RuntimeError("Set OPENAI_API_KEY in your environment first.")
client = AsyncOpenAI(api_key=openai_api_key)


# ----------------------------------------------------------------------------
# 2) Define an async handler that uses AsyncOpenAI for Q&A.
# ----------------------------------------------------------------------------
async def qa_agent(payload: Any, id: Any) -> Any:
    """
    payload:    the question string
    id:         the task ID (unused here, but could be logged)
    Returns:    the model's answer (string)

    Uses AsyncOpenAI to send a ChatCompletion request.
    """
    # Build a minimal “system + user” chat prompt
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": str(payload)},
    ]
    # Call AsyncOpenAI’s chat.completions.create(...)
    response = await client.chat.completions.create(
        model="gpt-5-mini",
        messages=messages,  # type: ignore
    )
    # Extract the assistant’s reply text
    return response.choices[0].message.content


# ----------------------------------------------------------------------------
# 3) Spin up FameFabric, serve our function‐agent, and invoke it remotely.
# ----------------------------------------------------------------------------
async def main():
    async with FameFabric.create() as fabric:
        # Wrap qa_agent into a BaseAgent subclass on the fly
        agent_address = await fabric.serve(Agent.from_handler(qa_agent))
        remote = Agent.remote_by_address(agent_address)

        # Ask a question via the proxy’s run_task()
        question = "What year did the first moon landing occur?"
        answer = await remote.run_task(payload=question)
        print(f"Q: {question}\nA: {answer}")


if __name__ == "__main__":
    asyncio.run(main())
