from Cpu import Cpu
from Task import Task
from Job import Job, WATERFALL_MIGRATIONS_ENABLED
from typing import List, Tuple, Any, Union
from utils import binary_search
import math


class Scheduler:
    def __init__(self):
        self.task_list = []
        self.processors = []
        self.jobs_on_processors = None

    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pass

    def get_task_list(self):
        return self.task_list

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

    def reschedule(self, job_list: List[Job], processors) -> Tuple[List[Any], Tuple[int, None]]:
        new_job_list = []
        for job in job_list:
            self.add_job(new_job_list, job)
            self.assign_processor(job, job_list, processors)
            # print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor().get_id())

        return new_job_list, (-1, None)

    @staticmethod
    def assign_processor(job: Job, job_list: List[Job], processor_list: List[Cpu]):
        job_priority = job_list.index(job)
        if job_priority < len(processor_list):
            # not avoiding waterfall migrations
            if not WATERFALL_MIGRATIONS_ENABLED:
                job.set_processor([processor_list[job_priority]])
            else:
                # avoiding waterfall migrations
                one_processor_is_None = job.get_processor() is None
                if one_processor_is_None or job.get_processor()[0].get_speed() != processor_list[
                    job_priority].get_speed():
                    job.set_processor([processor_list[job_priority]])
        else:
            job.set_processor(None)

    def get_jobs_on_processor(self, processor):
        if self.jobs_on_processors is not None:
            return self.jobs_on_processors[processor]
        return None

    def get_earliest_release(self, job_list, t, task):
        # no deadline partitioning
        return math.inf

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
        for index, task in enumerate(self.task_list):
            task.set_id(index)
        return self.task_list  # sort by deadlines


class EDF_Scheduler(Scheduler):
    def __init__(self):
        super(EDF_Scheduler, self).__init__()

    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_deadline() <= job_list[j].get_deadline()
                                      or ((job_list[j].get_deadline() == job.get_deadline()) and
                                          (job_list[j].get_id() < job.get_id()))
                            )
        job_list.insert(pos, job)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors()  # sort by decreasing speeds
        self.task_list = task_list

