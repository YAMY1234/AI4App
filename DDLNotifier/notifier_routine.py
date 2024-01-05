import os

from DDLNotifier.CUHK import ddl_notifier as CUHK
from DDLNotifier.HKU import ddl_notifier as HKU
from DDLNotifier.HKUST import ddl_notifier as HKUST

import sys
# Get the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))
# Append the current directory to sys.path
sys.path.append(current_directory)


def main():
    CUHK.main()
    HKU.main()
    HKUST.main()

if __name__ == '__main__':
    main()
