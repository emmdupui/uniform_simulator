import argparse

from cpu_gen import *
from Schedulers import *
from Simulator import Simulator
from utils import task_file_parser
import os
import numpy as np
import matplotlib.pyplot as plt

preemptions = [0 for _ in range(6)]
migrations = [0 for _ in range(6)]
deadlines_missed = [0 for _ in range(6)]
iterations = [0 for _ in range(6)]
tot_iterations = [0 for _ in range(6)]

NUM_TASK_SETS = 11
NUM_CPU_SETS = 11
TASK_SET_SIZE = 50
CPU_SET_SIZES = [2 ** i for i in range(1,7)]
TOTAL_UTILIZATION = CPU_SET_SIZES



def update_values(simulator, algo_num):
    if not simulator.not_feasible():
        preemptions[algo_num] += simulator.get_num_preemptions()
        migrations[algo_num] += simulator.get_num_migrations()
        iterations[algo_num] += 1

    deadlines_missed[algo_num] += simulator.not_feasible()
    tot_iterations[algo_num] += 1

def run_all(f, cpus, scheduler, algo_num):
    task_list = task_file_parser(f)
    #cpus = [Cpu(0, 0.6), Cpu(1, 1.4)]
    #cpus = [Cpu(0, 2), Cpu(1, 1), Cpu(2, 1), Cpu(3, 1)]

    scheduler.run(task_list, cpus)
    simulator = Simulator(scheduler)
    simulator.run()
    update_values(simulator, algo_num)


def average_all():
    average = [[0 for _ in range(3)] for _ in range(6)]
    for i in range(len(preemptions)):
        if iterations[i] != 0:
            av_preemptions = preemptions[i]/iterations[i]
            av_migrations = migrations[i]/iterations[i]
            average[i] = [av_preemptions, av_migrations, 1-deadlines_missed[i]/tot_iterations[i]]

    return average

def plot(res):
    pass


def run_all_schedulers(file, cpu_set):

    #print()
    #print(" ------------------RM-----------------------")
    #print()
    rm_scheduler = RM_Scheduler()
    run_all(file, cpu_set, rm_scheduler, 0)
    """
    #print()
    #print(" ------------------EDF----------------------")
    #print()
    edf_scheduler = EDF_Scheduler()
    run_all(file, cpu_set, edf_scheduler, 1)

    #print()
    #print(" ------------------FFD----------------------")
    #print()
    ffd_scheduler = FFD_Scheduler()
    run_all(file, cpu_set, ffd_scheduler, 2)

    #print()
    #print(" ------------------AFD----------------------")
    #print()
    afd_scheduler = AFD_Scheduler()
    run_all(file, cpu_set, afd_scheduler, 3)

    #print()
    #print(" ------------------EDF_DU_IS_FF----------------------")
    #print()
    edf_DU_IS_FF_scheduler = EDF_DU_IS_FF_Scheduler()
    run_all(file, cpu_set, edf_DU_IS_FF_scheduler, 4)

    
    print()
    print(" ---------------------LEVEL-------------------------")
    print()
    level_scheduler = Level_Scheduler()
    run_all(file, cpu_set, level_scheduler, 5)
    """


def plot_cpu_rep():
    preemptions = [[] for _ in range(6)]
    migrations = [[] for _ in range(6)]
    feasibilities = [[] for _ in range(6)]
    cpu_size = CPU_SET_SIZES[2]
    for num_repetitions in range(10, NUM_CPU_SETS, 10):
    #for num_repetitions in range(1, 2):
        print("Num repetiton = ", num_repetitions)
        res = [[0, 0, 0] for _ in range(6)]
        for i in range(num_repetitions):
            print("repetition ", i)
            cpu_set, speeds = generate_cpu_tasks(TOTAL_UTILIZATION[2], cpu_size, 10, 0.5)
            #cpu_set, speeds = [(0, 2), (1, 2)], [2,2]
            generate_task_sets(speeds)
            cpu_set = list(cpu_set)
            #print(cpu_set)

            res = np.add(res, run_results(2, cpu_set))
        res = np.divide(res, num_repetitions)

        for i in range(6):
            preemptions[i].append(res[i][0])
            migrations[i].append(res[i][1])
            feasibilities[i].append(res[i][2])

    x = [i for i in range(10, NUM_CPU_SETS, 10)]
    #print(feasibilities)
    figure, axis = plt.subplots(1, 3)
    for i in range(len(preemptions)):
        axis[0].plot(x, preemptions[i], label="Number of preemptions", linestyle="-")
        axis[0].set_title("Preemptions")
        axis[1].plot(x, migrations[i], label="Number of migrations", linestyle="--")
        axis[1].set_title("Migrations")
        axis[2].set_title("Feasibility")
        axis[2].plot(x, feasibilities[i], label="Number of feasible sets " + str(i), linestyle="-.")
    plt.legend()
    plt.show()


def generate_task_sets(speeds):
    #print(TASK_SET_SIZE*0.1, sum(speeds), TASK_SET_SIZE*max(speeds))
    oct.task_generation(TASK_SET_SIZE, 1, sum(speeds), 0.1, max(speeds), NUM_TASK_SETS, TOTAL_UTILIZATION[2])

def run_results(i, cpu_set):
    #directory = 'tasks/tasks_' + str(CPU_SET_SIZES[i])
    directory = 'tasks/tasks_' + str(i)

    if not os.path.exists(directory):
        # if the demo_folder directory is not present
        # then create it.
        os.makedirs(directory)
    # iterate over files in
    # that directory
    local_res = [[0 for _ in range(3)] for _ in range(6)]
    files = os.listdir(directory)
    for i in range(len(cpu_set)):
        cpu_set[i] = Cpu(cpu_set[i][0], cpu_set[i][1])

    print(directory, files)
    for filename in files:
        print(filename)
        f = os.path.join(directory, filename)
        #print(directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            run_all_schedulers(f, cpu_set)
            average = average_all()
            local_res = np.add(local_res, average)
            print("AVERAGE = ", average)
        else:
            print("ERROR : NO FILE FOUND : ", filename)

    if len(files) > 0:
        return np.divide(local_res, len(files))
    return -1


if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="file containing tasks", type=str)
    args = parser.parse_args()
    """

    #plot_cpu_rep()

    cpu_set, speeds = [(0, 2), (1, 2)], [2,2]
    run_results(0, cpu_set)