from dataclasses import dataclass


@dataclass
class Packet:
    source_id: int | str
    target_id: int | str
    seq_num: int
    ttl: int
    path: list[int | str] | None = None
    thread_id: int | None = None