class Level_Scheduler(Scheduler):
    def __init__(self):
        super(Level_Scheduler, self).__init__()

    def release_job(self, job_list: List[Job], task: Task, processors, t):
        earliest_release = self.get_earliest_release(job_list, t, task)
        new_job = Job(task.get_id(), t, t + task.get_deadline(), task.get_wcet(),
                              self.task_list.index(task))
        new_job.scale_u(earliest_release)
        #new_job = Job(task.get_id(), t, t + task.get_deadline(), task.get_wcet(),
        #              self.task_list.index(task))
        self.add_job(job_list, new_job)
        self.assign_processor(new_job, job_list, processors)
        self.jobs_on_processors = [[] for _ in self.processors]


    @staticmethod
    def add_job(job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_e() >= job_list[j].get_e()
                                      or ((job_list[j].get_e() == job.get_e()) and
                                          (job_list[j].get_id() < job.get_id()))
                            )
        job_list.insert(pos, job)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors()  # sort by decreasing speeds
        self.task_list = task_list
        self.jobs_on_processors = [[] for _ in self.processors]

    def get_earliest_release(self, job_list, t, task):
        earliest_release = math.inf
        if not job_list:
            earliest_release = t + task.get_deadline()
        for job in job_list:
            if job.get_deadline() < earliest_release:
                earliest_release = job.get_deadline()
        return earliest_release

    def reschedule(self, job_list: List[Job], processors) -> Tuple[
        List[Any], Union[Tuple, Tuple[Union[float, Any], Any]]]:
        new_job_list = []
        for job in job_list:
            self.add_job(new_job_list, job)
        for job in new_job_list:
            self.assign_processor(job, new_job_list, processors)
            #print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor()[0].get_id())

        next_join = (-1, None)
        for running_job_index, running_job in enumerate(new_job_list):
            if running_job.get_processor() is not None:
                lower_prio_index = running_job_index
                while lower_prio_index < len(new_job_list) and new_job_list[lower_prio_index].get_processor() == running_job.get_processor():
                    lower_prio_index += 1

                num_lower_prio_tasks = 0
                i = lower_prio_index
                while i < len(new_job_list) and new_job_list[i].get_processor() == new_job_list[lower_prio_index].get_processor():
                    num_lower_prio_tasks += 1
                    i += 1

                # print("Lower prio index : ", lower_prio_index)
                if lower_prio_index < len(new_job_list): # if there is a lower priority job
                    num_joined_tasks = len(self.get_jobs_on_processor(running_job.get_processor()[0].get_id()))
                    running_job_speed = sum(proc.get_speed() for proc in running_job.get_processor())/num_joined_tasks
                    if new_job_list[lower_prio_index].get_processor() is not None:
                        lower_prio_speed = sum(proc.get_speed() for proc in new_job_list[lower_prio_index].get_processor())/num_lower_prio_tasks
                    else:
                        lower_prio_speed = 0
                    # print("Lower prio speed : ", lower_prio_speed)
                    if running_job_speed > lower_prio_speed:
                        next_interruption_time = (running_job.get_e() - new_job_list[lower_prio_index].get_e()) / (running_job_speed - lower_prio_speed)
                        #next_interruption_time = round(next_interruption_time, 7)
                        if next_join[0] == -1 or next_interruption_time < next_join[0]:
                            next_join = (next_interruption_time, new_job_list[lower_prio_index])
        #print(next_join)
        return new_job_list, next_join

    def assign_processor(self, job: Job, job_list: List[Job], processor_list: List[Cpu]):
        occupied_processors = set()
        search_index = 0  # index of first job in jo_list having the same wcet
        while job_list[search_index].get_e() > job.get_e():
            occupied_processors = occupied_processors.union(job_list[search_index].get_processor())
            search_index += 1

        num_same_priority = 0
        if len(occupied_processors) < len(processor_list):
            while search_index < len(job_list) and job_list[search_index].get_e() == job.get_e():
                num_same_priority += 1
                search_index += 1
            job.set_processor(processor_list[len(occupied_processors):len(occupied_processors)+num_same_priority])
            for i in range(len(occupied_processors),len(occupied_processors)+num_same_priority):
                if i < len(self.jobs_on_processors) and job not in self.jobs_on_processors[i]:
                    self.jobs_on_processors[i].append(job)
            #print("assign ", job.get_id(), job.get_processor()[0].get_id())
        else:
            job.set_processor(None)


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
                            lambda j: job.get_deadline() <= job_list[j].get_deadline()
                                      or ((job_list[j].get_deadline() == job.get_deadline()) and
                                          (job_list[j].get_id() < job.get_id()))
                            )
        job_list.insert(pos, job)

    def release_job(self, job_list: List[Job], task: Task, processors, t):
        new_job = Job(task.get_id(), t, t + task.get_deadline(), task.get_wcet(),
                      self.task_list.index(task))
        self.add_job(job_list, new_job)
        for cpu_num, cpu in enumerate(self.processor_assignment):
            if new_job.get_id() in cpu:
                self.add_job(self.active_jobs[cpu_num], new_job)
        self.assign_processor(new_job, job_list)

    def reschedule(self, job_list: List[Job], processors) -> Tuple[List[Any], Tuple[int, None]]:
        new_job_list = []
        self.active_jobs = [[] for _ in self.processors]
        for job in job_list:
            self.add_job(new_job_list, job)

            for cpu_num, cpu in enumerate(self.processor_assignment):
                if job.get_id() in cpu:
                    self.add_job(self.active_jobs[cpu_num], job)
                    break

            self.assign_processor(job, job_list)
            # print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor().get_id())
        return new_job_list, (-1, None)

    def assign_processor(self, job: Job, job_list: List[Job]):
        for cpu_num, cpu in enumerate(self.processor_assignment):
            if job.get_id() in cpu:
                if self.active_jobs[cpu_num][0].get_id() == job.get_id():
                    job.set_processor([self.processors[cpu_num]])
                else:
                    job.set_processor(None)
                break
        # print(job.get_id(), job.get_processor())

    def processor_task_assignment(self):
        for task in self.task_list:
            task_is_assigned = False
            for j in range(len(self.processors)):
                u_i = task.get_wcet() / task.get_period()
                if u_i <= self.cpu_U[j]:
                    self.processor_assignment[j].append(task.get_id())
                    self.cpu_U[j] -= u_i
                    task_is_assigned = True
                    break
            if not task_is_assigned:
                # TODO: Error
                return 0
        return 1

    def set_processor_assignment(self, processor_assignment):
        self.processor_assignment = processor_assignment


class FFD_Scheduler(Partitionned_Scheduler):
    def __init__(self):
        super(FFD_Scheduler, self).__init__()

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list  # no sorting as any processor fit is fine
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [cpu.get_speed() for cpu in self.processors]
        self.task_list = task_list
        self.processor_task_assignment()
        print("processors: ", self.processor_assignment)


class AFD_Scheduler(Partitionned_Scheduler):
    def __init__(self):
        super(AFD_Scheduler, self).__init__()

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list  # no sorting as any processor fit is fine
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [cpu.get_speed() for cpu in self.processors]
        self.task_list = task_list
        self.processor_task_assignment()
        print("processors: ", self.processor_assignment)


class EDF_DU_IS_FF_Scheduler(Partitionned_Scheduler):
    def __init__(self):
        super(EDF_DU_IS_FF_Scheduler, self).__init__()

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors(False)  # sort by increasing speeds
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [cpu.get_speed() for cpu in self.processors]

        self.task_list = sorted(task_list, key=lambda task: task.get_wcet() / task.get_period(), reverse=True)
        for index, task in enumerate(self.task_list):
            task.set_id(index)

        self.processor_task_assignment()
        print("processors: ", self.processor_assignment)
