├── ai_spider/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py       # 包含全局配置、例如headers、timeout、retry等
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── general.py       # 包含一些常见的工具函数，例如URL验证等
│   │   └── regex_parser.py  # 正则匹配方法
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── base_spider.py   # 基础爬虫类，所有的学校爬虫都继承这个
│   │   ├── school1.py       # school1的爬虫实现
│   │   ├── school2.py       # school2的爬虫实现
│   │   └── ...              # 其他学校的爬虫实现
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── db.py            # 数据库相关操作
│   │   └── logger.py        # 日志处理
│   ├── data/                # 存放中间数据和最终结果
│   └── main.py              # 项目的入口，从这里开始运行