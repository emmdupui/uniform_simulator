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

    def clean_queue(self):
        """
        Removes all events after time of treated event which are completion events.
        :param job_list:
        :param event: Treated event
        :return: None
        """

        event_index = 0
        while event_index < len(self.queue):
            if self.queue[event_index].get_id() != 1:
                del self.queue[event_index]
            else:
                event_index += 1
