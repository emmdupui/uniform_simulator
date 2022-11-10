from Job import Job
from EventQueue import EventQueue
from Schedulers import Scheduler
from typing import List
from Event import *
from Cpu import *

class Simulator:
    def __init__(self, processors: List[Cpu], task_list: List[Task], scheduler: Scheduler):
        self.processors = processors
        self.scheduler = scheduler
        self.task_list = task_list
        self.job_list = []
        # self.num_preemptions = []
        # self.num_migrations = []
        self.queue = EventQueue()
        self.t = 0  # common time for all
        self.last_t = 0
        self.no_deadlines_missed = True

    def run(self):
        for task in self.task_list:
            self.queue.add_event(Event(RELEASE, self.t + task.get_offset(), task))  # add release event

        print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id()) for i in range(self.queue.get_len())])

        # while len(self.queue.get_len()) > 0 and self.no_deadlines_missed:
        while self.t < 20 and self.no_deadlines_missed:
            self.treat_event()

    def treat_event(self):
        event = self.queue.get_head()
        self.t = event.get_t()  # update common time to event time

        # compute job execution till now
        for job in self.job_list:
            if job.get_processor() is not None:  # job assigned to a processor
                cpu_print = job.get_processor().get_id()
                # print(self.t, self.last_t)
                job.execute(self.t, self.last_t)
                # print("     Job ", job.get_id(), " is executed on CPU ", cpu_print,
                #      "at time t = ", self.t)

        if event.get_id() == RELEASE:
            print("Event RELEASE of task ", event.get_task().get_id(), "at time t = ", self.t)
            self.treat_event_release(event)
        else:  # COMPLETION
            print("Event COMPLETION of task ", event.get_task().get_id(), "at time t = ", self.t)
            self.treat_event_completion(event)

        self.last_t = self.t
        return self.t

    def treat_event_completion(self, event):
        task = event.get_task()
        for job_index, job in enumerate(self.job_list):
            if job.get_id() == task.get_id():
                self.check_deadline(job)
                del self.job_list[job_index]
                print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

        if self.no_deadlines_missed:
            # reschedule
            self.job_list = self.scheduler.reschedule(self.job_list, self.processors)

            self.update_queue()

        print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(),self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())],
              " at time t = ", self.t)

    def treat_event_release(self, event):
        task = event.get_task()

        # Add release job to active jobs
        self.scheduler.release_job(self.job_list, task, self.processors, self.t)
        print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

        self.job_list = self.scheduler.reschedule(self.job_list, self.processors)

        self.update_queue()

        # Add next release
        new_release_time = self.t + task.get_period()
        self.queue.add_event(Event(RELEASE, new_release_time, task))  # add release event for next job of same task
        print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(), self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())])

    def check_deadline(self, job: Job):
        if job.get_deadline() < self.t:
            self.no_deadlines_missed = False
            print("DEADLINE MISSED at time t = ", job.get_deadline(), "by job ", job.get_id())

    def update_queue(self):
        """
        Removes all events after time of treated event which are completion events.
        Then adds new generated events.
        :param event: Treated event
        :return: None
        """

        self.queue.clean_queue()

        for job in self.job_list:
            processor_speed = job.get_processor().get_speed()
            completion_time = self.t + (job.get_wcet()/processor_speed)
            # add completion time of task whose job is being executed
            self.queue.add_event(Event(COMPLETION, completion_time, self.task_list[job.get_priority()]))


"""
to do

- when reschedule -> put back lowest_priority = 0
- correct t -> ex release not at self.t


"""