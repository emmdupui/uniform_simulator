from Job import Job
from EventQueue import EventQueue
from Schedulers import Scheduler
from typing import List
from Event import *

class Simulator:
    def __init__(self, scheduler: Scheduler):
        self.processors = scheduler.get_processors()
        self.scheduler = scheduler
        self.task_list = scheduler.get_task_list()
        self.job_list = []
        self.num_preemptions = []
        self.num_migrations = []
        self.queue = EventQueue()
        self.t = 0  # common time for all
        self.last_t = 0
        self.no_deadlines_missed = True

    def run(self):
        for task in self.task_list:
            self.queue.add_event(Event(RELEASE, self.t + task.get_offset(), task))  # add release event

        print("     FIRST RUN queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id()) for i in range(self.queue.get_len())])

        # while len(self.queue.get_len()) > 0 and self.no_deadlines_missed:
        while self.t <= 2 and self.no_deadlines_missed:
            self.treat_event()

        for task in self.task_list:
            self.num_preemptions.append(task.get_num_preemptions())
            self.num_migrations.append(task.get_num_migrations())

        print(sum(self.num_preemptions), sum(self.num_preemptions))

    def treat_event(self):
        event = self.queue.get_head()
        self.t = event.get_t()  # update common time to event time

        # compute job execution till now
        for job in self.job_list:
            if job.get_processor() is not None:  # job assigned to a processor
                cpu_print = job.get_processor().get_id()
                # print(self.t, self.last_t)
                job.execute(self.t, self.last_t)
                print("     Job ", job.get_id(), " is done execution on CPU ", cpu_print,
                     "at time t = ", self.t)

        print("--------------------------------------------")
        for job in self.job_list:
            print(job.get_id())
        print("--------------------------------------------")

        if event.get_id() == RELEASE:
            print("Event RELEASE of task ", event.get_task().get_id(), "at time t = ", self.t)
            self.treat_event_release(event)
        elif event.get_id() == COMPLETION:
            print("Event COMPLETION of task ", event.get_task().get_id(), "at time t = ", self.t)
            self.treat_event_completion(event)
        else:
            print("Event NEXT of task ", event.get_task().get_id(), "at time t = ", self.t)
            self.treat_event_next(event)

        self.last_t = self.t
        return self.t

    def treat_event_completion(self, event):
        task = event.get_task()
        for job_index, job in enumerate(self.job_list):
            if job.get_id() == task.get_id():
                self.check_deadline(job)
                task.add_num_preempts(job.get_num_preemptions())
                task.add_num_migrations(job.get_num_migrations())

                del self.job_list[job_index]
                print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

        if self.no_deadlines_missed:
            # reschedule
            self.job_list, next_interruption = self.scheduler.reschedule(self.job_list, self.processors)

            self.update_queue(next_interruption)

        print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(),self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())],
              " at time t = ", self.t)

    def treat_event_release(self, event):
        task = event.get_task()

        self.scheduler.release_job(self.job_list, task, self.processors, self.t)
        print("     job_list = ", [self.job_list[i].get_id() for i in range(len(self.job_list))])

        self.job_list, next_interruption = self.scheduler.reschedule(self.job_list, self.processors)

        self.update_queue(next_interruption)
 
        # Add next release
        new_release_time = self.t + task.get_period()
        self.queue.add_event(Event(RELEASE, new_release_time, task))  # add release event for next job of same task
        print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(), self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())])

    def treat_event_next(self, event):
        task = event.get_task()

        self.job_list, next_interruption = self.scheduler.reschedule(self.job_list, self.processors)

        self.update_queue(next_interruption)
        print("     queue = ", [(self.queue.get_el(i).get_id(), self.queue.get_el(i).get_task().get_id(), self.queue.get_el(i).get_t()) for i in range(self.queue.get_len())])


    def check_deadline(self, job: Job):
        if job.get_deadline() < self.t:
            self.no_deadlines_missed = False
            print("DEADLINE MISSED at time t = ", job.get_deadline(), "by job ", job.get_id())

    def update_queue(self, next_interruption):
        """
        Removes all events after time of treated event which are completion events.
        Then adds new generated events.
        :return: None
        """

        self.queue.clean_queue()

        for job in self.job_list:
            if job.get_processor() is not None:

                if next_interruption[0] == -1:
                    processor_speed = job.get_processor().get_speed()
                    completion_time = self.t + (job.get_wcet()/processor_speed)
                    # add completion time of task whose job is being executed
                    self.queue.add_event(Event(COMPLETION, completion_time, self.task_list[job.get_id()]))
                elif next_interruption[1].get_id() == job.get_id():
                    if next_interruption[1].get_wcet() == next_interruption[0]:
                        self.queue.add_event(
                            Event(COMPLETION, self.t + next_interruption[0], self.task_list[job.get_id()]))
                        self.scheduler.reset_joint_period(next_interruption[1].get_priority())
                    else:
                        # TODO: processor speed????
                        self.queue.add_event(Event(NEXT, self.t + next_interruption[0], self.task_list[job.get_id()]))
