import argparse

from Schedulers import *
from Simulator import Simulator
from utils import task_file_parser
import os

preemptions = [0 for _ in range(6)]
migrations = [0 for _ in range(6)]
deadlines_missed = [0 for _ in range(6)]
iterations = [0 for _ in range(6)]


def update_values(simulator, algo_num):
    if not simulator.not_feasible():
        preemptions[algo_num] += simulator.get_num_preemptions()
        migrations[algo_num] += simulator.get_num_migrations()
        deadlines_missed[algo_num] += simulator.not_feasible()
        iterations[algo_num] += 1


def run_all(f, scheduler, algo_num):
    task_list = task_file_parser(f)
    cpus = [Cpu(0, 2), Cpu(1, 1)]

    scheduler.run(task_list, cpus)
    simulator = Simulator(scheduler)
    simulator.run()
    update_values(simulator, algo_num)


def average_all():
    average = [0 for _ in range(6)]
    for i in range(len(preemptions)):
        if iterations[i] != 0:
            av_preemptions = preemptions[i]/iterations[i]
            av_migrations = migrations[i]/iterations[i]
            average[i] = [av_preemptions, av_migrations, deadlines_missed[i]]

    return average


if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="file containing tasks", type=str)
    args = parser.parse_args()
    """
    directory = 'tasks'

    # iterate over files in
    # that directory
    for filename in os.listdir(directory):
        f = os.path.join(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            """
            print()
            print(" ------------------RM-----------------------")
            print()
            rm_scheduler = RM_Scheduler()
            run_all(f, rm_scheduler, 0)

            print()
            print(" ------------------EDF----------------------")
            print()
            edf_scheduler = EDF_Scheduler()
            run_all(f, edf_scheduler, 1)

            print()
            print(" ------------------FFD----------------------")
            print()
            ffd_scheduler = FFD_Scheduler()
            run_all(f, ffd_scheduler, 2)

            print()
            print(" ------------------AFD----------------------")
            print()
            afd_scheduler = AFD_Scheduler()
            run_all(f, afd_scheduler, 3)


            print()
            print(" ------------------EDF_DU_IS_FF----------------------")
            print()

            edf_DU_IS_FF_scheduler = EDF_DU_IS_FF_Scheduler()
            run_all(f, edf_DU_IS_FF_scheduler, 4)

            """
            print()
            print(" ---------------------LEVEL-------------------------")
            print()
        
            task_list = task_file_parser(f)
            
            level_scheduler = Level_Scheduler()
            run_all(f, level_scheduler, 5)


            print("AVERAGE = ", average_all())

        # TODO: if insert and priority  or deadline is same depending on algo, order by task id so deterministic
        # DONE? I think
