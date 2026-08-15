from petrova.core.server import server_status


def status_command():
    print()
    print(server_status())
    print()
    return True