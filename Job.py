WATERFALL_MIGRATIONS_ENABLED = False


class Job:
    def __init__(self, id: int, release_time: int, deadline: int, wcet: int, priority: int):
        self.id = id
        self.release_time = release_time
        self.deadline = deadline
        self.period = deadline - self.release_time
        self.wcet = wcet
        self.u = self.wcet / self.period
        self.e = self.u
        self.last_processor = None
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

    def compute_num_migrations_or_preemptions(self, processor):
        if WATERFALL_MIGRATIONS_ENABLED:
            num_different_processor = 0
            speeds = []
            for cpu in processor[0]:
                if cpu.get_speed() not in speeds:
                    num_different_processor += 1
                    speeds.append(cpu.get_speed())
            return num_different_processor
        else:
            return len(processor[0])

    def update_num_preemptions(self):
        last_processor_used = [None, -1]
        for processor_index, processor in enumerate(self.processor_history):
            last_cpu_in_history = self.processor_history[processor_index - 1]

            different_processor = processor[0] != last_cpu_in_history[0]
            different_processor_occupation = processor[1] != last_cpu_in_history[1]

            num_interruptions = self.compute_num_migrations_or_preemptions(processor)

            # Only used by level algorithm
            cond = len(processor[0]) < len(last_cpu_in_history[0])  # restart of task -> runs on less processors
            if (processor_index == 0 or last_cpu_in_history[1] == 1 or cond) and (len(processor[0]) > 1 or len(last_cpu_in_history[0])>1):
                if len(processor[0]) >= 1:
                    # One less preemption as the first appearance on a processor is not a preemption
                    self.num_preemptions += num_interruptions - 1
                    if processor[0] != last_processor_used[0] or processor[1] != last_processor_used[1]:
                        self.num_migrations += num_interruptions - 1

            elif processor_index != 0:
                if different_processor or (not different_processor and different_processor_occupation):
                    self.num_preemptions += num_interruptions
                    if processor[0] != last_processor_used[0] or processor[1] != last_processor_used[1]:
                        self.num_migrations += num_interruptions

            if processor[0] is not None:
                last_processor_used = processor

    def set_processor(self, processor):
        self.last_processor = self.processor  # remembers cpu on which he last ran on
        self.processor = processor

    def set_priority(self, priority: int):
        self.priority = priority

    def execute(self, t: int, processor_speed, num_joined_jobs):
        if (t) > 0:
            self.wcet = self.wcet - t * processor_speed
            self.wcet = round(self.wcet, 7)
            self.e = self.e - t * processor_speed
            self.e = round(self.e, 7)
            # if self.processor is not None:
            self.processor_history.append((self.processor, num_joined_jobs))
            # print(self.wcet)
        if self.wcet == 0:
            self.processor = None
            self.processor_history.append(([], 0))

        self.last_processor = self.processor  # remembers cpu on which he last ran on

    def get_num_preemptions(self):
        self.update_num_preemptions()
        #print(self.processor_history, )
        #print("RES", self.num_preemptions, self.num_migrations)
        return self.num_preemptions

    def get_num_migrations(self):
        return self.num_migrations

    def scale_u(self, earliest_release):
        self.e = self.u * earliest_release
