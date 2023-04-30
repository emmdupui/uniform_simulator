WATERFALL_MIGRATIONS_ENABLED = True

# TODO: bad computation of migrations

class Job:
    def __init__(self, id: int, release_time: int, deadline: int, wcet: int, priority: int):
        self.id = id
        self.release_time = release_time
        self.deadline = deadline
        self.period = deadline - self.release_time
        self.wcet = wcet
        self.u = self.wcet / self.period
        self.e = self.u
        self.last_processor = [None, None]  # [last processor set to (may be None), last processor ran on]
        self.processor = None
        self.num_preemptions = 0
        self.num_migrations = 0
        self.priority = priority
        self.processor_history = []

    def get_e(self):
        return self.e

    def reset_e(self):
        self.e = self.u

    def get_id(self):
        return self.id

    def get_release_time(self):
        return self.release_time

    def get_deadline(self):
        return self.deadline

    def get_wcet(self):
        return self.wcet

    def get_priority(self) -> int:
        return self.priority

    def get_processor(self):
        return self.processor

    def get_last_processor(self):
        return self.last_processor[0]

    def set_processor(self, processor):
        # self.last_processor[0] = self.processor  # remembers cpu on which he last ran on
        self.processor = processor

    def set_priority(self, priority: int):
        self.priority = priority

    def update_performances(self):
        if self.last_processor[0] != self.processor and self.last_processor[0] is not None:
            self.num_preemptions += 1

        if self.last_processor[1] is not None and self.processor is not None and self.last_processor[1] != self.processor:
            self.num_migrations += 1

    def execute(self, t: int, processor_speed):
        if (t) > 0:
            self.wcet = self.wcet - t * processor_speed
            self.e = self.e - t * processor_speed
            # print(self.wcet)
        if self.wcet == 0:
            self.processor = None
        else:
            self.update_performances()

        self.last_processor[0] = self.processor  # remembers cpu on which he last ran on
        if self.processor is not None:
            self.last_processor[1] = self.processor

    def get_num_preemptions(self):

        return self.num_preemptions

    def get_num_migrations(self):
        return self.num_migrations

    def scale_u(self, earliest_release):
        self.e = self.u * earliest_release
