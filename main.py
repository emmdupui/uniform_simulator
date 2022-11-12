import argparse

from Schedulers import *
from Simulator import Simulator
from utils import task_file_parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="file containing tasks", type=str)
    args = parser.parse_args()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(1, 2), Cpu(2, 1)]

    scheduler = RM_Scheduler()
    task_list_rm = scheduler.run(task_list, cpus)
    rm_simulator = Simulator(cpus, task_list_rm, scheduler)
    rm_simulator.run()
    """

    print()
    print(" ------------------EDF----------------------")
    print()

    scheduler = EDF_Scheduler()
    scheduler.run(task_list, cpus)
    rm_simulator = Simulator(cpus, task_list, scheduler)
    rm_simulator.run()
    """
    """
    scheduler = Scheduler()
    rm_simulator = scheduler.rm(task_list)
    rm_simulator.run()

    edf_simulator = scheduler.edf(task_list)
    edf_simulator.run()
    """

"""
TODO: if insert and priority  or deadline is same depending on algo, order by task id so deterministic
    
    EDF PEUX CHANGER DE PRIORITÉ ENTRE 2 EVENEMENTS
"""
