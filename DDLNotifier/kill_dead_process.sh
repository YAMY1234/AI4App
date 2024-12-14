#!/bin/bash

# 定义宽泛的相对路径匹配规则
MATCH_PATTERNS=(
    "DDLNotifier/notifier_routine.py"
    "chrome/chrome"
    "chromedriver-linux64/chromedriver"
)

# 遍历匹配规则，逐一终止进程
for pattern in "${MATCH_PATTERNS[@]}"; do
    echo "Terminating processes matching: $pattern"
    pkill -f "$pattern"

    # 检查是否成功终止
    if [ $? -eq 0 ]; then
        echo "Successfully terminated processes containing: $pattern"
    else
        echo "No matching processes found or failed to terminate for: $pattern"
    fi
done

echo "Process termination completed."
