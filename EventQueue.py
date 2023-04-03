from Event import *
from utils import binary_search


class EventQueue:
    def __init__(self):
        self.queue = []

    def get_len(self):
        return len(self.queue)

    def add_event(self, event: Event):
        index = binary_search(0, len(self.queue) - 1,
                              lambda i: (self.queue[i].get_t() > event.get_t())
                              or ((self.queue[i].get_t() == event.get_t()) and event.get_id() == 2))
        self.queue.insert(index, event)

    def get_head(self):
        return self.queue.pop(0)

    def get_el(self, index):
        return self.queue[index]

    def clean_queue(self, t):
        """
        Removes all events after time of treated event which are completion events.
        :param job_list:
        :param event: Treated event
        :return: None
        """

        event_index = 0
        while event_index < len(self.queue):
            if self.queue[event_index].get_id() == 2 and round(self.queue[event_index].get_t(),6) != round(t,6):
                del self.queue[event_index]
            else:
                event_index += 1

    def add_next_join(self, interrupt_job, t):
        earlier_interrupt = False
        for event_index, event in enumerate(self.queue):
            if event.get_id() == 3:
                rounded_event_t = round(event.get_set_t(),7)
                if round(interrupt_job[0],7) < round(event.get_t()) or rounded_event_t == round(t,7):
                    del self.queue[event_index]
                else:
                    earlier_interrupt = True

        if not earlier_interrupt and round(interrupt_job[0], 6) > 0:
            event = Event(NEXT, t + interrupt_job[0], interrupt_job[1], t)
            self.add_event(event)
