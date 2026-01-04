# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-01-04 02:53:12
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-01-04 03:11:36


import secrets


class randomData:
    """根据设置随机选择数据"""

    name = "randomData"

    def __init__(self, seting):
        if not isinstance(seting, dict):
            raise ValueError("Setting must be a dictionary.")
        self.setting = seting
        # 自动发现配置中的 keys，而不是硬编码 ("pa", "pb", "pc")
        # 过滤掉非字典项（比如 "note" 字段）
        self.targets = [k for k, v in seting.items() if isinstance(v, dict)]

    def select(self, seting):
        if seting is None and not isinstance(seting, dict):
            return None
        pmin = seting.get("range_start", 0)
        pmax = seting.get("range_end", 100)
        plen = seting.get("count", 6)  # 默认选择6个数字
        if plen > pmax - pmin + 1:
            return None
        return sorted(secrets.SystemRandom().sample(range(pmin, pmax + 1), plen))

    def get_pabc(self):
        """
        获取随机数据
        :return: 返回随机数据
        """
        result = {}
        for key in self.targets:
            # 获取对应 key 的配置
            item_config = self.setting.get(key)
            # 生成数据
            numbers = self.select(item_config)

            if numbers is not None:
                result[key] = numbers

        return result

    def get_exp(self, abc:dict=None):
        """获取格式化的随机数据字符串表示"""
        if abc is None:
            pabc = self.get_pabc()
        else:
            pabc = abc
        exp_parts = []
        for key in self.targets:
            numbers = pabc.get(key)
            if numbers is not None:
                numbers_str = [f"{x:02}" for x in numbers]
                exp_parts.append(" ".join(numbers_str))
        return " + ".join(exp_parts)
    
    @staticmethod
    def generate_secure_string(length=8):
        # 定义候选字符集：大写字母 + 小写字母 + 数字
        alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        
        # 使用 SystemRandom 生成指定长度的随机字符串
        # secrets.choice 比 random.choice 更安全，适合生成密码或令牌
        secure_str = ''.join(secrets.choice(alphabet) for _ in range(length))
        
        return secure_str
