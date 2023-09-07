# utils/logger.py

import logging
import os


def setup_logger(Uni_ID, log_dir="./data/"):
    # 设置日志文件路径
    log_file_path = os.path.join(log_dir, f"{Uni_ID}/errors.log")
    # 确保目录存在
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

    logging.basicConfig(filename=log_file_path,
                        level=logging.ERROR,
                        format='%(asctime)s - %(levelname)s: %(message)s')

    return logging
