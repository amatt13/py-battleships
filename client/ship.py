class Ship(object):
    def __init__(self, ship_id, start_cord_x, start_cord_y, area):
        self.ship_id = ship_id
        self.start_cord_x = start_cord_x
        self.start_cord_y = start_cord_y
        self.area = area
        self.alive = True
