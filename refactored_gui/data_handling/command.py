from dataclasses import dataclass

@dataclass
class Command:
    number_repeats: int


@dataclass
class NMRCommand(Command):
    command_type: str = "NMR"


@dataclass
class PPMSCommand(Command):
    command_type: str = "PPMS"
