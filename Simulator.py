import math

from Job import Job
from EventQueue import EventQueue
from Schedulers import Scheduler
from typing import List
from Event import *

RUNNING_TIME = 10

class Simulator:
    def __init__(self, scheduler: Scheduler):
        self.processors = scheduler.get_processors()
        self.scheduler = scheduler
        self.task_list = scheduler.get_task_list()
        self.job_list = []
        self.num_preemptions = 0
        self.num_migrations = 0
        self.queue = EventQueue()
        self.t = 0  # common time for all
        self.last_t = 0
        self.no_deadlines_missed = True
        self.looping = False
        self.should_loop = self.scheduler.get_num_preemptions() > -1

    def get_num_preemptions(self):
        return self.num_preemptions

    def get_num_migrations(self):
        return self.num_migrations

    def not_feasible(self):
        return not self.no_deadlines_missed

    def run(self):
        for task in self.task_list:
            self.queue.add_event(Event(RELEASE, self.t + task.get_offset(), task, self.t))  # add release event

        #print("     FIRST RUN queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id()) for i in range(self.queue.get_len())])

        # while len(self.queue.get_len()) > 0 and self.no_deadlines_missed:
        while self.queue.get_el(0).get_t() <= RUNNING_TIME and self.no_deadlines_missed:
            self.treat_event()
            #print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(),self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())],
            #      " at time t = ", self.t)

        if not self.looping:
            for job in self.job_list:
                self.num_preemptions += job.get_num_preemptions()
                self.num_migrations += job.get_num_migrations()
            for task in self.task_list:
                self.num_preemptions += task.get_num_preemptions()
                self.num_migrations += task.get_num_migrations()
        else:
            self.num_preemptions += self.scheduler.get_num_preemptions()
            self.num_migrations += self.scheduler.get_num_migrations()

        print(self.num_preemptions, self.num_migrations)

    def treat_event(self):
        event = self.queue.get_head()
        self.t = event.get_t()  # update common time to event time
        if not self.looping:
            self.processor_occupation = [[] for _ in self.processors]
            # compute job execution till now
            for job_index, job in enumerate(self.job_list):
                if job.get_processor() is not None and round(job.get_e(),6) > 0:  # job assigned to a processor
                    processors = job.get_processor()[0]
                    self.processor_occupation[processors.get_id()] = self.scheduler.get_jobs_on_processor(processors.get_id())
                    cpu_print = [processor.get_id() for processor in job.get_processor()]
                    # print(self.t, self.last_t)
                    if self.processor_occupation[processors.get_id()] is not None and len(self.processor_occupation[processors.get_id()]):
                        processor_speed = sum(proc.get_speed() for proc in job.get_processor()) / len(self.processor_occupation[processors.get_id()])
                        job.execute((self.t - self.last_t), processor_speed)
                    else:
                        job.execute((self.t - self.last_t), job.get_processor()[0].get_speed())

                    print("     Job ", job.get_id(), " is done execution on CPU ", cpu_print,
                         "at time t = ", self.t)

            for job in self.job_list:
                self.check_deadline(job)

        if self.no_deadlines_missed:
            if event.get_id() == RELEASE:
                print("Event RELEASE of task ", event.get_task().get_id(), "at time t = ", self.t)
                self.treat_event_release(event)
            elif event.get_id() == COMPLETION:
                print("Event COMPLETION of task ", event.get_task().get_id(), "at time t = ", self.t)
                self.treat_event_completion(event)
            else:
                print("Event NEXT of task ", event.get_task().get_id(), "at time t = ", self.t)
                self.treat_event_next()

            self.last_t = self.t
            #print(self.scheduler.get_num_preemptions(), self.scheduler.get_num_migrations())
            return self.t
        else:
            return "error"

    def treat_event_release(self, event):
        task = event.get_task()
        if self.t != 0 and not self.looping and self.should_loop:
            self.looping = True
        # Add next release
        new_release_time = self.t + task.get_period()
        self.queue.add_event(Event(RELEASE, new_release_time, task, self.t))  # add release event for next job of same task

        if not self.looping:
            self.scheduler.release_job(self.job_list, task, self.processors, self.t)
            # print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

            earliest_release_time = self.scheduler.get_earliest_release(self.job_list, self.t, task)
            if earliest_release_time != math.inf:
                for job in self.job_list:
                    job.reset_e()
                    job.scale_u(earliest_release_time - self.t)
                    job.set_processor(None)
            else:
                for job in self.job_list:
                    #  TODO if job.get_wcet() <= 0: ????
                    job.scale_u(earliest_release_time - self.t)

            self.job_list, interrupt_job = self.scheduler.reschedule(self.job_list, self.processors)

            self.update_queue(interrupt_job)

        else:
            self.scheduler.update_performances()

        #print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(), self.queue.get_el(i).get_t())
        #       for i in range(self.queue.get_len())])

    def treat_event_completion(self, event):
        task = event.get_task()
        for job_index, job in enumerate(self.job_list):
            if job.get_id() == task.get_id() and round(job.get_wcet(),6) <= 0:
                self.check_deadline(job)
                #print(job.get_id(), self.t)
                if not self.should_loop:
                    task.add_num_preempts(job.get_num_preemptions())
                    task.add_num_migrations(job.get_num_migrations())
                elif not self.looping:
                    self.scheduler.update_end_performances(job)
                #print("PREEMPTIONS ", job.processor_history, job.get_num_preemptions())
                del self.job_list[job_index]
                job.set_processor(None)
                #print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

        if self.no_deadlines_missed:
            # reschedule
            self.job_list, interrupt_job = self.scheduler.reschedule(self.job_list, self.processors)

            self.update_queue(interrupt_job)

        #print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(),self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())],
        #     " at time t = ", self.t)

    def treat_event_next(self):
        if not self.looping:
            self.job_list, interrupt_job = self.scheduler.reschedule(self.job_list, self.processors)
            self.update_queue(interrupt_job)
            self.scheduler.compute_performances(self.job_list)

        #print("     queue = ",
        #      [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(), self.queue.get_el(i).get_t())
        #       for i in range(self.queue.get_len())],
        #      " at time t = ", self.t)

    def check_deadline(self, job: Job):
        if not self.looping and job.get_deadline() <= self.t and round(job.get_wcet(),7) > 0:
            self.no_deadlines_missed = False
            print("DEADLINE MISSED at time t = ", job.get_deadline(), "by job ", job.get_id())

    def update_queue(self, interrupt_job):
        """
        Removes all events after time of treated event which are completion events.
        Then adds new generated events.
        :return: None
        """
        if not self.looping:
            if interrupt_job[0] != -1:
                self.queue.add_next_join(interrupt_job, self.t)
            self.queue.clean_queue(self.t)

            for job in self.job_list:
                processors = job.get_processor()
                if processors is not None:
                    joined_jobs = self.scheduler.get_jobs_on_processor(processors[0].get_id())

                    if joined_jobs is None:  # not level algo
                        cond = round(job.get_wcet(),6) > 0 and sum(
                            job.get_id() == event.get_task().get_id() and event.get_id() == 2 for event in
                            self.queue.queue) == 0
                    else:
                        cond = round(job.get_e(),6) > 0 and sum(
                            job.get_id() == event.get_task().get_id() and event.get_id() == 2 for event in
                            self.queue.queue) == 0
                    if cond:
                        joined_jobs = self.scheduler.get_jobs_on_processor(processors[0].get_id())

                        if joined_jobs is None or len(joined_jobs) <= 1:
                            processor_speed = processors[0].get_speed()
                        else:
                            processor_speed = sum(proc.get_speed() for proc in processors)/len(joined_jobs)

                        if joined_jobs is not None:
                            # completion_time = self.t + (round(job.get_e(),6)/processor_speed)
                            completion_time = self.t + (job.get_e()/processor_speed)
                            #completion_time = round(completion_time, 10)
                        else:
                            # completion_time = self.t + (round(job.get_wcet(),6)/processor_speed)
                            completion_time = self.t + (job.get_wcet()/processor_speed)

                        # add completion time of task whose job is being executed
                        self.queue.add_event(Event(COMPLETION, completion_time, self.task_list[job.get_priority()], self.t))
