from dataclasses import dataclass, asdict

@dataclass
class Sample:

    name: str
    mass: float


    def convert_to_dict(self) -> dict:
        return asdict(self)
