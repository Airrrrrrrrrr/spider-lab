"""Spider Lab 现代爬虫与数据工程进阶实验室。"""

import sys

if sys.version_info < (3, 12):
    cur_ver = sys.version.split()[0]
    raise RuntimeError(
        f"检测到当前解释器版本为 Python {cur_ver}（可能误用了全局工作环境 Python 3.6.8）。\n"
        "请使用 'uv run python ...' 运行本仓库代码，以确保在隔离的 Python 3.12 虚拟环境中执行！"
    )

__version__ = "0.1.0"
