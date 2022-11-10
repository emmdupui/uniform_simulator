from Cpu import Cpu
from Task import Task
from Job import Job
from typing import List
from utils import binary_search


class Scheduler:
    def __init__(self):
        self.task_list = []
        self.processors = []

    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pass

    def sort_processors(self, processor_list: List[Cpu], decreasing=True):
        for cpu in processor_list:
            if len(self.processors) == 0:
                self.processors.append(cpu)
            elif decreasing:
                pos = binary_search(0, len(processor_list) - 1,
                                    lambda i: (cpu.get_speed() < self.processors[i].get_speed()))
                self.processors.insert(pos, cpu)
            else:  # decreasing order
                pos = binary_search(0, len(processor_list) - 1,
                                    lambda i: (cpu.get_speed() > self.processors[i].get_speed()))
                self.processors.insert(pos, cpu)

    def release_job(self, job_list: List[Job], task: Task, processors, t):
        new_job = Job(task.get_id(), t, t + task.get_deadline(), task.get_wcet(),
                      self.task_list.index(task))
        self.add_job(job_list, new_job)
        self.assign_processor(new_job, job_list, processors)

    def reschedule(self, job_list: List[Job], processors) -> List[Job]:
        new_job_list = []
        for job in job_list:
            self.add_job(new_job_list, job)
            self.assign_processor(job, job_list, processors)
            # print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor().get_id())

        return new_job_list

    @staticmethod
    def assign_processor(job: Job, job_list: List[Job], processor_list: List[Cpu]):
        job_priority = job_list.index(job)
        if job_priority < len(processor_list):
            job.set_processor(processor_list[job_priority])


class RM_Scheduler(Scheduler):
    def __init__(self):
        super(RM_Scheduler, self).__init__()

    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda i: (job_list[i].get_priority() > job.get_priority()))
        job_list.insert(pos, job)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.sort_processors(processor_list)  # sort by increasing speeds
        self.task_list = task_list
        return sorted(task_list, key=lambda task: task.get_deadline())  # sort by deadlines


class EDF_Scheduler(Scheduler):
    def __init__(self):
        super(EDF_Scheduler, self).__init__()

    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_deadline() <= job_list[j].get_deadline())
        job_list.insert(pos, job)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.sort_processors(processor_list)  # sort by increasing speeds
        self.task_list = task_list
        return task_list


class Partitionned_Scheduler(Scheduler):
    def __init__(self, processors: List[Cpu]):
        super(Partitionned_Scheduler, self).__init__()
        self.processors = processors
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [0 for _ in self.processors]

    @staticmethod
    def add_job(job_list: List[Job], job: Job):  # EDF BY DEFAULT
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_deadline() <= job_list[j].get_deadline())
        job_list.insert(pos, job)

    def release_job(self, job_list: List[Job], task: Task, processors, t):
        new_job = Job(task.get_id(), t, t + task.get_deadline(), task.get_wcet(),
                      self.task_list.index(task))
        self.add_job(job_list, new_job)
        self.assign_processor(new_job, job_list, processors)

    def reschedule(self, job_list: List[Job], processors) -> List[Job]:
        new_job_list = []
        for job in job_list:
            self.add_job(new_job_list, job)
            self.assign_processor(job, job_list, processors)
            # print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor().get_id())

        return new_job_list

    def assign_processor(self, job: Job, job_list: List[Job], processor_list: List[Cpu]):
        for cpu_num, cpu in enumerate(self.processor_assignment):
            if job.get_id() in cpu:
                for job_index in range(len(cpu)):
                    if job == cpu[job_index]:
                        job.set_processor(cpu_num)
                        break


class FFD_Scheduler(Partitionned_Scheduler):
    def __init__(self, processors: List[Cpu]):
        super(FFD_Scheduler, self).__init__(processors)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.sort_processors(processor_list)  # sort by increasing speeds
        self.task_list = task_list
        # assign to local cpu AFT
        for task in self.task_list:
            task_is_assigned = False
            for j in range(len(self.processors)):
                self.cpu_U[j] = self.processors[j].get_speed() - self.cpu_U[j]
                u_i = task.get_wcet() / task.get_period()
                if self.cpu_U[j] <= u_i:
                    self.processor_assignment.append(task.get_id())
                    task_is_assigned = True
            if not task_is_assigned:
                # TODO: Error
                return 0
        return 1


# TODO: AFD?? random choose?


class EDF_DU_IS_FF_Scheduler(Partitionned_Scheduler):
    def __init__(self, processors: List[Cpu]):
        super(EDF_DU_IS_FF_Scheduler, self).__init__(processors)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.sort_processors(processor_list, False)  # sort by decreasing speeds
        self.task_list = sorted(task_list, key=lambda task: task.get_wcet() / task.get_period())

        for task in self.task_list:
            task_is_assigned = False
            for j in range(len(self.processors)):
                u_i = task.get_wcet() / task.get_period()
                if self.cpu_U[j] + u_i <= self.processors[j].get_speed():
                    self.cpu_U[j] = self.cpu_U[j] + u_i
                    self.processor_assignment.append(task.get_id())
                    task_is_assigned = True
                    break
            if not task_is_assigned:
                # TODO: Error
                return 0
        return 1
