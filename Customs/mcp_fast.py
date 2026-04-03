# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-27 13:34:06
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-04-03 01:04:27

"""MCP Fast 服务模块。

本模块提供基于 FastMCP 框架的 Server-Sent Events (SSE) 服务实现，
用于管理彩票相关的计算任务和查询操作。

主要功能：
    - 提供彩票信息查询工具
    - 提供任务状态监控工具
    - 管理 MCP 服务器的生命周期
    - 动态端口分配和健康检查
"""

import asyncio
import socket

import uvicorn
from mcp.server.fastmcp import FastMCP

from . import datamodle as dm
from .lotterMange import Lotter_Data, LotteryManager

mcp = FastMCP("LOTTER-MCP-SSE")
server_instance = None
app_state = LotteryManager()


@mcp.tool()
def check_calc_status() -> dm.TaskStatus:
    """实时获取后台计算任务的进度。

    此工具用于查询当前计算任务的状态。AI 客户端应定期调用此工具
    以监控长时间运行的计算任务的进度。

    返回状态说明：
        - idle: 准备就绪，可以开始新的计算。
        - calculating: 正在努力计算中，请引导用户稍等。
        - done: 计算已完成，现在可以调用获取结果的工具。
        - timeout: 计算时间过长已自动停止。
        - error: 内部逻辑出错。

    Returns:
        dm.TaskStatus: 包含当前状态和已耗时间的任务状态对象。
            - status (str): 当前任务状态
            - elapsed_time (float): 已耗费的时间（秒）
    """
    current_status = getattr(app_state, "status", "idle")
    current_elapsed = getattr(app_state, "elapsed_time", 0.0)

    # 直接返回模型实例，FastMCP 会自动处理序列化
    return dm.TaskStatus(status=current_status, elapsed_time=current_elapsed)


@mcp.tool()
def get_supported_lotteries() -> dm.LotteryLibrary:
    """获取系统支持的所有彩票预设及其详细规则。

    此工具返回系统支持的所有彩票类型的完整信息，包括每种彩票的
    球组配置、抽取数量等详细规则。AI 应该在开始任何计算前调用此工具，
    以确保获取正确的彩票名称和参数结构。

    Returns:
        dm.LotteryLibrary: 包含所有支持彩票信息的库对象。
            包含列表中的每个元素包括：
            - name (str): 彩票名称
            - description (str): 彩票描述
            - rules (List[BallGroup]): 球组规则列表
                * group_id (str): 球组标识符
                * range (List[int]): 球号范围 [最小, 最大]
                * count (int): 需要抽取的球数
    """
    all_lotteries = []

    # 动态解析你的 Lotter_Data 字典
    for name, info in Lotter_Data.items():
        ball_groups = []

        # 寻找所有规则对 (例如 PA 和 PA_K)
        potential_keys = sorted(
            [k for k in info.keys() if not k.endswith("_K") and k != "description"]
        )

        for key in potential_keys:
            count_key = f"{key}_K"
            if (
                count_key in info
                and isinstance(info[key], list)
                and len(info[key]) == 2
            ):
                # 提取组名，例如从 "PA" 提取 "A"
                group_id = key[1:] if len(key) > 1 and key[0] in ("P", "S") else key

                # 创建球组模型
                ball_groups.append(
                    dm.BallGroup(
                        group_id=group_id, range=info[key], count=info[count_key]
                    )
                )

        # 创建单种彩票模型
        all_lotteries.append(
            dm.LotteryInfo(
                name=name,
                description=info.get("description", "无描述"),
                rules=ball_groups,
            )
        )

    # 返回结构化库对象
    return dm.LotteryLibrary(lotteries=all_lotteries)


