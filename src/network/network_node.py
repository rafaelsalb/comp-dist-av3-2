from graph import Node
from network.packet import Packet


class NetworkNode(Node):
    seen_messages: set[tuple[int | str, str]]
    neighbors: dict[str, list[Node]]

    def __init__(self, id: str, resources: set[str]):
        super().__init__(id)
        self.seen_packets: set[int] = set()
        self.resources = resources
        self.seen_messages = set()

    def set_neighbors(self, neighbors: dict[str, list[Node]]):
        self.neighbors = neighbors

    def has_resource(self, resource: str) -> bool:
        return resource in self.resources

    def receive_flood(self, packet: Packet, node_id: str, stats: dict) -> bool:
        stats['total_messages'] += 1

        msg_signature = (packet.source_id, node_id)
        if msg_signature in self.seen_messages:
            return False  # Message already seen
        self.seen_messages.add(msg_signature)

        if packet.target_resource in self.resources:
            return True

        if packet.ttl <= 0:
            return False

        packet.ttl -= 1
        current_path = packet.path + [self.id] if packet.path else [self.id]

        # explorar vizinhos
        found_somewhere = False
        for neighbor in self.neighbors:
            if neighbor.id != node_id:
                new_packet = Packet(
                    source_id=packet.source_id,
                    target_id=packet.target_id,
                    seq_num=packet.seq_num,
                    content=packet.content,
                    ttl=packet.ttl,
                    path=current_path.copy()
                )

                if neighbor.receive_flood(new_packet, self.id, stats):
                    found_somewhere = True

        if found_somewhere:
            packet.path = current_path
            self.send_packet(packet)
        return found_somewhere
