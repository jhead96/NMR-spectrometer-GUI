from data_handling.command import Command

class ExperimentScheduler:

    def __init__(self):
        self.command_list = []

    def delete_command(self, index) -> None:
        pass

    def add_command(self, command_type: str, command_lbl: str, number_repeats: int) -> None:

        new_command = Command(command_type, command_lbl, number_repeats)
        self.command_list.append(new_command)

    def get_command_list(self) -> list[Command]:
        return self.command_list
