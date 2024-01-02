from DDLNotifier.CUHK import ddl_notifier as CUHK
from DDLNotifier.HKU import ddl_notifier as HKU
from DDLNotifier.HKUST import ddl_notifier as HKUST


def main():
    CUHK.main()
    HKU.main()
    HKUST.main()

if __name__ == '__main__':
    main()
