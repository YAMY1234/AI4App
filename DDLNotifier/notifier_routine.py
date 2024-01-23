import os

import sys
current_directory = os.path.dirname(os.path.abspath(__file__))
current_directory = os.path.join(current_directory, '..')
# Append the current directory to sys.path
sys.path.append(current_directory)

from email_sender import send_email
from config import CONFIG

from DDLNotifier.P001_HKU import ddl_notifier as P001_HKU
from DDLNotifier.P002_CUHK import ddl_notifier as P002_CUHK
from DDLNotifier.P003_HKUST import ddl_notifier as P003_HKUST
from DDLNotifier.P004_POLYU import ddl_notifier as P004_POLYU
from DDLNotifier.P005_CITYU import ddl_notifier as P005_CITYU
from DDLNotifier.P006_HKBU import ddl_notifier as P006_HKBU
from DDLNotifier.P007_EDUHK import ddl_notifier as P007_EDUHK
from DDLNotifier.P008_INEDUHK import ddl_notifier as P008_INEDUHK
from DDLNotifier.P009_HKSYU import ddl_notifier as P009_HKSYU
from DDLNotifier.P010_HKMU import ddl_notifier as P010_HKMU
from DDLNotifier.P011_HSU import ddl_notifier as P011_HSU
from DDLNotifier.P012_CHUHAI import ddl_notifier as P012_CHUHAI

from DDLNotifier.P014_NTU import ddl_notifier as P014_NTU
from DDLNotifier.P014_NTU2 import ddl_notifier as P014_NTU2
from DDLNotifier.P015_SMU import ddl_notifier as P015_SMU
from DDLNotifier.P016_EDUMO import ddl_notifier as P016_EDUMO
from DDLNotifier.P017_CITYUMO import ddl_notifier as P017_CITYUMO
from DDLNotifier.P018_MPU import ddl_notifier as P018_MPU
from DDLNotifier.P019_MUST import ddl_notifier as P019_MUST
from DDLNotifier.P020_ImperialAcUk import ddl_notifier as P020_ImperialAcUk
from DDLNotifier.P021_UCL import ddl_notifier as P021_UCL
from DDLNotifier.P022_Edinburgh import ddl_notifier as P022_Edinburgh


import threading
import logging


# 设置日志记录
logging.basicConfig(filename='program_errors.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')

def run_program(program):
    if CONFIG.TEST_MODE:
        program.main()
    else:
        try:
            program.main()
        except Exception as e:
            error_message = f"Error running {program.__name__}: {e}"
            logging.error(error_message, exc_info=True)
            print(error_message)
            # Assuming you want to send the error message to yourself
            send_email("Program Failure Alert", error_message, "yamy12344@gmail.com")


def main():
    programs = [P001_HKU, P002_CUHK, P003_HKUST, P004_POLYU, P005_CITYU, P006_HKBU, P007_EDUHK, P008_INEDUHK, P009_HKSYU,
                P010_HKMU, P011_HSU, P012_CHUHAI, P014_NTU, P014_NTU2, P015_SMU, P016_EDUMO, P017_CITYUMO, P018_MPU,
                P019_MUST, P020_ImperialAcUk, P021_UCL, P022_Edinburgh]
    threads = []

    if CONFIG.MULTITHREADING:
        for program in programs:
            thread = threading.Thread(target=run_program, args=(program,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()
    else:
        for program in programs:
            run_program(program)

if __name__ == "__main__":
    main()
