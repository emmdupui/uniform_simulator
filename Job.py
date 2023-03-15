WATERFALL_MIGRATIONS_ENABLED = False

class Job:
    def __init__(self, id: int, release_time: int, deadline: int, wcet: int, priority: int):
        self.id = id
        self.release_time = release_time
        self.deadline = deadline
        self.period = deadline-self.release_time
        self.wcet = wcet
        self.u = self.wcet/self.period
        self.initial_u = self.u
        self.last_processor = None
        self.processor = None
        self.num_preemptions = 0
        self.num_migrations = 0
        self.priority = priority

    def get_u(self):
        return self.u

    def reset_u(self):
        self.u = self.initial_u

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
        if self.processor is not None and self.processor != processor:
            # print("HERE for job : ", self.id, self.num_preemptions)
            # not avoiding waterfall migrations (for level algo)
            if not WATERFALL_MIGRATIONS_ENABLED:
                self.num_preemptions += len(self.processor)
            # avoiding waterfall migrations (for level algo)
            else:
                if len(self.processor) > 1:
                    self.num_preemptions += len(self.processor)-1
                else:
                    self.num_preemptions += 1

        instant_migration = self.processor is not None and processor is not None and self.processor != processor
        #instant_migration = self.processor is not None and processor is not None and self.processor != processor
        # TODO : ? later_migration = self.last_processor is not None and processor is not None and self.last_processor != processor

        # not avoiding waterfall migrations (for level algo)
        if instant_migration:
            if not WATERFALL_MIGRATIONS_ENABLED:
                self.num_migrations += len(self.processor)
            else:
                # avoiding waterfall migrations (for level algo)
                if instant_migration:
                    if len(self.processor) > 1:
                        self.num_migrations += len(self.processor) - 1
                    else:
                        self.num_migrations += 1

        if self.processor is not None:
            self.last_processor = self.processor  # remembers cpu on which he last ran on
        self.processor = processor

    def set_priority(self, priority: int):
        self.priority = priority

    def execute(self, t: int):
        if (t) > 0:
            processor_speed = sum(proc.get_speed() for proc in self.processor) / len(self.processor)
            self.wcet = self.wcet - t*processor_speed
            self.wcet = round(self.wcet, 7)
            self.u = self.u - t*processor_speed
            self.u = round(self.u, 7)
            # print(self.wcet)
        if self.wcet == 0:
            self.processor = None

    def get_num_preemptions(self):
        return self.num_preemptions

    def get_num_migrations(self):
        return self.num_migrations

    def scale_u(self, earliest_release):
        self.u = self.initial_u*earliest_release

