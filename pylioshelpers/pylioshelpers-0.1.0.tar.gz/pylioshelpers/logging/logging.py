import datetime, pprint

log_printer = pprint.PrettyPrinter(compact=False, width=40).pprint


def log(
    message: str,
    level: str = "",
    color: bool = True,
    datetime_format: str = "%Y-%m-%d %H:%M:%S",
):
    timestamp = datetime.datetime.now().strftime(datetime_format)

    level = level.lower()

    color_code = ""
    if color:
        if level == "" or level == "message":
            pass
        elif level == "ok" or level == "success":
            color_code = "\u001b[32;1m"
        elif level == "info":
            color_code = "\u001b[34;1m"
        elif level == "warn":
            color_code = "\u001b[33;1m"
        elif level == "error":
            color_code = "\u001b[31;1m"

    level = "(" + level.upper() + ") " if level != "" else ""

    if isinstance(message, str):
        print(
            "{color_code}[{timestamp}] {level}{message}{end_color}".format(
                color_code=color_code,
                timestamp=timestamp,
                level=level,
                message=message,
                end_color="\033[0m" if color else "",
            )
        )

    else:

        return_val = "{color_code}[{timestamp}] ---[ Printing {var_type} ]---\n".format(
            color_code=color_code, timestamp=timestamp, var_type=type(message)
        )
        return_val += pprint.pformat(message) + "\n"
        return_val += "[{timestamp}] ---[ End      {var_type} ]---{end_color}".format(
            timestamp=timestamp,
            var_type=type(message),
            end_color="\033[0m" if color else "",
        )
        print(return_val)
        return

    return