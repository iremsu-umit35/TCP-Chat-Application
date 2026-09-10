SEPARATOR = "|"


def create_message(message_type, content=""):
    return f"{message_type}{SEPARATOR}{content}"


def parse_message(message):
    parts = message.split(SEPARATOR, 1)

    message_type = parts[0]

    if len(parts) > 1:
        content = parts[1]
    else:
        content = ""

    return message_type, content