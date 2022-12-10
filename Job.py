class Job:
    def __init__(self, id: int, release_time: int, deadline: int, wcet: int, priority: int):
        self.id = id
        self.release_time = release_time
        self.deadline = deadline
        self.wcet = wcet
        self.last_processor = None
        self.processor = None
        self.num_preemptions = 0
        self.num_migrations = 0
        self.priority = priority

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

    def set_processor(self, processor):
        preemption = self.processor is not None and self.processor != processor
        if preemption:  # running job stops running or runs on new processor
            self.num_preemptions += 1
            # print("HERE for job : ", self.id, self.num_preemptions)

        instant_migration = self.processor is not None and processor is not None and self.processor != processor
        # TODO : ? later_migration = self.last_processor is not None and processor is not None and self.last_processor != processor
        if instant_migration:
            self.num_migrations += 1

        if self.processor is not None:
            self.last_processor = self.processor  # remenbers cpu on which he last ran on
        self.processor = processor

    def set_priority(self, priority: int):
        self.priority = priority

    def execute(self, t: int, last_t):
        if (t-last_t) > 0:
            self.wcet = self.wcet - (t-last_t)*self.processor.get_speed()
            # print(self.wcet)
        if self.wcet == 0:
            self.processor = None

    def get_num_preemptions(self):
        return self.num_preemptions

    def get_num_migrations(self):
        return self.num_migrations
