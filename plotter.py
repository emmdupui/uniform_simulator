import os

from matplotlib import pyplot as plt

from main import NUM_CPU_SETS

preemptions = [0 for _ in range(6)]
migrations = [0 for _ in range(6)]
feasibilities = [0 for _ in range(6)]

final_preemptions = [[] for _ in range(6)]
final_migrations = [[] for _ in range(6)]
final_feasibilities = [[] for _ in range(6)]

res = [preemptions, migrations, feasibilities]
algos = ["RM", "EDF", "FFD", "AFD", "EDF_DU_IS_FF", "LEVEL"]

def readfile(file):
    file = open(file, "r")
    lines = file.readlines()

    for line_index, line in enumerate(lines[1:]):
        if line_index > 0 and line_index%10 == 0 or line_index == 36 or line_index == 2:
            for i in range(len(preemptions)):
                final_preemptions[i].append(preemptions[i]/line_index)
                final_migrations[i].append(migrations[i]/line_index)
                final_feasibilities[i].append(feasibilities[i]/line_index)

        line = line.replace('\n', '').replace('[', '').replace(']', '').split(',')
        i = 0
        for value_index, value in enumerate(line):
            if value_index > 0 and value_index % 3 == 0:
                i += 1
            res[value_index % 3][i] += float(value)
    print(final_preemptions)
    plot_res()
    file.close()

def plot_res():
    x = [i for i in range(0, 41, 10)]
    # print(feasibilities)
    figure, axis = plt.subplots(1, 3)
    for i in range(len(final_preemptions)-1):
        print(final_feasibilities[i])
        axis[0].plot(x, final_preemptions[i], label=algos[i], linestyle="-")
        axis[0].set_title("Preemptions")
        if i not in [2,3,4]:
            axis[1].plot(x, final_migrations[i], label=algos[i], linestyle="--")
        axis[1].set_title("Migrations")
        axis[2].set_title("Feasibility")
        axis[2].plot(x, final_feasibilities[i], label=algos[i], linestyle="-.")
    plt.legend()
    plt.show()

if __name__ == '__main__':
    readfile("res_10 ")