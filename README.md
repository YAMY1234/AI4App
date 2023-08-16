# AI Spider Project Structure

以下是`AI4App`项目的结构：

```
ai_spider/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py       # 包含全局配置、例如headers、timeout、retry等
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── general.py       # 包含一些常见的工具函数，例如URL验证等
│   │   └── regex_parser.py  # 正则匹配方法，spiders在对于deadline等文本数据进行处理的时候，可以写在这里从而减少spiders的负担
│   ├── spiders/
│   │   ├── __init__.py
│   │   ├── base_spider.py   # 基础爬虫类，所有的学校爬虫都继承这个
│   │   ├── school1.py       # school1的爬虫实现，继承base_spider并重写对应方法
│   │   ├── school2.py       # school2的爬虫实现，....
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── db.py            # 数据库相关操作
│   │   └── logger.py        # 日志处理
│   ├── data/                # 存放中间数据和最终结果
│   └── main.py              # 项目的入口，从这里开始运行
```

## 使用指南

1. **配置**: `config/settings.py`中存储后续可能需要的配置，如请求头。
2. **工具**: `tools`目录下可以书写一些常用的工具函数和正则匹配方法，在base_spider当中调用。
3. **爬虫**: 所有的学校爬虫都应继承`spiders/base_spider.py`中的基础爬虫类。每个学校的爬虫都有自己的文件，例如`school1.py`和`school2.py`。
4. **工具**: `utils`目录包含一些常用的工具，例如数据库操作和日志处理。
5. **数据**: 所有的中间数据和最终结果都存放在`data`目录中。
6. **运行**: `main.py`：主程序入口，可以选择对于不同的学校进行爬取。

