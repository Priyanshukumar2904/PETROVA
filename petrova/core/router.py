from petrova.commands.help import help_command
from petrova.commands.version import version_command
from petrova.commands.about import about_command
from petrova.commands.clear import clear_command
from petrova.commands.exit import exit_command
from petrova.commands.server import status_command


def route_command(command: str):
    command = command.lower().strip()

    routes = {
        "help": help_command,
        "version": version_command,
        "about": about_command,
        "clear": clear_command,
        "exit": exit_command,
        "status": status_command,
    }

    handler = routes.get(command)

    if handler:
        return handler()

    return False