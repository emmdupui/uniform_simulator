from Task import Task

RELEASE = 1
COMPLETION = 2
NEXT = 3


class Event:
    def __init__(self, id: int, t, task: Task):
        self.id = id
        self.t = t
        self.task = task

    def get_id(self):
        return self.id

    def get_t(self):
        return self.t

    def get_task(self):
        return self.task
