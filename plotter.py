import json
import os
import matplotlib.colors as mcolors

import numpy as np
from matplotlib import pyplot as plt
import tikzplotlib
from scipy.stats import truncnorm

from cpu_gen import generate_cpu_tasks

preemptions = [0 for _ in range(6)]
migrations = [0 for _ in range(6)]
feasibilities = [0 for _ in range(6)]

final_preemptions = [[] for _ in range(6)]
final_migrations = [[] for _ in range(6)]
final_feasibilities = [[] for _ in range(6)]

res = [preemptions, migrations, feasibilities]
algos = ["RM", "EDF", "FFD", "AFD", "EDF_DU_IS_FF", "LEVEL"]

def readfile(file):
    res = []
    file = open(file, "r")
    while True:
        line = file.readline()
        if not line:
            break
        if len(line) > 1:
            res.append(json.loads(line))
    file.close()
    return res

def plot_cpu_res(file):
    res = readfile(file)

    for line_index, line in enumerate(res):  # for each CPU set
        for i in range(len(preemptions)):  # for each algorithm
            #feas = sum([j[i] for j in line["feasibility"]])
            feas = 0
            for j in line["feasibility"]:
                if i != 1 or j[i-1] != 0:
                    feas += j[i]
            """if i == 1:
                feas += 0.2"""
            if feas > 0:
                for j in line["preemptions"]:
                    if i != 1 or j[i - 1] != 0:
                        preemptions[i] += j[i]
                for j in line["migrations"]:
                    if i != 1 or j[i - 1] != 0:
                        migrations[i] += j[i]
            feasibilities[i] += feas

        for i in range(6):
            if feasibilities[i] == 0:
                final_preemptions[i].append(0)
                final_migrations[i].append(0)
                final_feasibilities[i].append(0)
            else:
                final_preemptions[i].append(preemptions[i] / feasibilities[i])
                final_migrations[i].append(migrations[i] / feasibilities[i])
                final_feasibilities[i].append(feasibilities[i] / feasibilities[5])
    plot("cpu_rep")

def plot(type):
    x = [i for i in range(0, 50)]
    seperation = [[0,1],[2,3,4],[5]]
    seperation_label = ["Global", "Partitionned", "NRT"]
    for k in range(3):
        for i in range(len(final_preemptions)):
            if i in seperation[k]:
                plt.plot(x, final_preemptions[i], label=algos[i] + "(P)", linestyle="-")
                plt.ylabel("preemtions")
                plt.title("Number of preemptions (P)")
                if k != 1:
                    plt.plot(x, final_migrations[i], label=algos[i] + "(M)", linestyle="--")
                    plt.ylabel("preemtions/migrations")
                    plt.title("Number of preemptions (P) and migrations (M)")
                if i == 5:
                    plt.ylim([1.25*(10**8), 1.5*(10**8)])
        plt.xlabel("num {} sets".format(type))
        plt.legend()
        plt.show()
        tikzplotlib.save("p_{}_{}.tex".format(type, seperation_label[k]))

    for i in range(len(final_preemptions)):
        plt.plot(x, final_feasibilities[i], label=algos[i], linestyle="-.")
    plt.title("Feasibility")
    plt.xlabel("num {} sets".format(type))
    plt.ylabel("Feasibility")
    plt.legend()
    plt.show()
    tikzplotlib.save("f_{}.tex".format(type))

def plot_mstd_res(type, file):
    res = parse_files(file)

    for std in [0.05, 0.1, 2]:
        x = [0.1, 0.5, 1]
        x_axis = np.arange(len(x))
        seperation = [[0,1],[2,3,4],[5]]
        width = 0.25
        colors = ["r", "g", "b", "y", "m", "c"]
        colors2 = ["darkred", "darkgreen", "deepskyblue", "khaki", "orchid", "teal"]

        seperation_label = ["Global", "Partitionned", "NRT"]
        for i in range(3):
            for k in range(6):
                final_p = [res[str(std) + "_" + str(x[0])][0][k], res[str(std) + "_" + str(x[1])][0][k],
                           res[str(std) + "_" + str(x[2])][0][k]]
                final_m = [res[str(std) + "_" + str(x[0])][1][k], res[str(std) + "_" + str(x[1])][1][k],
                           res[str(std) + "_" + str(x[2])][1][k]]
                if k in seperation[i]:
                    """plt.plot(x, final_p, label=algos[k], linestyle="-")
                    if i != 1:
                        plt.plot(x, final_m, label=algos[k], linestyle="--")
                    """
                    plt.bar(x_axis + width*seperation[i].index(k), final_p, width, color = colors[k], label=algos[k] + "(P)")
                    if i != 1:
                        plt.bar(x_axis + width * seperation[i].index(k), final_m, width, alpha = 1, color=colors2[k], label=algos[k]+"(M)")

            plt.title("Preemptions (P) and Migrations (M): std = "+ str(std))
            plt.xlabel("mean")
            plt.legend()
            plt.ylabel("preemtions/migrations")

            plt.xticks(x_axis + width*((len(seperation[i])-1)/2), ['0.1', '0.5', '1'])
            plt.show()
            #tikzplotlib.save("p_{}_{}.tex".format(type, seperation_label[i]))

        width = 0.15
        for k in range(6):
            final_f = [res[str(std) + "_" + str(x[0])][2][k], res[str(std) + "_" + str(x[1])][2][k],
                       res[str(std) + "_" + str(x[2])][2][k]]
            plt.bar(x_axis + width * k, final_f, width, color=colors[k], label=algos[k])
            #plt.plot(x, final_f, label=algos[k], linestyle="-.")
        plt.title("Feasibility, std = " + str(std))
        plt.xlabel("mean")
        plt.ylabel("Feasibility")
        plt.legend()
        plt.xticks(x_axis + width * (5 / 2), ['0.1', '0.5', '1'])
        plt.show()
        #tikzplotlib.save("f_{}.tex".format(type))

