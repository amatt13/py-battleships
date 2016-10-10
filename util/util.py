from enum import Enum
import sys
import pickle


class RequestType(Enum):
    req_map = 0
    send_map = 1
    start_turn = 2
    hit = 3
    miss = 4
    msg = 5
    send_coord = 6


def create_message(request_type: int, message):
    if not isinstance(message, str):
        message = str(message)
    if request_type < 0:
        print("Invalid request type: " + str(request_type))
        sys.exit()
    elif message.__len__() == 0:
        print("Empty message")
        sys.exit()
    return pickle.dumps(str(request_type) + "#" + message)


def read_message(package):
    if not isinstance(package, bytes):
        package = package[0]
    msg = pickle.loads(package)
    split = msg.split('#')
    split[0] = int(split[0])
    return split

