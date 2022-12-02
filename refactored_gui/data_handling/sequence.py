from dataclasses import dataclass, asdict, fields
import numpy as np

@dataclass
class Sequence:

    name: str
    frequency: int
    TX_phase: int
    RX_phase: int
    p1: int
    g1: int
    p2: int
    g2: int
    p3: int
    rec: int = 0

    def __post_init__(self) -> None:
        self.valid_sequence = 1
        # Convert fields to int
        self.convert_to_int()
        # Format data for saving
        self.formatted_data = np.array([val for val in self.convert_to_dict().values() if isinstance(val, int)], dtype=int)

    # noinspection PyTypeChecker
    def save_to_file(self, save_path: str) -> None:

        np.savetxt(save_path, self.formatted_data, delimiter="\n")
        print(f"Sequence saved to {save_path}")

    def convert_to_dict(self) -> dict:
        return asdict(self)

    def convert_to_int(self) -> None:

        # Convert all values to int except name if not Nont
        for field in fields(self):
            if issubclass(field.type, int):
                value = getattr(self, field.name)
                try:
                    setattr(self, field.name, int(value))
                except ValueError as ex:
                    print(ex)
                    print(f"{field.name} is empty!")
                    self.valid_sequence = 0