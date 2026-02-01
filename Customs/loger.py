# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-28 01:18:11
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-01 10:57:15

import traceback
import datetime
import logging
import sys

# 1. 配置日志格式
# %(asctime)s 自动处理 datetime
# %(levelname)s 自动处理级别名称
# %(message)s 自动处理消息内容
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt=DATE_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout) # 确保输出到标准输出，方便 adb logcat 查看
    ]
)

logr = logging.getLogger(__name__)
# loger = logging.getLogger(__name__)

# regiong loginfo
class LogInfo:
    def __init__(self, show_time: bool = True):
        # 使用常量定义格式，避免实例属性被误改
        self.show_time = show_time
        # {level} 和 {message} 是占位符
        self.log_format = (
            "[{time}] {level}: {message}" if show_time else "{level}: {message}"
        )

    def __emit(self, level: str, message: str, ex: Exception = None):
        """内部统一处理日志输出"""
        # 1. 处理时间
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 2. 处理错误堆栈 (针对你之前的 traceback 需求)
        full_message = str(message)
        if ex is not None:
            # 获取完整堆栈并拼接到消息后面
            error_stack = traceback.format_exc()
            full_message = (
                f"{full_message}\nException: {ex}\nStack Trace:\n{error_stack}"
            )

        # 3. 格式化最终字符串 (使用关键字参数修复原有 bug)
        log_str = self.log_format.format(
            time=now, level=level.upper(), message=full_message
        )

        # 4. 实际执行打印 (或者写入文件)
        print(log_str)
        return log_str

    def info(self, message: str):
        return self.__emit("info", message)

    def debug(self, message: str):
        return self.__emit("debug", message)

    def error(self, message: str, ex: Exception = None):
        """支持传入 Exception 对象以自动记录堆栈"""
        return self.__emit("error", message, ex=ex)


# endregion

# logr = LogInfo(show_time=True)
