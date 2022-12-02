from dataclasses import dataclass, asdict
from typing import Union

@dataclass
class Sample:

    name: str
    mass: Union[str, float]
    shape: str

    def __post_init__(self) -> None:

        self.valid_mass = 1
        self.valid_name = 1

        # Convert mass to float
        try:
            float(self.mass)
        except ValueError as ex:
            print(ex)
            self.valid_mass = 0

        # Check for empty name
        if self.name == "":
            self.valid_name = 0

    def convert_to_dict(self) -> dict:
        return asdict(self)
