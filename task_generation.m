
function [x,v] = task_generation(n, m, s, a, b, r, speed)

T_min = 10;
T_max = 1000;
T_g = 10;

primes = [3,5,7]
exponant = 4

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
matrix

for i = 1:r
    file_name = strcat("tasks/tasks_", int2str(speed), "/task_set_", int2str(i), '.txt');
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
        T_i
        wcet = u_i * T_i;
        task = [0 floor(wcet) floor(T_i) floor(T_i)];

        fdisp(file_id, task);
    end
    fclose(file_id);
end

endfunction