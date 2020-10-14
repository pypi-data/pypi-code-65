import socket


def is_someone_listening(location: str) -> bool:
    tokens = location.split(":")
    host_address = tokens[0]
    port = int(tokens[1])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as a_socket:
        host_location = (host_address, port)
        try:
            result_of_check = a_socket.connect_ex(host_location)

            return result_of_check == 0
        except Exception:
            return False
