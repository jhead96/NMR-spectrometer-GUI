from data_handling.sequence import Sequence
from dataclasses import dataclass, field
import numpy as np


@dataclass
class NMRCommand:

    sequence_filepath: str
    repeats: int
    command_type: str = "NMR"

    def __post_init__(self):
        """
        Loads sequence associated with NMRCommand.
        :return:
        """

        # Load sequence associated wth command
        self.sequence = Sequence(*np.loadtxt(self.sequence_filepath, dtype=int))

        # Check validity
        if self.repeats <= 0:
            self.valid_command = 0
        else:
            self.valid_command = 1

    def set_repeats(self, repeats: int) -> None:
        """
        Sets repeats to the value specified.
        :param repeats: New value of repeats.
        :return:
        """
        self.repeats = repeats


@dataclass
class PPMSCommand:

    set_value: float
    rate: float
    value_limits: list[int] | None = None
    rate_limits: list[int] | None = None
    variable_type: str | None = None
    unit: str | None = None
    command_lbl: str | None = None

    def __post_init__(self) -> None:
        """
        Generates string label to describe command using values provided at object instantiation.
        :return:
        """
        self.generate_label()

    def edit_set_value(self, value: float) -> None:
        """
        Sets 'value' to the provided value.
        :param value: New value of 'value'.
        :return:
        """

        if self.value_limits[0] <= value <= self.value_limits[1]:
            self.set_value = value
            self.generate_label()
        else:
            print(f"Invalid value must be in range "
                  f"{self.value_limits[0]}{self.unit} - {self.value_limits[1]}{self.unit}")

    def set_rate(self, rate: float) -> None:
        """
        Sets 'rate' to the provided rate.
        :param rate: New value of 'rate'.
        :return:
        """
        if self.rate_limits[0] <= rate <= self.rate_limits[1]:
            self.rate = rate
            self.generate_label()
        else:
            print(f"Invalid value must be in range "
                  f"{self.rate_limits[0]}{self.unit}/s - {self.rate_limits[1]}{self.unit}/s")

    def generate_label(self) -> None:
        """
        Generates a new command label. Needs to be called if any instance variables are changed.
        :return:
        """
        self.command_lbl = f"Set {self.variable_type}={self.set_value}{self.unit}\nRate={self.rate}{self.unit}/s"


@dataclass
class PPMSTemperatureCommand(PPMSCommand):

    command_type: str = "PPMS-Temp"
    unit: str = "K"
    variable_type: str = "T"
    value_limits: list[int] = field(default_factory=lambda: [2, 400])
    rate_limits: list[int] = field(default_factory=lambda: [2, 20])


@dataclass
class PPMSFieldCommand(PPMSCommand):

    command_type: str = "PPMS-Field"
    unit: str = "Oe"
    variable_type: str = "B"
    value_limits: list[int] = field(default_factory=lambda: [-70000, 70000])
    rate_limits: list[int] = field(default_factory=lambda: [10, 500])
