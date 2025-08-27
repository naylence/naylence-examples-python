import asyncio

from naylence.fame.core import FameFabric

from naylence.agent import (
    Agent,
    BaseAgent,
    Message,
    Task,
    TaskQueryParams,
    TaskSendParams,
    TaskState,
    make_task,
)


async def main():
    # --- Define an agent that supports background task execution ---
    class BackgroundTaskAgent(BaseAgent):
        """
        A minimal agent that handles long-running tasks by simulating
        work in the background. Task state can be queried at any time.
        """

        def __init__(self, *args):
            super().__init__(*args)
            self._tasks: dict[str, TaskState] = {}

        async def start_task(self, params: TaskSendParams) -> Task:
            """
            Starts a background task identified by `params.id`.
            Immediately returns a Task object with WORKING state.
            """
            self._tasks[params.id] = TaskState.WORKING
            asyncio.create_task(self._run_background_job(params.id))
            return make_task(id=params.id, state=TaskState.WORKING, payload={})

        async def _run_background_job(self, task_id: str):
            """
            Simulates long-running work by sleeping, then marks
            the task as completed.
            """
            await asyncio.sleep(0.1)
            self._tasks[task_id] = TaskState.COMPLETED

        async def get_task_status(self, params: TaskQueryParams) -> Task:
            """
            Returns the current state of a task by ID.
            If not found, returns UNKNOWN.
            """
            state = self._tasks.get(params.id, TaskState.UNKNOWN)
            return make_task(id=params.id, state=state, payload={})

    # --- Create a fabric instance (transport layer) ---
    async with FameFabric.create() as fabric:
        # Register the agent with the fabric and obtain its Fame address.
        # In real applications, this happens in a long-running agent process.
        agent_address = await fabric.serve(BackgroundTaskAgent("background-agent"))
        print(f"Agent address: {agent_address}")

        # In another process or component, resolve a proxy to the remote agent.
        # The `Agent.remote()` call returns a strongly-typed RPC proxy.
        remote = Agent.remote_by_address(agent_address)

        # Create a new task by calling `start_task` on the remote agent proxy.
        task_id = "my task #1"
        first_result = await remote.start_task(
            params=TaskSendParams(id=task_id, message=Message(role="agent", parts=[]))
        )
        print(f"Start task result: {first_result}")

        # Immediately query the task status.
        status_immediate = await remote.get_task_status(TaskQueryParams(id=task_id))
        print(f"Immediate status: {status_immediate}")
        assert status_immediate.status.state == TaskState.WORKING

        # Wait long enough for the background job to complete.
        await asyncio.sleep(0.2)

        # Query again — task should now be marked as COMPLETED.
        final_status = await remote.get_task_status(TaskQueryParams(id=task_id))
        print(f"Final status: {final_status}")
        assert final_status.status.state == TaskState.COMPLETED


if __name__ == "__main__":
    # Entrypoint for local execution.
    asyncio.run(main())