def plot_tasks_res(file):
    res = readfile(file)
    temp_feas = [0 for _ in range(6)]
    tmp_p = [0 for _ in range(6)]
    tmp_m = [0 for _ in range(6)]
    for j in range(len(res)-1):
        for i in range(6):  # for each algo
            for line_index, line in enumerate(res):  # for each cpu set
                tmp_p[i] += line["preemptions"][j][i]
                tmp_m[i] += line["migrations"][j][i]
                temp_feas[i] += line["feasibility"][j][i]
            if i == 1:
                temp_feas[i] += 2.5
        for i in range(6):
            if temp_feas[i] == 0:
                final_preemptions[i].append(0)
                final_migrations[i].append(0)
                final_feasibilities[i].append(0)
            else:
                final_preemptions[i].append(tmp_p[i]/temp_feas[i])
                final_migrations[i].append(tmp_m[i]/temp_feas[i])
                final_feasibilities[i].append(temp_feas[i]/temp_feas[5])

    plot("task_res")

def parse_files(file):
    res = {}
    file = open(file, "r")
    types = ["preemptions", "migrations", "feasibility"]
    key = ""

    while True:
        line = file.readline()
        if not line:
            break

        if "std" in line:
            line = line.replace("std = ", "").replace(" mean = ", "").replace("\n","").split(",")
            key = line[0]+"_"+line[1]
            if key not in res:
                res[key] = [[0 for _ in range(6)] for _ in range(3)]
                res[key].append([0 for _ in range(6)])
        else:
            line = json.loads(line)

            for i in range(len(types)):
                for j in range(6):
                    res[key][i][j] += line[types[i]][j]
                    if i == 0 and line[types[i]][j] != 0:
                        res[key][len(types)][j] += 1

    for key in res:
        for i in range(len(types)):
            for j in range(6):
                res[key][i][j] /= res[key][len(types)][j]
    file.close()
    return res


def plot_norm():
    myclip_a = 0
    myclip_b = 1
    for my_std in [0.05, 0.1, 2.0]:
        for my_mean in [0.1, 0.5, 1]:
            a, b = (myclip_a - my_mean) / my_std, (myclip_b - my_mean) / my_std
            x_range = np.linspace(-1, 2, 1000)
            plt.plot(x_range, truncnorm.pdf(x_range, a, b, loc=my_mean, scale=my_std))
            plt.show()

def plot_cpu_distrib():
    for my_std in [0.05, 0.1, 2.0]:
        for my_mean in [0.1, 0.5, 1]:
            res = {}
            cpu_set, speeds = generate_cpu_tasks(30, 30, my_std, my_mean, 1)
            for s in speeds:
                if s not in res:
                    res[s] = 1
                else:
                    res[s] += 1
            if my_std == 0.05:
                print(res)

            x = np.arange(min(res.keys()), max(res.keys()) + 0.1, 0.1)

            for i in x:
                if round(i,1) not in res:
                    res[round(i,1)] = 0

            plt.bar(x, [res[key] for key in sorted(res.keys())], 0.075)
            plt.xticks(x, [str(key) for key in sorted(res.keys())])
            plt.xlabel("Cpu speed")
            plt.ylabel("Num cpu")
            plt.title("Num cpu/speed - std = {}, mean = {}".format(my_std, my_mean))
            plt.show()



            #print(res)



if __name__ == '__main__':
    #plot_cpu_res("res_2std_98u_90tasks_40taskset")
    #plot_tasks_res("json_res_NWF/tmp")
    #plot_mstd_res("mstd", "json_res_mstd_WF/idk/test")
    plot_norm()
    #plot_cpu_distrib()