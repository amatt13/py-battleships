import socket
import numpy
from enum import  Enum
import pickle
from urllib import request
import time

from pip._vendor.distlib.compat import raw_input

my_ip = request.urlopen('http://ip.42.pl/raw').read()
connections = list()


class RequestType(Enum):
    req_map = 0
    send_map = 1
    other = 2


def check_for_hit(coordinate: str, map):
    split_coordinate = coordinate.split(' ')
    x = int(split_coordinate[1]) - 1
    y = (ord(str(split_coordinate[0]))-96) - 1
    if map[y][x] > 0.1:
        print("Player hit!")
        map[y][x] = 0.0
        return True
    else:
        print("Player missed!")
        return False


if __name__ == '__main__':
    #x = raw_input('What is your name?')

    port = 10000
    buf = 4096

    # Create socket and bind to address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((socket.gethostname(), port))
    # s.listen(5)
    # Receive messages
    player_count = 0
    while player_count != 2:
        data, addr = s.recvfrom(buf)
        L = pickle.loads(data)
        if not data:
            print("Client has exited!")
            break
        else:
            player_count += 1
            player = {'addr': addr, 'map': L, 'player_id': player_count}
            if player not in connections:  # TODO: make sure that the same player can't connect twice
                connections.append(player)
                print("added")
                s.sendto(pickle.dumps(player_count), addr)
    print("Two players are now connected")
    for players in connections:
        print(players.get("addr")[0])

    game_in_progress = True
    turn = 1
    while game_in_progress:
        if turn % 2 == 0:
            current_player = connections[0]
            waiting_player = connections[1]
        else:
            current_player = connections[1]
            waiting_player = connections[0]

        s.sendto(pickle.dumps("Your turn\nEnter coordinate to bomb:"), current_player.get('addr'))
        #s.sendto(pickle.dumps("Opponents turn"), waiting_player.get('addr'))
        package = s.recvfrom(buf)
        coordinate = pickle.loads(package[0])
        while check_for_hit(coordinate, waiting_player.get('map')):  # break when player miss
            s.sendto(pickle.dumps("Hit at : " + coordinate + "\nEnter new coordinate:"), current_player.get('addr'))
            package = s.recvfrom(buf)
            coordinate = pickle.loads(package[0])
        else:
            turn += 1


    # Close socket
    s.close()

