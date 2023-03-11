import multiprocessing

bind = "127.0.0.1:8888"
cpu_num = multiprocessing.cpu_count()
workers = cpu_num - int(round(cpu_num / 10.0))
proc_name = "iaos"
default_proc_name = "iaos"
