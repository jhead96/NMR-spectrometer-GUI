from data_handling.command import NMRCommand, PPMSCommand
from typing import Union

class ExperimentManager:


    def __init__(self) -> None:
        self.command_list = []

    def delete_command(self, index: int) -> None:
        """
        Deletes a command from the command list.
        :param index: Index of command to be deleted.
        :return:
        """
        del self.command_list[index]

    def add_command(self, command: NMRCommand | PPMSCommand) -> None:
        """
        Appends a command to the command list.
        :param command: Command to be appended.
        :return:
        """
        self.command_list.append(command)

    def get_command_list(self) -> list[NMRCommand | PPMSCommand]:
        """
        Returns the command list.
        :return: command list object
        """
        return self.command_list

    def get_command(self, index: int) -> NMRCommand | PPMSCommand:
        """
        Gets the command from the command list at the specified index.
        :param index: Index of command to be returned.
        :return: command
        """
        return self.command_list[index]

    def get_command_type(self, index: int) -> type:
        """
        Returns the type of the command at the given index.
        :param index: Index of command type to be returned.
        :return: type of command
        """
        return type(self.command_list[index])

    def edit_command(self, index: int, repeats: None | int = None,
                     value: None | int = None, rate: None | int = None) -> None:
        """
        Edits the parameters of the command specified by the index.
        :param index: Index of command to be edited.
        :param repeats: If specified, sets the 'repeats' field of the selected command. Only works for NMRCommand.
        :param value: If specified, sets the 'value' field of the selected command. Only works for PPMSCommand.
        :param rate: If specified, sets the 'rate' field of the selected command. Only works for PPMSCommand.
        :return:
        """

        selected_command = self.command_list[index]

        if repeats:
            selected_command.set_repeats(repeats)
        if value:
            selected_command.edit_set_value(value)
        if rate:
            selected_command.set_rate(rate)



