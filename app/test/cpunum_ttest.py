import multiprocessing

cpu_num = multiprocessing.cpu_count()
workers = cpu_num - int(round(cpu_num / 10.0))

print(cpu_num)
print(workers)