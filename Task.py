class Task:
    def __init__(self, id: int, offset: int, wcet: int, deadline: int, period: int):
        self.id = id
        self.offset = offset
        self.period = period
        self.deadline = deadline
        self.wcet = wcet

    def get_id(self):
        return self.id

    def get_offset(self):
        return self.offset

    def get_period(self):
        return self.period

    def get_deadline(self):
        return self.deadline

    def get_wcet(self):
        return self.wcet
