import socket
import numpy
import pickle
from util.util import RequestType as RT, create_message, read_message
from urllib import request

my_ip = request.urlopen('http://ip.42.pl/raw').read()
connections = list()


def check_for_hit(coordinate: str, map: numpy.ndarray, username: str):
    split_coordinate = coordinate.split(' ')
    x = int(split_coordinate[1]) - 1
    y = (ord(str(split_coordinate[0]))-96) - 1
    if map[y][x] > 0.1:
        print("%s hit!" % username)
        map[y][x] = 0.0
        return True
    else:
        print("%s missed!" % username)
        return False


if __name__ == '__main__':
    #x = raw_input('What is your name?')

    port = 21
    buf = 4096
    print(socket.gethostname())
    # Create socket and bind to address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((socket.gethostname(), port))
    # s.listen(5)
    # Receive messages
    player_count = 0
    while player_count != 2:
        data, addr = s.recvfrom(buf)
        L = pickle.loads(data)  #TODO convert read_message such that it can be used here
        if not data:
            print("Client has exited!")
            break
        else:
            player_count += 1
            player = {'addr': addr, 'player_id': player_count, 'map': L[0], 'map_size': L[1], 'username': L[2]}
            if player not in connections:  # TODO: make sure that the same player can't connect twice
                connections.append(player)
                print("added")
                s.sendto(create_message(RT.msg.value, player_count), addr)
    print("Two players are now connected")
    for players in connections:
        print(players.get("addr")[0])

    game_in_progress = True
    turn = 1
    while game_in_progress:
        print("Turn: %d" % turn)
        if turn % 2 == 0:
            current_player = connections[0]
            waiting_player = connections[1]
        else:
            current_player = connections[1]
            waiting_player = connections[0]

        s.sendto(create_message(RT.start_turn.value, "Your turn\nEnter coordinate to bomb:"), current_player.get('addr'))
        s.sendto((create_message(RT.msg.value, "Opponent %s turn" % current_player.get('username'))), waiting_player.get('addr'))
        coordinate = read_message(s.recvfrom(buf)[0])
        while check_for_hit(coordinate[1], waiting_player.get('map'), current_player.get('username')):  # break when player miss
            s.sendto(create_message(RT.hit.value, "Hit at: " + coordinate[1] + "\nEnter new coordinate:"), current_player.get('addr'))
            coordinate = read_message(s.recvfrom(buf))
        else:
            s.sendto(create_message(RT.miss.value, "Miss!\nIt is now the opponents turn"), current_player.get('addr'))
            turn += 1


    # Close socket
    s.close()

