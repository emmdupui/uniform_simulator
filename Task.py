class Task:
    def __init__(self, id: int, offset: int, wcet: int, deadline: int, period: int):
        self.id = id
        self.offset = offset
        self.period = period
        self.deadline = deadline
        self.wcet = wcet
        self.num_preemptions = 0
        self.num_migrations = 0

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

    def add_num_preempts(self, num_preemptions):
        self.num_preemptions += num_preemptions

    def add_num_migrations(self, num_migrations):
        self.num_migrations += num_migrations

    def get_num_preemptions(self):
        return self.num_preemptions

    def get_num_migrations(self):
        return self.num_migrations