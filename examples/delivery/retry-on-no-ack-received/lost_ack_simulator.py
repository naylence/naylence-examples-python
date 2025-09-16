from naylence.fame.node.node_event_listener import NodeEventListener

from naylence.fame.node.node_like import NodeLike

from naylence.fame.core import (
    FameDeliveryContext,
    FameEnvelope,
    DeliveryAckFrame,
)


class LostAckSimulator(NodeEventListener):
    def __init__(self):
        super().__init__()
        self._delivery_ack_counter = 0

    async def on_forward_upstream(
        self,
        node: NodeLike,
        envelope: FameEnvelope,
        context: FameDeliveryContext | None = None,
    ) -> FameEnvelope | None:
        if isinstance(envelope.frame, DeliveryAckFrame):
            self._delivery_ack_counter += 1
            if 0 < self._delivery_ack_counter % 3 < 3:
                print(
                    "Simulating lost acknowledgment to envelope id",
                    envelope.frame.ref_id,
                )
                return None
        return envelope
