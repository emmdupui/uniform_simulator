from Cpu import Cpu
from Task import Task
from Job import Job
from typing import List, Tuple, Any, Union
from utils import binary_search
import math


class Scheduler:
    def __init__(self):
        self.task_list = []
        self.processors = []

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

    def reschedule(self, job_list: List[Job], processors) -> Tuple[List[Any], Tuple[Union[float, Any], Any]]:
        new_job_list = []
        next_interruption = (None, math.inf)
        count = 0
        for job in job_list:
            self.add_job(new_job_list, job)
            self.assign_processor(job, job_list, processors)
            if next_interruption[1] is None or next_interruption[0].get_priority() == job.get_priority():
                if job.get_wcet() < next_interruption[1]:
                    count = 1
                elif job.get_wcet() == next_interruption[1]:
                    next_interruption = (job, job.get_wcet())
                    count += 1
            # print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor().get_id())
        if next_interruption[0] is not None:
            next_interruption_duration = next_interruption[0].get_wcet() / count
            return new_job_list, (next_interruption_duration, next_interruption[0].get_priority())
        return new_job_list, (-1, None)

    @staticmethod
    def assign_processor(job: Job, job_list: List[Job], processor_list: List[Cpu]):
        job_priority = job_list.index(job)
        if job_priority < len(processor_list):
            job.set_processor(processor_list[job_priority])
        else:
            job.set_processor(None)

    def get_assigment(self, task):
        # TODO: necessary??
        pass

    def reset_joint_period(self, processor):
        pass


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
                            lambda j: job.get_deadline() <= job_list[j].get_deadline()
                                      or ((job_list[j].get_priority() == job.get_priority()) and
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
        self.processor_assignment = None
        self.occupied = []

    def add_job(self, job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_wcet() >= job_list[j].get_wcet()

                            )
        job_list.insert(pos, job)
        for j in job_list:
            job.set_priority(job_list.index(j))


    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors()  # sort by decreasing speeds
        self.task_list = task_list
        self.processor_assignment = [[] for _ in self.processors]
        self.test = [0 for _ in self.processors]
        self.occupied = [False for _ in self.processors]
        self.period_joint = [None for _ in self.processors]

    def reschedule(self, job_list: List[Job], processors) -> Tuple[List[Any], Tuple[Union[float, Any], Any]]:
        print(self.processor_assignment)
        new_job_list = []
        for job in job_list:
            for i, cpu in enumerate(self.processor_assignment):
                for j, el in enumerate(cpu):
                    if el not in job_list:
                        del self.processor_assignment[i][j]
            self.add_job(new_job_list, job)
            self.set_job_priority(job, new_job_list)

        print(self.processor_assignment)
        for job in new_job_list:
            self.assign_processor(job, new_job_list, processors)

        print("TEST ", self.test)
        next_interruption = None
        for index, cpu in enumerate(self.processor_assignment):
            if len(cpu) > 1:
                next_interruption = cpu[0]
                cpu.append(cpu.pop(0))
                self.processor_assignment[index] = cpu

        res = (new_job_list, (-1, None))
        if next_interruption is not None:
            if self.period_joint[next_interruption.get_priority()] is None:
                self.period_joint[next_interruption.get_priority()] = next_interruption.get_wcet()
            number_joint_jobs = len(self.processor_assignment[next_interruption.get_priority()])
            next_interruption_duration = self.period_joint[next_interruption.get_priority()] / number_joint_jobs
            print("xdfghjkl", next_interruption_duration)
            res = (new_job_list, (next_interruption_duration, next_interruption))

        return res

    def reset_joint_period(self, processor):
        self.processor_assignment[processor] = []
        self.period_joint[processor] = None

    def set_job_priority(self, job, job_list):
        p_i = 0
        for index in range(len(job_list)):
            if job_list[index].get_wcet() > job.get_wcet() and job_list[index].get_priority() != job.get_priority():
                if p_i+1 < len(self.processor_assignment) and job_list[index] not in self.processor_assignment[p_i+1]:
                    p_i += 1
                else:
                    p_i = -1

        if p_i != -1 and job.get_priority() < len(self.processor_assignment) and job not in self.processor_assignment[p_i]:
            print(p_i, job.get_priority())
            if job in self.processor_assignment[job.get_priority()]:
                del self.processor_assignment[job.get_priority()][self.processor_assignment[job.get_priority()].index(job)]
            self.processor_assignment[p_i].append(job)

        job.set_priority(p_i)

    def assign_processor(self, job: Job, job_list: List[Job], processor_list: List[Cpu]):
        #print("job ", job.get_id(), " PRIO ", job.get_priority())

        num_cpu_available = len(processor_list)
        p_i = job.get_priority()
        if p_i != -1 and p_i < len(processor_list):
            for i in range(p_i):
                num_cpu_available -= len(self.processor_assignment[i])

            if job not in self.processor_assignment[p_i]:
                self.processor_assignment[p_i].append(job)
                for a, cpu in enumerate(self.processor_assignment):
                    if a != p_i and job in cpu:
                        del self.processor_assignment[a][self.processor_assignment[a].index(job)]

            index = self.processor_assignment[p_i].index(job)

            num_used_processors = len(processor_list)-num_cpu_available
            processor = num_used_processors +(
                        len(self.processor_assignment[p_i]) - index) % len(self.processor_assignment[p_i])

            # print(len(self.processor_assignment[p_i]), index)
            # print("vfgbhnj,k;kjhg help ", processor, num_cpu_available)
            if processor <= num_cpu_available and processor < len(processor_list) and processor >= num_used_processors:
                print("SET job ", job.get_id(), "on CPU ", processor)
                job.set_processor(processor_list[processor])
            else:
                #print("OH NO ", job.get_id())
                job.set_processor(None)
        else:
            job.set_processor(None)

    """
    def assign_processor(self, job: Job, job_list: List[Job], processor_list: List[Cpu]):
        index = 0
        p_i = 0
        while job_list[index].get_id() != job.get_id():
            if index > 0 and job_list[index-1].get_wcet() != job_list[index].get_wcet():
                p_i += 1
            index += 1
        job.set_priority(p_i)

        for index, cpu in enumerate(self.processor_assignment):
            if job.get_id() in cpu:
                del cpu[cpu.index(job.get_id())]
            if len(cpu) == 0:
                self.occupied[index] = False

        if p_i < len(processor_list):
            pos = binary_search(0, len(self.processor_assignment[p_i]) - 1,
                                lambda j: job.get_id() < self.processor_assignment[p_i][j])
            self.processor_assignment[p_i].insert(pos, job.get_id())
            if False in self.occupied:
                processor = self.occupied.index(False)
            else:
                processor = None
            if processor is None or processor > len(processor_list):
                #TODO When several on one, need to get next
                processor = None
            job.set_processor(processor_list[processor])
            self.occupied[processor] = True
        else:
            job.set_processor(None)

    
    def get_assigment(self, task):
        for cpu in self.processor_assignment:
            if task.get_id() in cpu:
                return len(cpu)
        return None
    """


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
                                      or ((job_list[j].get_priority() == job.get_priority()) and
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
