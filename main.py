import argparse

from Schedulers import *
from Simulator import Simulator, NRT_Simulator
from utils import task_file_parser

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="file containing tasks", type=str)
    args = parser.parse_args()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(0, 2), Cpu(1, 1)]
    """
    print()
    print(" ------------------RM-----------------------")
    print()
    rm_scheduler = RM_Scheduler()
    rm_scheduler.run(task_list, cpus)
    rm_simulator = Simulator(rm_scheduler)
    rm_simulator.run()

    print()
    print(" ------------------EDF----------------------")
    print()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(0, 2), Cpu(1, 1)]

    edf_scheduler = EDF_Scheduler()
    edf_scheduler.run(task_list, cpus)
    edf_simulator = Simulator(edf_scheduler)
    edf_simulator.run()

    print()
    print(" ------------------FFD----------------------")
    print()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(0, 2), Cpu(1, 1)]

    ffd_scheduler = FFD_Scheduler()
    ffd_scheduler.run(task_list, cpus)
    ffd_simulator = Simulator(ffd_scheduler)
    ffd_simulator.run()

    print()
    print(" ------------------AFD----------------------")
    print()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(0, 2), Cpu(1, 1)]

    afd_scheduler = AFD_Scheduler()
    afd_scheduler.run(task_list, cpus)
    afd_simulator = Simulator(afd_scheduler)
    afd_simulator.run()

    print()
    print(" ------------------EDF_DU_IS_FF----------------------")
    print()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(0, 2), Cpu(1, 1)]

    edf_DU_IS_FF_scheduler = EDF_DU_IS_FF_Scheduler()
    edf_DU_IS_FF_scheduler.run(task_list, cpus)
    edf_DU_IS_FF_simulator = Simulator(edf_DU_IS_FF_scheduler)
    edf_DU_IS_FF_simulator.run()
    """

    print()
    print(" ---------------------LEVEL-------------------------")
    print()

    task_list = task_file_parser(args.task_file)

    cpus = [Cpu(0, 1), Cpu(1, 1)]
    
    level_scheduler = Level_Scheduler()
    level_scheduler.run(task_list, cpus)
    level_simulator = NRT_Simulator(level_scheduler)
    level_simulator.run()

# TODO: if insert and priority  or deadline is same depending on algo, order by task id so deterministic
# DONE? I think
