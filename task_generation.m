
function [x,v] = task_generation(n, m, s, a, b, r, speed, run_id)

primes = [2,5,7];
exponant = 4;

matrix = {};
for prime = primes
    line = [];
    for exp = 0:exponant
        val = power(prime, exp);
        if val <= primes(end) || power(prime, exp-1) < primes(end)
            repetitions = randi([1,exponant]);
            line = [line repmat(val, 1, repetitions)];
        end
    end
    matrix = [matrix line];
end

for i = 1:r
    # file_name = strcat("/home/users/s/i/sirenard/emma/code/tasks/tasks_", int2str(speed), '_' ,int2str(run_id), "/task_set_", int2str(i), '.txt');
    file_name = strcat("/home/emma/Documents/MA2/thesis/Scheduler/mstd_tasks/tasks/tasks_", int2str(speed), '_' ,int2str(run_id),"/task_set_", int2str(i), '.txt');
    #file_name = strcat("/tasks/tasks_", int2str(speed), '_' ,int2str(run_id),"/task_set_", int2str(i), '.txt');
    file_id = fopen(file_name, 'w');
    U = randfixedsum(n,m,s,a,b);
    for j = 1:n
        u_i = U(j);
        T_i = 1;
        for line = 1:length(matrix)
            index = randi([1,length(matrix{line})]);
            matrix{line}(index);
            T_i = T_i * matrix{line}(index);
        end
        wcet = u_i * T_i;
        task = [0 round(wcet*10)/10 round(T_i*10)/10 round(T_i*10)/10];

        fdisp(file_id, task);
    end
    fclose(file_id);
end

endfunction
