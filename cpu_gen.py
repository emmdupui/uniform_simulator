from math import floor
import numpy as np
from scipy.stats import truncnorm
import oct2py

oct = oct2py.Oct2Py()
oct.eval('pkg load statistics')

# user input
myclip_a = 0.1
myclip_b = 1


def generate_cpu_tasks(total_utilization, cpu_set_size, std, mean):
    my_std = std
    my_mean = mean
    # Speed generation
    a, b = (myclip_a - my_mean) / my_std, (myclip_b - my_mean) / my_std
    ratios = truncnorm.rvs(a, b, loc=my_mean, scale=my_std, size=cpu_set_size)

    y = total_utilization / sum(ratios)
    speeds = list(map(lambda x: round(y * x, 1), ratios))

    return list(zip([i for i in range(len(speeds))], speeds)), speeds


#print(generate_cpu_tasks(4, 10, 10, 0.5))
