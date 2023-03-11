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

    def get_num_preemptions(self):
        return self.num_preemptions

    def get_num_migrations(self):
        return self.num_migrations

    def not_feasible(self):
        return not self.no_deadlines_missed

    def run(self):
        for task in self.task_list:
            self.queue.add_event(Event(RELEASE, self.t + task.get_offset(), task))  # add release event

        #print("     FIRST RUN queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id()) for i in range(self.queue.get_len())])

        # while len(self.queue.get_len()) > 0 and self.no_deadlines_missed:
        while self.t <= RUNNING_TIME and self.no_deadlines_missed:
            self.treat_event()
            #print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(),self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())],
            #      " at time t = ", self.t)

        for task in self.task_list:
            self.num_preemptions += task.get_num_preemptions()
            self.num_migrations += task.get_num_migrations()

        print(self.num_preemptions, self.num_migrations)

    def treat_event(self):
        event = self.queue.get_head()
        self.t = event.get_t()  # update common time to event time
        # compute job execution till now
        for job in self.job_list:
            if job.get_processor() is not None:  # job assigned to a processor
                cpu_print = [processor.get_id() for processor in job.get_processor()]
                # print(self.t, self.last_t)
                job.execute(self.t, self.last_t)
                #print("     Job ", job.get_id(), " is done execution on CPU ", cpu_print,
                #     "at time t = ", self.t)

        """
        print("--------------------------------------------")
        for job in self.job_list:
            print(job.get_id())
        print("--------------------------------------------")
        """

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
        return self.t

    def treat_event_release(self, event):
        task = event.get_task()

        # Add next release
        new_release_time = self.t + task.get_period()
        self.queue.add_event(Event(RELEASE, new_release_time, task))  # add release event for next job of same task

        self.scheduler.release_job(self.job_list, task, self.processors, self.t)
        #print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

        self.job_list, interrupt_job = self.scheduler.reschedule(self.job_list, self.processors)

        self.update_queue(interrupt_job)

        #print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(), self.queue.get_el(i).get_t())
        #       for i in range(self.queue.get_len())])

    def treat_event_completion(self, event):
        task = event.get_task()
        for job_index, job in enumerate(self.job_list):
            if job.get_id() == task.get_id():
                self.check_deadline(job)
                task.add_num_preempts(job.get_num_preemptions())
                task.add_num_migrations(job.get_num_migrations())

                del self.job_list[job_index]
                #print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

        if self.no_deadlines_missed:
            # reschedule
            self.job_list, interrupt_job = self.scheduler.reschedule(self.job_list, self.processors)

            self.update_queue(interrupt_job)

        #print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(),self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())],
        #     " at time t = ", self.t)

    def treat_event_next(self):
        self.job_list, interrupt_job = self.scheduler.reschedule(self.job_list, self.processors)

        self.update_queue(interrupt_job)

        #print("     queue = ",
        #      [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(), self.queue.get_el(i).get_t())
        #       for i in range(self.queue.get_len())],
        #      " at time t = ", self.t)

    def check_deadline(self, job: Job):
        if job.get_deadline() < self.t:
            self.no_deadlines_missed = False
            print("DEADLINE MISSED at time t = ", job.get_deadline(), "by job ", job.get_id())

    def update_queue(self, interrupt_job):
        """
        Removes all events after time of treated event which are completion events.
        Then adds new generated events.
        :return: None
        """
        if interrupt_job[0] != -1:
            self.queue.add_next_join(interrupt_job, self.t)
        self.queue.clean_queue(self.t)

        for job in self.job_list:
            if sum(job.get_id() == event.get_task().get_id() and event.get_id() == 2 for event in self.queue.queue) == 0:
                processors = job.get_processor()
                if processors is not None:
                    if len(processors) == 1:
                        processor_speed = processors[0].get_speed()
                    else:
                        processor_speed = sum(proc.get_speed() for proc in processors)/len(processors)

                    joined_jobs = self.scheduler.get_jobs_on_processor(processors[0].get_id())
                    if joined_jobs is not None:
                        joint_wcet = sum(job.get_wcet() for job in joined_jobs)
                        completion_time = self.t + (joint_wcet/processor_speed)/len(processors)
                    else:
                        completion_time = self.t + (job.get_wcet()/processor_speed)
                    # add completion time of task whose job is being executed
                    self.queue.add_event(Event(COMPLETION, completion_time, self.task_list[job.get_priority()]))
