import os

import sys
current_directory = os.path.dirname(os.path.abspath(__file__))
current_directory = os.path.join(current_directory, '..')
# Append the current directory to sys.path
sys.path.append(current_directory)

from DDLNotifier.P002_CUHK import ddl_notifier as CUHK
from DDLNotifier.P001_HKU import ddl_notifier as HKU
from DDLNotifier.P003_HKUST import ddl_notifier as HKUST
from DDLNotifier.P004_POLYU import ddl_notifier as POLYU
from DDLNotifier.P005_CITYU import ddl_notifier as CITYU
from DDLNotifier.P006_HKBU import ddl_notifier as HKBU
from DDLNotifier.P007_EDUHK import ddl_notifier as EDUHK
# from DDLNotifier.P008_LN import ddl_notifier as LN
from DDLNotifier.P009_HKSYU import ddl_notifier as HKSYU
from DDLNotifier.P010_HKMU import ddl_notifier as HKMU
from DDLNotifier.P011_HSU import ddl_notifier as HSU
from DDLNotifier.P012_CHUHAI import ddl_notifier as CHUHAI

from DDLNotifier.P014_NTU import ddl_notifier as NTU
from DDLNotifier.P014_NTU2 import ddl_notifier as NTU2
from DDLNotifier.P015_SMU import ddl_notifier as SMU
# from DDLNotifier.P017_CITYUMO import ddl_notifier as CITYUMO
from DDLNotifier.P018_MPU import ddl_notifier as MPU
from DDLNotifier.P019_MUST import ddl_notifier as MUST

import threading
import logging


# 设置日志记录
logging.basicConfig(filename='program_errors.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def run_program(program):
    try:
        program.main()
    except Exception as e:
        logging.error(f"Error running {program.__name__}: {e}", exc_info=True)


def main():
    # programs = [CITYU, HKBU, EDUHK, HKSYU, HKMU, HSU, CHUHAI]
    programs = [CUHK, HKU, HKUST, POLYU, CITYU, HKBU, EDUHK, HKSYU, HKMU, HSU, CHUHAI, NTU, NTU2, SMU, MPU, MUST]
    threads = []

    for program in programs:
        thread = threading.Thread(target=run_program, args=(program,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
