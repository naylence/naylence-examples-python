import asyncio

from naylence.fame.core import FameAddress, FameFabric

from naylence.agent import (
    Agent,
    BaseAgent,
    Task,
    TaskSendParams,
    TaskState,
    first_text_part,
    make_task,
    make_task_params,
)


async def main():
    # -----------------------------------------------------------------------------
    # 1. Define the "Pong" agent using start_task(), returning TextPart replies
    # -----------------------------------------------------------------------------
    class PongAgent(BaseAgent):
        """
        A PongAgent that implements the A2A start_task() method. Whenever it
        receives a TaskSendParams, it immediately returns a Task in COMPLETED state,
        echoing back the incoming text inside a TextPart under data["reply"].
        """

        async def start_task(self, params: TaskSendParams) -> Task:
            """
            RPC method start_task:
              • params.id       → unique task ID
              • params.message  → Message(role="agent", parts=[Part, ...])

            Behavior:
              1. Extract the incoming_text from params.message.parts[0].text
              2. Construct reply_text = f"Pong: {incoming_text}"
              3. Return a Task with
                    state=COMPLETED
                    data={"reply": TextPart(type="text", text=reply_text, metadata=None)}
            """
            # 1. Get the first TextPart from the incoming message
            incoming_text = first_text_part(params.message)

            # 2. Build the reply string
            reply_text = f"Pong: {incoming_text}"

            # 3. Wrap the reply in a TextPart and return a completed Task
            return make_task(
                id=params.id,
                state=TaskState.COMPLETED,
                payload=reply_text,
            )

    # -----------------------------------------------------------------------------
    # 2. Define the "Ping" agent using start_task(), forwarding TextPart
    # -----------------------------------------------------------------------------
    class PingAgent(BaseAgent):
        """
        A PingAgent that, upon receiving its own start_task() invocation,
        obtains a proxy to PongAgent and forwards the TaskSendParams unchanged.
        It then returns the Task that PongAgent produces.
        """

        def __init__(self, name: str, pong_address: FameAddress):
            """
            :param name:        Unique identifier for this PingAgent
            :param pong_address: Fame address string where PongAgent is served
            """
            super().__init__(name)
            self._pong_address = pong_address

        async def start_task(self, params: TaskSendParams) -> Task:
            """
            RPC method start_task:
              • params.id      → unique task ID
              • params.message → Message(role="agent", parts=[TextPart, ...])

            Behavior:
              1. Create a proxy to PongAgent via Agent.remote(self._pong_address).
              2. Call pong_proxy.start_task(params) and await its Task.
              3. Return that Task to the original caller.
            """
            # 1. Obtain a proxy to the remote PongAgent
            pong_proxy = Agent.remote_by_address(self._pong_address)

            # 2. Forward the same TaskSendParams (including TextPart) to PongAgent.start_task()
            pong_task: Task = await pong_proxy.start_task(params)

            # 3. Return PongAgent’s Task (with state and data fields)
            return pong_task

    # -----------------------------------------------------------------------------
    # 3. Spin up the FameFabric and serve both agents
    # -----------------------------------------------------------------------------
    async with FameFabric.create() as fabric:
        # 3a. Serve PongAgent first to get its address
        pong_address = await fabric.serve(PongAgent("pong-agent"))
        print(f"[main] PongAgent is listening at: {pong_address}")

        # 3b. Serve PingAgent, passing the PongAgent address so PingAgent can locate it
        ping_address = await fabric.serve(PingAgent("ping-agent", pong_address))
        print(f"[main] PingAgent is listening at: {ping_address}")

        # -----------------------------------------------------------------------------
        # 4. From "main", get a proxy to PingAgent and call start_task()
        # -----------------------------------------------------------------------------
        ping_proxy = Agent.remote_by_address(ping_address)

        # Build a TaskSendParams with:
        #  • id="task-123"
        #  • message=Message(role="agent", parts=[TextPart(...)])
        ping_params = make_task_params(id="task-123", payload="Hello, Pong!")

        # Invoke PingAgent.start_task(); PingAgent will forward
        # to PongAgent.start_task() and return PongAgent’s Task result
        result_task: Task = await ping_proxy.start_task(ping_params)

        # -----------------------------------------------------------------------------
        # 5. Inspect the returned Task object
        # -----------------------------------------------------------------------------
        print("[main] Received Task from PingAgent:")
        print(f"       id:    {result_task.id}")
        print(f"       state: {result_task.status.state}")

        assert result_task.status.message
        reply_part = first_text_part(result_task.status.message)
        print(f"       reply: {reply_part}")


if __name__ == "__main__":
    asyncio.run(main())
