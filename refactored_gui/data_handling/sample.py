from dataclasses import dataclass, asdict


@dataclass
class Sample:

    name: str
    mass: str | float
    shape: str

    def __post_init__(self) -> None:
        """
        Checks whether user input is valid. A non-empty string must be provided for 'name'. A float must be provided for
        mass.
        :return:
        """

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
        """
        Convenience method for returning fields as a dictionary.
        :return: dict
        """
        return asdict(self)
