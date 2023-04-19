class Cpu:
    def __init__(self, id:  int, speed: float):
        self.id = id
        self.speed = speed
        self.occupied = True

    def get_id(self):
        return self.id
    def set_id(self, id):
        self.id = id

    def get_speed(self):
        return self.speed

    def is_occupied(self):
        return self.occupied
