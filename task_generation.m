function [x,v] = task_generation(n, m, s, r)

T_min = 10
T_max = 50

for i = 1:r
    file_name = strcat("tasks/task_set", int2str(r), '.txt')
    file_id = fopen(file_name, 'w');
    U = randfixedsum(n,m,s,0.1,1)
    for j = 1:n
        u_i = U(j)
        r_i = unifrnd(log(T_min), log(T_max))
        T_i = exp(r_i)
        wcet = u_i * T_i
        task = [0 wcet T_i T_i]

        fdisp(file_id, task);
    end
    fclose(file_id);
end

endfunction