from Task import Task

RELEASE = 1
COMPLETION = 2
NEXT = 3
END = 4


class Event:
    def __init__(self, id: int, t, task: Task, set_t: int):
        self.id = id
        self.t = t
        self.task = task
        self.set_t = set_t

    def get_id(self):
        return self.id

    def get_t(self):
        return self.t

    def get_task(self):
        return self.task

    def get_set_t(self):
        return self.set_t

