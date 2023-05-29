import argparse
from cpu_gen import *
from Schedulers import *
from Simulator import Simulator
from utils import task_file_parser
import os
import json
import time

NUM_TASK_SETS = 15
TASK_SET_SIZE = 90

def update_values(simulator, algo_num, preemptions, migrations, feasibility):
    if not simulator.not_feasible():
        preemptions[algo_num] += float(simulator.get_num_preemptions())
        migrations[algo_num] += float(simulator.get_num_migrations())
    feasibility[algo_num] += float(not simulator.not_feasible())

def run_all(f, cpus, scheduler, algo_num, preemptions, migrations, feasibility):
    task_list = task_file_parser(f)

    scheduler.run(task_list, cpus)
    simulator = Simulator(scheduler)
    simulator.run()
    update_values(simulator, algo_num, preemptions, migrations, feasibility)

"""def average_all():
    average = [[0 for _ in range(3)] for _ in range(6)]
    for i in range(len(preemptions)):
        if iterations[i] != 0:
            av_preemptions = preemptions[i]/iterations[i]
            av_migrations = migrations[i]/iterations[i]
            average[i] = [av_preemptions, av_migrations, 1-deadlines_missed[i]/tot_iterations[i]]

    return average"""


def run_all_schedulers(file, cpu_set):
    preemptions = [0 for _ in range(6)]
    migrations = [0 for _ in range(6)]
    feasibility = [0 for _ in range(6)]

    # print()
    # print(" ------------------RM-----------------------")
    # print()
    rm_scheduler = RM_Scheduler(WF)
    run_all(file, cpu_set, rm_scheduler, 0, preemptions, migrations, feasibility)

    # print()
    # print(" ------------------EDF----------------------")
    # print()
    edf_scheduler = EDF_Scheduler(WF)
    run_all(file, cpu_set, edf_scheduler, 1, preemptions, migrations, feasibility)

    # print()
    # print(" ------------------FFD----------------------")
    # print()
    ffd_scheduler = FFD_Scheduler(WF)
    run_all(file, cpu_set, ffd_scheduler, 2, preemptions, migrations, feasibility)

    # print()
    # print(" ------------------AFD----------------------")
    # print()
    afd_scheduler = AFD_Scheduler(WF)
    run_all(file, cpu_set, afd_scheduler, 3, preemptions, migrations, feasibility)

    # print()
    # print(" ------------------EDF_DU_IS_FF----------------------")
    # print()
    edf_DU_IS_FF_scheduler = EDF_DU_IS_FF_Scheduler(WF)
    run_all(file, cpu_set, edf_DU_IS_FF_scheduler, 4, preemptions, migrations, feasibility)

    # print()
    # print(" ---------------------LEVEL-------------------------")
    # print()
    #level_scheduler = Level_Scheduler(WF)
    #run_all(file, cpu_set, level_scheduler, 5, preemptions, migrations, feasibility)

    if exp == 2:
        for i in range(6):
            performances["preemptions"][i] += preemptions[i]
            performances["migrations"][i] += migrations[i]
            performances["feasibility"][i] += feasibility[i]
    if exp == 1:
        performances["preemptions"].append(preemptions)
        performances["migrations"].append(migrations)
        performances["feasibility"].append(feasibility)

def plot_rep():
    cpu_size = 10
    cpu_set, speeds = generate_cpu_tasks(cpu_size, cpu_size, 2, 0.5, run_id)

    #directory = 'tasks/tasks_10_' + str(run_id)
    directory = tasks_dir + str(run_id)
    #directory = '/home/users/s/i/sirenard/emma/code/tasks/tasks_' + str(cpu_size)+ '_' + str(run_id)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    #generate_task_sets(speeds)
    cpu_set = list(cpu_set)

    run_results(cpu_size, cpu_set)
    print(json.dumps(performances))

def reset_performances():
    global performances
    performances = {
        "preemptions": [0 for _ in range(6)],
        "migrations": [0 for _ in range(6)],
        "feasibility": [0 for _ in range(6)]
    }


def plot_mean_std():
    cpu_size = 10
    for std in [0.05, 0.5, 2]:
        for mean in [0.1, 0.5, 1]:
            cpu_set, speeds = generate_cpu_tasks(cpu_size, cpu_size, std, mean, run_id)
            #directory = 'tasks/tasks_10_' + str(run_id)
            directory = tasks_dir + str(run_id)
            #directory = '/home/users/s/i/sirenard/emma/code/tasks/tasks_' + str(cpu_size)+ '_' + str(run_id)
            if not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
            generate_task_sets(speeds)
            cpu_set = list(cpu_set)

            #run_results(cpu_size, cpu_set)
            #print("std = {}, mean = {}".format(std, mean))
            #print(json.dumps(performances))

            reset_performances()

def generate_task_sets(speeds):
    #print(TASK_SET_SIZE*0.1, sum(speeds)*0.98, TASK_SET_SIZE*max(speeds))
    oct.task_generation(TASK_SET_SIZE, 1, sum(speeds)*0.98, 0.1, max(speeds), NUM_TASK_SETS, round(sum(speeds, 0)), run_id)

def run_results(i, cpu_set):
    #directory = 'tasks/tasks_10_' + str(run_id)
    directory = tasks_dir + str(run_id)

    #directory = '/home/users/s/i/sirenard/emma/code/tasks/tasks_' + str(i) + '_' + str(run_id)

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    files = os.listdir(directory)
    for i in range(len(cpu_set)):
        cpu_set[i] = Cpu(cpu_set[i][0], cpu_set[i][1])

    for filename in files:
        f = os.path.join(directory, filename)
        if os.path.isfile(f):
            run_all_schedulers(f, cpu_set)

    if exp == 2:
        for i in range(6):
            if performances["feasibility"][i] > 0:
                performances["preemptions"][i] /= performances["feasibility"][i]
                performances["migrations"][i] /= performances["feasibility"][i]
            performances["feasibility"][i] /= len(files)

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--runId', type = int, required =True)
    parser.add_argument('--WF', type = int, required =True)
    parser.add_argument('--tasks', type = str, required =True)
    parser.add_argument('--exp', type = int, required =True)

    return parser.parse_args()


if __name__ == '__main__':
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("task_file", help="file containing tasks", type=str)
    args = parser.parse_args()
    """
    args = parse_args()
    run_id = args.runId
    WF = bool(args.WF)
    tasks_dir = args.tasks
    exp = args.exp

    if exp == 1:
        performances = {
            "preemptions": [],
            "migrations": [],
            "feasibility": []
        }
    else:
        performances = {
            "preemptions": [0 for _ in range(6)],
            "migrations": [0 for _ in range(6)],
            "feasibility": [0 for _ in range(6)]
        }

    if exp == 1:
        average = plot_rep()
    #print(average)
    elif exp == 2:
        plot_mean_std()


    """for i in range(51):
        run_id = i
        plot_mean_std()"""
    #print(performances)
    #print(json.dumps(performances))
    #cpu_set, speeds = [(0, 2), (1, 1)], [2,1]
    #run_results(0, cpu_set)
