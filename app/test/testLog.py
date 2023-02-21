# import logging
# import logging.config
# import os
#
# log_filename = "/Users/zhangtao/projects/IAOS/iaos-server/logs/app/app.log"
# os.makedirs(os.path.dirname(log_filename), exist_ok=True)
# # create logger
# cfg = '../conf/logging.cfg'
# logging.config.fileConfig(cfg)
#
# logger = logging.getLogger('app')
#
# logger.debug('debug message')
# logger.info('info message')
# logger.warning('warning message')
# logger.error('error message')
# logger.critical('critical message')

xx={'log_files': '../logs/app/app.log,../logs/quantization/quantization.log,../logs/schedtask/schedtask.log,./logs/blueprint/blueprint.log,./logs/analysis/analysis.log'}
for x in xx.values():
    ss=x.split(',')
    for s in ss:
        print(s)