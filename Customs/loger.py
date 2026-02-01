# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-28 01:18:11
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-02-01 01:04:25

import logging
import sys
import traceback

# 显式添加一个流处理器，指向 sys.stdout（标准输出）
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)

logging.basicConfig(
    level=logging.INFO,  # 设置为 DEBUG 可以看到最细碎的日志
    handlers=[handler],
    format="%(levelname)s: %(message)s",
)

loger = logging.getLogger(__name__)

tbackexec = traceback.format_exc
