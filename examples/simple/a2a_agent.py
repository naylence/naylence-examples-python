import asyncio

from naylence.fame.core import FameFabric

from naylence.agent import (
    Agent,
    BaseAgent,
    Message,
    Task,
    TaskSendParams,
    TaskState,
    make_task,
)


async def main():
    # --- Define a minimal agent with a single RPC method ---
    class SimpleA2AAgent(BaseAgent):
        """
        A trivial agent that immediately returns a completed task
        with a hardcoded result. Used for basic testing and SDK demos.
        """

        async def start_task(self, params: TaskSendParams) -> Task:
            """
            Simulates task handling by returning a COMPLETED task instantly.
            """
            return make_task(
                id=params.id,
                state=TaskState.COMPLETED,
                payload={"result": "Hello!"},
            )

    # --- Start a FameFabric transport layer and serve the agent ---
    async with FameFabric.create() as fabric:
        # Register the SimpleAgent with the fabric and get its address.
        # In real deployments, this would happen in the agent runtime process.
        agent_address = await fabric.serve(SimpleA2AAgent("simple-agent"))
        print(f"Agent address: {agent_address}")

        # Resolve a remote proxy to the agent.
        # This simulates a client or external caller invoking the agent.
        remote = Agent.remote_by_address(agent_address)

        # Send a new task to the remote agent using its JSON-RPC method.
        # This call is fully typed and asynchronous.
        result = await remote.start_task(
            params=TaskSendParams(
                id="my task #1",
                message=Message(role="agent", parts=[]),  # empty message payload
            )
        )

        print(f"Result: {result}")
        assert result.status.state == TaskState.COMPLETED


# Entry point for running this script directly.
if __name__ == "__main__":
    asyncio.run(main())
