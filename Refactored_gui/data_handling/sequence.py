from dataclasses import dataclass, asdict

@dataclass
class Sequence:

    name: str
    frequency: int
    phase: int
    p1: int
    g1: int
    p2: int
    g2: int
    p3: int
    rec: int = 0
    

    def __post_init__(self) -> None:
        self.frequency = int(self.frequency)
        self.p1 = int(self.p1)
        self.g1 = int(self.g1)
        self.p2 = int(self.p2)
        self.g2 = int(self.g2)
        self.p3 = int(self.p3)
        self.rec = int(self.rec)

    def convert_to_dict(self) -> dict:
        return asdict(self)
