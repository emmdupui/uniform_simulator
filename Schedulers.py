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
        for job in job_list:
            self.add_job(new_job_list, job)
            self.assign_processor(job, job_list, processors)
            # print("         UPDATE: job ", job.get_id(), "on processor ", job.get_processor().get_id())

        return new_job_list, (-1, None)

    @staticmethod
    def assign_processor(job: Job, job_list: List[Job], processor_list: List[Cpu]):
        job_priority = job_list.index(job)
        if job_priority < len(processor_list):
            job.set_processor(processor_list[job_priority])
        else:
            job.set_processor(None)

    def reset_joint_period(self, processor):
        pass

    def shift(self, param):
        pass

    def reset_all(self):
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

    def release_job(self, job_list: List[Job], task: Task, processors, t):
        new_job = Job(task.get_id(), t, t + task.get_deadline(), task.get_wcet(),
                      -1)
        self.add_job(job_list, new_job)
        self.assign_processor(new_job, job_list, processors)
        self.processor_assignment[0].append(new_job)
        self.memory = [False for _ in processors]
        self.join_memory = [[] for _ in self.processors]

    def add_job(self, job_list: List[Job], job: Job):
        pos = binary_search(0, len(job_list) - 1,
                            lambda j: job.get_wcet() > job_list[j].get_wcet()
                                      or ((job.get_wcet() == job_list[j].get_wcet()) and
                                          (job_list[j].get_id() > job.get_id()))
                            )
        job_list.insert(pos, job)

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list
        self.sort_processors()  # sort by decreasing speeds
        self.task_list = task_list
        self.processor_assignment = [[] for _ in self.processors]
        self.occupied = [False for _ in self.processors]
        self.period_joint = [None for _ in self.processors]
        self.memory = [False for _ in self.processors]  # memory of joined jobs are running on processor
        self.join_memory = [[] for _ in self.processors]

    def reschedule(self, job_list: List[Job], processors) -> Tuple[List[Any], Tuple[Union[float, Any], Any]]:
        new_job_list = []
        for job in job_list:
            self.add_job(new_job_list, job)

        temp_active_job_list = new_job_list[:]
        temp_processor_assignment = [[] for _ in self.processors]

        for index, i in enumerate(self.join_memory):
            still_running = False
            for j in temp_active_job_list:
                if j in i:
                    still_running = True
            if not still_running:
                self.join_memory[index] = []
                self.memory[index] = False
                self.occupied[index] = False
                self.processor_assignment[index] = []
                self.period_joint[index] = None

        while len(temp_active_job_list) > 0 and [] in temp_processor_assignment:
            first_free_processor = temp_processor_assignment.index([])
            jobs_to_run = self.get_highest_priority_jobs(temp_active_job_list, first_free_processor)
            #print([job.get_id() for job in jobs_to_run], first_free_processor)
            for i in range(len(jobs_to_run)):
                if not self.memory[first_free_processor] and jobs_to_run[i] not in self.join_memory[jobs_to_run[i].get_priority()]:
                    temp_processor_assignment[first_free_processor].append(jobs_to_run[i])
                    del temp_active_job_list[temp_active_job_list.index(jobs_to_run[i])]
                else:
                    temp_processor_assignment[first_free_processor] = self.join_memory[first_free_processor]
                    del temp_active_job_list[temp_active_job_list.index(jobs_to_run[i])]

            if len(jobs_to_run) > 1:
                self.memory[first_free_processor] = True
            self.join_memory[first_free_processor] = temp_processor_assignment[first_free_processor]

        for job in job_list:
            job.set_priority(-1)
            job.set_processor(None)

        for priority, list in enumerate(temp_processor_assignment):
            for job in list:
                job.set_priority(priority)
                job.set_processor(self.processors[priority])
        self.processor_assignment = temp_processor_assignment

        self.occupied = [False for _ in self.processors]
        for job in job_list:
            self.assign_processor(job, new_job_list, processors)

        # print("     processor_assignment : ", self.processor_assignment)

        next_job_interruption = None
        for index, cpu in enumerate(self.processor_assignment):
            if len(cpu) > 1 and (next_job_interruption is None or next_job_interruption.get_wcet() < cpu[0].get_wcet()):
                next_job_interruption = cpu[0]

        res = (new_job_list, (-1, None))
        if next_job_interruption is not None:
            if self.period_joint[next_job_interruption.get_priority()] is None:
                self.period_joint[next_job_interruption.get_priority()] = next_job_interruption.get_wcet()
            number_joint_jobs = len(self.processor_assignment[next_job_interruption.get_priority()])
            if next_job_interruption.get_wcet() == 0:
                return (new_job_list, (0, next_job_interruption))
            else:
                next_interruption_duration = self.period_joint[next_job_interruption.get_priority()] / number_joint_jobs
            # print("     -- Interruption duration: ", next_interruption_duration)
            res = (new_job_list, (next_interruption_duration, next_job_interruption))
        return res

    def shift(self, processor):
        self.join_memory[processor].append(self.join_memory[processor].pop(0))  # shift

    def reset_joint_period(self, processor):
        self.processor_assignment[processor] = []
        self.period_joint[processor] = None
        
    def reset_all(self):
        self.processor_assignment = [[] for _ in self.processors]
        self.occupied = [False for _ in self.processors]
        self.period_joint = [None for _ in self.processors]
        self.memory = [False for _ in self.processors]  # memory of joined jobs are running on processor
        self.join_memory = [[] for _ in self.processors]

    def assign_processor(self, job: Job, new_job_list, processor_list: List[Cpu]):
        # print("job ", job.get_id(), " PRIO ", job.get_priority())
        p_i = job.get_priority()

        print("Job : ", job.get_id(), p_i)
        num_higher_priority = 0
        for i in range(p_i):
            num_higher_priority += len(self.processor_assignment[i])

        if p_i != -1 and num_higher_priority < len(processor_list):
            if job in self.join_memory[p_i]:
                job_index = self.join_memory[p_i].index(job)
            else:
                job_index = self.processor_assignment[p_i].index(job)

            num_cpu_available = len(processor_list)
            for i in range(p_i):
                if i >= 0:
                    num_cpu_available -= len(self.join_memory[i])

            if job.get_processor() is None or self.memory[p_i]:
                num_used_processors = len(processor_list) - num_cpu_available
                processor = num_used_processors + (job_index % len(self.processor_assignment[p_i]))

                # print("proc ", processor, num_cpu_available,num_used_processors, job.get_id())
                if processor <= num_cpu_available and processor < len(processor_list) and processor >= num_used_processors:
                    # print("SET job ", job.get_id(), "on CPU ", processor)
                    job.set_processor(processor_list[processor])
                    self.occupied[processor] = True
                else:
                    job.set_processor(None)
        else:
            job.set_processor(None)

    def get_highest_priority_jobs(self, temp_active_job_list, priority):
        highest_jobs = []
        highest_wcet = temp_active_job_list[0].get_wcet()
        current_index = 0

        is_lower_priority = temp_active_job_list[current_index].get_priority() <= priority
        while current_index < len(temp_active_job_list) and is_lower_priority and (
                highest_wcet == temp_active_job_list[current_index].get_wcet()
                or (self.memory[priority] and temp_active_job_list[current_index] in self.processor_assignment[
            priority])):  # if same prioriy or running jointly on a processor
            #print(temp_active_job_list[current_index].get_priority(), temp_active_job_list[current_index].get_priority() == -1)
            highest_jobs.append(temp_active_job_list[current_index])
            current_index += 1
        return highest_jobs


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

    def reschedule(self, job_list: List[Job], processors) -> Tuple[List[Any], Tuple[int, None]]:
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
        return new_job_list, (-1, None)

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

    def set_processor_assignment(self, processor_assignment):
        self.processor_assignment = processor_assignment


class FFD_Scheduler(Partitionned_Scheduler):
    def __init__(self):
        super(FFD_Scheduler, self).__init__()

    def run(self, task_list: List[Task], processor_list: List[Cpu]):
        self.processors = processor_list  # no sorting as any processor fit is fine
        self.active_jobs = [[] for _ in self.processors]
        self.processor_assignment = [[] for _ in self.processors]
        self.cpu_U = [0 for _ in self.processors]
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
        self.cpu_U = [0 for _ in self.processors]
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
        print("processors: ", self.processor_assignment)
        self.task_list = task_list
        return 1
