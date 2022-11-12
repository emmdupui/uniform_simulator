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

    def get_processors(self):
        return self.processors

    def sort_processors(self, decreasing=True):
        sorted_processors = []
        for cpu in self.processors:
            if len(sorted_processors) == 0:
                sorted_processors.append(cpu)
            elif decreasing:
                pos = binary_search(0, len(sorted_processors) - 1,
                                    lambda i: (cpu.get_speed() > sorted_processors[i].get_speed()))
                sorted_processors.insert(pos, cpu)
            else:  # increasing order
                pos = binary_search(0, len(sorted_processors) - 1,
                                    lambda i: (cpu.get_speed() < sorted_processors[i].get_speed()))
                sorted_processors.insert(pos, cpu)
        self.processors = sorted_processors

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
        else:
            job.set_processor(None)


class RM_Scheduler(Scheduler):
    def __init__(self):
        super(RM_Scheduler, self).__init__()

    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda i: ((job_list[i].get_priority() > job.get_priority())
                            or ((job_list[i].get_priority() == job.get_priority()) and
                                (job_list[i].get_id() < job.get_id()))))
        """
        TODO : (job_list[i].get_id() < job.get_id()) or (job_list[i].get_id() > job.get_id())???????
        """
        job_list.insert(pos, job)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors()  # sort by decreasing speeds
        self.task_list = sorted(task_list, key=lambda task: task.get_deadline())
        return self.task_list  # sort by deadlines


class EDF_Scheduler(Scheduler):
    def __init__(self):
        super(EDF_Scheduler, self).__init__()

    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_deadline() <= job_list[j].get_deadline())
        job_list.insert(pos, job)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors()  # sort by decreasing speeds
        self.task_list = task_list
        return task_list


class Partitionned_Scheduler(Scheduler):
    def __init__(self):
        super(Partitionned_Scheduler, self).__init__()
        self.processors = []
        self.active_jobs = None
        self.processor_assignment = None
        self.cpu_U = None

    @staticmethod
    def add_job(job_list: List[Job], job: Job):  # EDF BY DEFAULT
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_deadline() <= job_list[j].get_deadline())
        job_list.insert(pos, job)

    def release_job(self, job_list: List[Job], task: Task, processors, t):
        new_job = Job(task.get_id(), t, t + task.get_deadline(), task.get_wcet(),
                      self.task_list.index(task))
        self.add_job(job_list, new_job)
        for cpu_num,  cpu in enumerate(self.processor_assignment):
            if new_job.get_id() in cpu:
                self.add_job(self.active_jobs[cpu_num], new_job)
        self.assign_processor(new_job, job_list)

    def reschedule(self, job_list: List[Job], processors) -> List[Job]:
        new_job_list = []
        new_active_job_list = [[] for _ in self.processors]
        for job in job_list:
            self.add_job(new_job_list, job)

            for cpu_num, cpu in enumerate(self.processor_assignment):
                if job.get_id() in cpu:
                    self.add_job(new_active_job_list[cpu_num], job)

            self.assign_processor(job, job_list)
            # print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor().get_id())
        self.active_jobs = new_active_job_list
        return new_job_list

    def assign_processor(self, job: Job, job_list: List[Job]):
        for cpu_num, cpu in enumerate(self.processor_assignment):
            if job.get_id() in cpu:
                if self.active_jobs[cpu_num][0].get_id() == job.get_id():
                    job.set_processor(self.processors[cpu_num])
                else:
                    job.set_processor(None)
                break


    def processor_task_assignment(self):
        for task in self.task_list:
            task_is_assigned = False
            for j in range(len(self.processors)):
                self.cpu_U[j] = self.processors[j].get_speed() - self.cpu_U[j]
                u_i = task.get_wcet() / task.get_period()
                if u_i <= self.cpu_U[j]:
                    self.processor_assignment[j].append(task.get_id())
                    task_is_assigned = True
                    break
            if not task_is_assigned:
                # TODO: Error
                return 0
        return 1


class FFD_Scheduler(Partitionned_Scheduler):
    def __init__(self):
        super(FFD_Scheduler, self).__init__()

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors()  # sort by decreasing speeds
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [0 for _ in self.processors]

        self.task_list = task_list
        # assign to local cpu AFT
        self.processor_task_assignment()


class AFD_Scheduler(Partitionned_Scheduler):
    def __init__(self):
        super(AFD_Scheduler, self).__init__()

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list  # no sorting as any processor fit is fine
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [0 for _ in self.processors]
        self.task_list = task_list
        self.processor_task_assignment()


class EDF_DU_IS_FF_Scheduler(Partitionned_Scheduler):
    def __init__(self):
        super(EDF_DU_IS_FF_Scheduler, self).__init__()

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors(False)  # sort by increasing speeds
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [0 for _ in self.processors]
        self.task_list = sorted(task_list, key=lambda task: task.get_wcet() / task.get_period())

        for task in self.task_list:
            task_is_assigned = False
            for j in range(len(self.processors)):
                u_i = task.get_wcet() / task.get_period()
                if self.cpu_U[j] + u_i <= self.processors[j].get_speed():
                    self.cpu_U[j] = self.cpu_U[j] + u_i
                    self.processor_assignment[j].append(task.get_id())
                    task_is_assigned = True
                    break
            if not task_is_assigned:
                # TODO: Error
                print("Error")
                return 0
        print(self.processor_assignment)
        return 1
