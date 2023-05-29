from typing import List

from Task import Task


def binary_search(start: int, end: int, comparator) -> int:
    """
    return i in [end, start] such that comparator(j) = True for all start <= j <= i and comparator(k) = False for all
    end >= k > i
    :return: i
    """
    if end >= start:
        mid = start + (end - start) // 2
        if comparator(mid):
            return binary_search(start, mid - 1, comparator)
        else:
            return binary_search(mid + 1, end, comparator)
    else:
        return start


def task_file_parser(filename: str) -> List[Task]:
    """
    Reads file that contains a description of the tasks (offset, WCET, deadline and period) that have to be scheduled.
    :param filename
    :return: list of all tasks
    """
    task_list = []
    with open(filename) as file:
        id = 0
        for line in file:
            if len(line.strip()) and len(line.strip().split()) == 4:  # don't care about empty lines
                task_properties = map(float, line.strip().split())  # retrieve task properties as integers list
                task_list.append(Task(id, *task_properties))
                id += 1
    return task_list


def save_task_list(task_list: List[Task], filename: str):
    """
    Creates a file containing a description of the tasks (offset, WCET, deadline and period)
    :param task_list: list of tasks
    :param filename
    """
    lines = []
    for task in task_list:
        lines.append("{} {} {} {}".format(task.get_offset(), task.get_wcet(), task.get_deadline(), task.get_period()))

    with open(filename, "w") as file:
        file.write("\n".join(lines))

if __name__ == '__main__':
    task_file_parser("tasks/tasks_10_1/task_set_1.txt")