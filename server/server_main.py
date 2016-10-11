import socket
import numpy
from util.util import RequestType as RT, create_message, read_message as rm, read_request_type as rt, read_package as rp, read_player_info_package as rpip

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


def accept_player(plyer_info: dict, player_count: int):
    connections.append(player)
    s.sendto(create_message(RT.joined_game.value, str(player_count)), plyer_info.get('addr'))  # Inform player of succ conn and player ID
    print("Added player " + player.get('username'))
    return player_count + 1


def recv_basic(the_socket):
    total_data = []
    print("entered")
    the_socket.settimeout(3.0)
    while True:
        d, addr = the_socket.recvfrom(8192)
        print(d)
        if not d: break
        total_data.append(d)
    return ''.join(total_data)


if __name__ == '__main__':
    #x = raw_input('What is your name?')

    port = 21
    buf = 200
    print(socket.gethostname())
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((socket.gethostname(), port))
    # Create socket and bind to address

    player_count = 0
    while player_count != 2:
        data = recv_basic(s)
        print(data)
        if data:
            player_info = rpip(data)
            player = {'addr': addr,  # IP, Port
                      'player_id': player_count,  # the local counter 1/2
                      'map': player_info.get('map'),  # numpy ndarray
                      'map_size': ord(str(player_info.get('map_size').lower()))-96,  # the map dimensions  ord(str(sys.argv[1]).lower())-96
                      'username': player_info.get('username')}  # the clients username

            for p in connections:
                if p.get('username') is player.get('username'):  # Username taken
                    print("Player %s tried to connect, but the username were taken (%s)" %
                          (player.get('addr'), player.get('usernname')))
                    s.sendto(create_message(RT.username_taken.value, None), addr)  # Send username taken msg
                # elif p.get('addr')[0] is player.get('addr')[0]:  # The same IP have been used
                #    print("Player %s tried to connect from multiple clients" % (player.get('addr')))
                #    # msg
                elif int(p.get('map_size')) != int(player.get('map_size')):  # Map size differs for the players
                    print("The players map size are different!\n %s:%s\n%s:%s" %
                          (p.get('username'), int(p.get('map_size')), player.get('username'), int(player.get('map_size'))))
                    s.sendto(create_message(RT.map_size_error.value,
                                            "Your map size is differen from the opponent!\n"
                                            "Your map size: %s\n"
                                            "Opponent map size: %s"
                                            % (player.get('map_size'), p.get('map_size'))
                                            ), addr)  # Send incorrect map size msg
                else:  # Successful addition of player (trivial when connection.size = 0)
                    accept_player(plyer_info=player, player_count=player_count)
            if player_count == 0:  # Accept the first player
                accept_player(plyer_info=player, player_count=player_count)

    print("Two players are now connected")
    for players in connections:
        print(players.get("addr")[0])

    # Start the actual game
    game_in_progress = True
    turn = 1
    while game_in_progress:
        print("Turn: %d" % turn)
        if turn % 2 == 1:
            current_player = connections[0]
            waiting_player = connections[1]
        else:
            current_player = connections[1]
            waiting_player = connections[0]

        s.sendto(create_message(RT.start_turn.value,  # send message to current player
                                "Your turn\nEnter coordinate to bomb:"), current_player.get('addr'))
        s.sendto((create_message(RT.msg.value,  # send message to waiting player
                                 "Opponent %s's turn" % current_player.get('username'))), waiting_player.get('addr'))

        while True:  #TODO: create a win condition
            package = rp(s.recvfrom(buf)[0])
            request_type = package.get('rt')
            message = package.get('msg')
            if request_type == RT.send_coord:  # player send a coordinate they wish to bomb
                while check_for_hit(message, waiting_player.get('map'), current_player.get('username')):  # continue if hit
                    s.sendto(create_message(RT.hit.value,
                                            "Hit at: " + message + "\nEnter new coordinate:"
                                            ), current_player.get('addr'))
                    coordinate = rm(s.recvfrom(buf))  # Only read the message
                else:  # player missed
                    s.sendto(create_message(RT.miss.value, "Miss!\nIt is now the opponents turn"), current_player.get('addr'))
                    turn += 1

    s.close()

