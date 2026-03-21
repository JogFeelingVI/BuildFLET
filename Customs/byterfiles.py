# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-21 11:05:27
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-21 13:34:23
import base64
import enum
import pickle
from pathlib import Path
from typing import Any, Optional, Tuple, Union


class ResultCode(enum.Enum):
    ERROR = -1
    DONE = 1


class BinaryConverter:
    """处理对象与二进制/Base64字符串之间的转换工具类"""

    @staticmethod
    def save_binary(
        path: Union[str, Path], obj: Any
    ) -> Tuple[ResultCode, Optional[Exception]]:
        """将对象序列化并保存到文件"""
        try:
            with open(path, "wb") as f:
                pickle.dump(obj, f)
            return ResultCode.DONE, None
        except Exception as ex:
            return ResultCode.ERROR, ex

    @staticmethod
    def load_binary(path: Union[str, Path]) -> Tuple[ResultCode, Any]:
        """从文件读取并反序列化对象"""
        try:
            with open(path, "rb") as f:
                data = pickle.load(f)
            return ResultCode.DONE, data
        except Exception as ex:
            return ResultCode.ERROR, ex

    @staticmethod
    def to_base64_str(obj: Any) -> Tuple[ResultCode, str]:
        """将对象转换为 Base64 字符串（安全传输专用）"""
        try:
            # pickle 得到 bytes -> base64 编码 -> 转为 utf-8 字符串
            binary_data = pickle.dumps(obj)
            base64_str = base64.b64encode(binary_data).decode("utf-8")
            return ResultCode.DONE, base64_str
        except Exception as ex:
            return ResultCode.ERROR, str(ex)

    @staticmethod
    def from_base64_str(b64_str: str) -> Tuple[ResultCode, Any]:
        """将 Base64 字符串还原为对象"""
        try:
            # 字符串转回 bytes -> base64 解码 -> pickle 加载
            binary_data = base64.b64decode(b64_str.encode("utf-8"))
            obj = pickle.loads(binary_data)
            return ResultCode.DONE, obj
        except Exception as ex:
            return ResultCode.ERROR, str(ex)