async def run_mcp_server():
    """启动 MCP SSE 服务器。

    在独立的异步任务中启动 FastMCP 驱动的 SSE 服务器。自动处理
    端口冲突，当指定端口被占用时会递增尝试其他端口。捕获并优雅
    处理 SSE 连接中断。

    Global:
        server_instance: 全局服务器实例引用，用于后续关闭操作。
        app_state: 应用状态管理器，包含服务器地址和端口配置。

    Note:
        - 日志级别设置为 "critical" 以减少输出噪音
        - ASGI 消息错误视为正常的 SSE 中断
        - 服务关闭时会清理状态

    Raises:
        Exception: 捕获并记录非 SSE 相关的异常，但不会重新抛出。
    """
    print("Starting MCP SSE service in a separate thread...")
    for tool in mcp._tool_manager.list_tools():
        print(f"Registered tool: {tool.name}")
    global server_instance
    # 获取 FastMCP 内部生成的 Starlette app
    host = app_state.server_address["host"]
    port = app_state.server_address["port"]

    while is_port_in_use(host, port):
        port += 1
        app_state.setting_port(port)
        await asyncio.sleep(0.1)  # 避免过快循环
    try:
        app = mcp.sse_app()
        config = uvicorn.Config(app, host=host, port=port, log_level="critical")
        server_instance = uvicorn.Server(config)
        await server_instance.serve()
        print(f"MCP server address: {app_state.server_address['address']}")
    except Exception as e:
        error_msg = str(e)
        if "ASGI message" in error_msg:
            # 这是正常的 SSE 中断，不需要当作错误处理
            print("MCP Server: SSE connections closed gracefully.")
        else:
            print(f"MCP Server stopped with message: {e}")
    finally:
        # 确保状态被清理
        print("MCP Server: Shutdown complete.")


async def stop_mcp_server():
    """优雅关闭 MCP 服务器。

    安全地关闭全局服务器实例，等待其完全停止（最多 3 秒）。
    如果服务器未在运行，则输出相应提示信息。

    Global:
        server_instance: 全局服务器实例引用。

    Note:
        - 最多等待 30 次，每次间隔 0.1 秒（总计 3 秒）
        - 会在控制台输出关闭状态信息
    """
    global server_instance
    if server_instance and server_instance.started:
        print("Shutting down MCP server...")
        server_instance.should_exit = True
        for _ in range(30):
            if not server_instance.started:
                break
            await asyncio.sleep(0.1)
        print("MCP service successfully detached.")
    else:
        print("Server is not running.")


def is_port_in_use(host, port):
    """检查指定的主机和端口是否被占用。

    Args:
        host (str): 要检查的主机地址（如 '127.0.0.1'）。
        port (int): 要检查的端口号。

    Returns:
        bool: 如果端口被占用返回 True，否则返回 False。

    Note:
        使用 TCP 连接尝试来判断端口是否可用。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        socke_status = s.connect_ex((host, port)) == 0
        return socke_status


async def is_server_healthy():
    """检查 MCP 服务器是否正常运行。

    执行两级健康检查：
    1. 检查内存中的服务器实例状态
    2. 通过网络套接字连接探测服务器可达性

    Global:
        server_instance: 全局服务器实例。
        app_state: 应用状态管理器，包含服务器地址配置。

    Returns:
        bool: 如果服务器健康运行返回 True，否则返回 False。

    Note:
        - 网络探测超时时间为 0.5 秒
        - 任何连接异常都会被记录并返回 False
        - 在线程池中执行网络操作以避免阻塞事件循环
    """
    global server_instance

    # 1. 首先检查内存中的实例状态
    if server_instance is None or not server_instance.started:
        return False

    # 2. 网络探测
    host = app_state.server_address["host"]
    port = app_state.server_address["port"]

    try:

        def probe():
            with socket.create_connection((host, port), timeout=0.5):
                return True

        # 只要返回了状态码（哪怕是 405 Method Not Allowed 也行），
        # 就说明 HTTP 服务已经起来了
        return await asyncio.to_thread(probe)
    except Exception as ex:
        print(f"Health check failed: {ex}")
        return False


def register_mcp_tools():
    """注册 MCP 工具。

    此函数用于集中管理 MCP 工具的注册逻辑。当前工具已通过
    @mcp.tool() 装饰器自动注册，此函数可用于将来添加更多工具。

    Note:
        目前包含的工具：
        - check_calc_status: 查询计算任务状态
        - get_supported_lotteries: 获取支持的彩票列表
    """
    # 这里可以添加更多工具注册函数
    