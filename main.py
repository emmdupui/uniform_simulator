import argparse

from Schedulers import *
from Simulator import Simulator
from utils import task_file_parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="file containing tasks", type=str)
    args = parser.parse_args()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(0, 1), Cpu(1, 1)]

    """
    scheduler = RM_Scheduler()
    scheduler.run(task_list, cpus)
    rm_simulator = Simulator(scheduler)
    rm_simulator.run()

    print()
    print(" ------------------EDF----------------------")
    print()

    scheduler = EDF_Scheduler()
    scheduler.run(task_list, cpus)
    rm_simulator = Simulator(scheduler)
    rm_simulator.run()


    print()
    print(" ------------------FFD----------------------")
    print()

    scheduler = FFD_Scheduler()
    scheduler.run(task_list, cpus)
    ffd_simulator = Simulator(scheduler)
    ffd_simulator.run()

    print()
    print(" ------------------AFD----------------------")
    print()

    scheduler = AFD_Scheduler()
    scheduler.run(task_list, cpus)
    simulator = Simulator(scheduler)
    simulator.run()

    print()
    print(" ------------------EDF_DU_IS_FF----------------------")
    print()

    scheduler = EDF_DU_IS_FF_Scheduler()
    scheduler.run(task_list, cpus)
    simulator = Simulator(scheduler)
    simulator.run()
    """
    scheduler = Level_Scheduler()
    scheduler.run(task_list, cpus)
    rm_simulator = Simulator(scheduler)
    rm_simulator.run()

# TODO: if insert and priority  or deadline is same depending on algo, order by task id so deterministic
# DONE? I think
