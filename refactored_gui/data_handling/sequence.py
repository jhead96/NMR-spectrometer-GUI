from dataclasses import dataclass, asdict, fields
import numpy as np


@dataclass
class Sequence:

    frequency: int
    TX_phase: int
    RX_phase: int
    p1: int
    g1: int
    p2: int
    g2: int
    p3: int
    rec: int = 0
    name: str = ""

    def __post_init__(self) -> None:
        """
        Converts data into format for saving.
        :return:
        """
        self.valid_sequence = 1
        # Convert fields to int
        self.convert_to_int()
        # Format data for saving
        self.formatted_data = np.array([val for val in self.convert_to_dict().values() if isinstance(val, int)], dtype=int)

    # noinspection PyTypeChecker
    def save_to_file(self, save_path: str) -> None:
        """
        Convenience method to save class fields to the specified file.
        :param save_path: File path to save to.
        :return:
        """

        np.savetxt(save_path, self.formatted_data, delimiter="\n")
        print(f"Sequence saved to {save_path}")

    def convert_to_dict(self) -> dict:
        """
        Convenience method for returning fields as a dictionary.
        :return: dict
        """
        return asdict(self)

    def convert_to_int(self) -> None:
        """
        Converts all valid fields to int.
        :return:
        """

        # Convert all values to int except name if not None
        for field in fields(self):
            if issubclass(field.type, int):
                value = getattr(self, field.name)
                try:
                    setattr(self, field.name, int(value))
                except ValueError as ex:
                    print(ex)
                    print(f"{field.name} is empty!")
                    self.valid_sequence = 0

    def set_name(self, name: str) -> None:
        self.name = name

    def get_name(self) -> str:
        return self.name
