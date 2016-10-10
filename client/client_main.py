import socket
import numpy
import sys
import pickle
import re
import time

from pip._vendor.distlib.compat import raw_input

import client.ship as ship

# Set the socket parameters

HOST = "192.168.5.2" #"192.168.87.47" # AndersM-Pc
PORT = 21
ADDR = (HOST, PORT)

MATCHER = re.compile("(\[[0-9]\])")
DIMENSIONS = ord(str(sys.argv[1]))-96  # Map dimentions
SHIPS_ALLOWED = 4
SHIPS = list()
MAP = numpy.zeros(shape=(DIMENSIONS, DIMENSIONS))  # Matrix


def check_width(first_line: str):
    numbers = first_line.replace("__", "_").split("_")
    if numbers[1] is "1":
        numbers.reverse()
        if int(numbers[0]) == DIMENSIONS:
            print("Map accepted")
        else:
            print("Map width is invalid (Does not correspond with height")
            print("Height: %d \nWidth: %d" % (DIMENSIONS, int(numbers[0])-1))
            sys.exit()
    else:
        print("Failed to load map\nFirst line must start with 1")
        sys.exit()


def update_map(line: str, line_number: int):
    splits = line.split(" ")
    for index, fields in enumerate(splits):
        if MATCHER.match(fields):
            MAP[line_number][index-1] = int(fields[1])


def load_map():
    f = open('map', 'r')
    # Get map width
    check_width(f.readline())

    for i, line in enumerate(f):
        update_map(line, i)
        if line[0] is str(chr(DIMENSIONS + 96)):
            break
    print("Map loaded")


def go_right(ship_id, x, y):
    ship_area = list()
    while (DIMENSIONS - x) > 1:
        if MAP[y][x] == ship_id:
            ship_area.append({'x': x, 'y': y})
        x += 1
    return ship_area


def go_down(ship_id, x, y):
    ship_area = list()
    while (DIMENSIONS - y) > 1:
        if MAP[y][x] == ship_id:
            ship_area.append({'x': x, 'y': y})
        y += 1
    return ship_area


def build_ship(ship_id, x, y):
    ship_area = list()
    ship_area.append({'x': x, 'y': y})
    if (x + 1) < DIMENSIONS and MAP[y][x+1] == ship_id:
        ship_area.extend(go_right(ship_id, x+1, y))
        SHIPS.append(ship.Ship(ship_id=ship_id, start_cord_x=x, start_cord_y=y, area=ship_area))
    elif MAP[y+1][x] == ship_id:
        ship_area.extend(go_down(ship_id, x, y+1))
        SHIPS.append(ship.Ship(ship_id=ship_id, start_cord_x=x, start_cord_y=y, area=ship_area))
    else:
        print("No more ship")  # TODO: is 1 field ships allowed?


def check_ship_positions():
    available_ships = numpy.arange(start=1, stop=SHIPS_ALLOWED + 1, step=1, dtype=numpy.int16)  # Make a list of available ship IDs
    for y, row in enumerate(MAP):  # Check all columns
        for x, field in enumerate(row):  # Check all rows
            if 0 < field <= SHIPS_ALLOWED:  # Check if the field is a ship ID
                if field in available_ships:  # If ship ID is allowed ==> build ship
                    build_ship(field, x, y)
                    available_ships[field-1] = 99  # The ID can no longer be used


def wait_for_message_loop():
    # Create socket and bind to address
    UDPSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    UDPSock.connect(ADDR)

    # Send map
    my_id = -1  # Player id
    while int(my_id) < 0:
        if UDPSock.sendto(pickle.dumps((MAP, sys.argv[1], sys.argv[2])), ADDR):
            print("Sending map...")
            my_id = pickle.loads(UDPSock.recv(8))
        else:
            time.sleep(2)  # delays for 2 seconds
    print("You are now connected to the server!\nYou are player " + str(my_id))

    # Start game
    while True:
        data = pickle.loads(UDPSock.recv(256))
        print("msg from server: ", data)
        coordinate = raw_input(": ")
        UDPSock.sendto(pickle.dumps(coordinate), ADDR)
    UDPSock.close()

if __name__ == '__main__':
    load_map()
    check_ship_positions()
    # Send map and start game!
    wait_for_message_loop()

















