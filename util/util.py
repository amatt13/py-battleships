from enum import Enum
import sys
import pickle


class RequestType(Enum):
    joined_game = 0
    send_map = 1
    start_turn = 2
    hit = 3
    miss = 4
    msg = 5
    send_coord = 6
    username_taken = 7
    map_size_error = 8


def create_message(request_type: int, message):
    if request_type < 0:
        print("Invalid request type: " + str(request_type))
        sys.exit()
    elif message.__len__() == 0:
        print("Empty message")
        sys.exit()
    if type(message) is dict: # message is dict
        return sys.getsizeof(pickle.dumps(message)), pickle.dumps(message)
    return sys.getsizeof(pickle.dumps(str(request_type) + "#" + message)), pickle.dumps(str(request_type) + "#" + message)


def read_player_info_package(package):  # (request_type, #dict)
    player_info = pickle.loads(package)
    return player_info

def read_package(package):
    request_type = read_request_type(package)
    message = read_message(package)
    return {'rt': int(request_type), 'msg': message}


def read_message(package):
    opened_message = pickle.loads(package)
    split = opened_message.split('#')
    message = split[1]
    return message


def read_request_type(package):
    opened_message = pickle.loads(package)
    split = opened_message.split('#')
    request_type = int(split[0])
    return request_type
