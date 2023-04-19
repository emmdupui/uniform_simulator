
function [x,v] = task_generation(n, m, s, a, b, r, speed)

T_min = 10;
T_max = 500;


for i = 1:r
    file_name = strcat("tasks/tasks_", int2str(speed), "/task_set_", int2str(i), '.txt');
    file_id = fopen(file_name, 'w');
    U = randfixedsum(n,m,s,a,b);
    for j = 1:n
        u_i = U(j);
        r_i = unifrnd(log(T_min), log(T_max));
        T_i = exp(r_i);
        wcet = u_i * T_i;
        task = [0 floor(wcet) floor(T_i) floor(T_i)];

        fdisp(file_id, task);
    end
    fclose(file_id);
end

endfunction