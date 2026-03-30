# -*- coding: utf-8 -*-
# @Author: JogFeelingVI
# @Date:   2026-03-27 13:34:06
# @Last Modified by:   JogFeelingVI
# @Last Modified time: 2026-03-29 12:20:40
import threading

from mcp.server.fastmcp import FastMCP

mcp = FastMCP(f"LOTTER-MCP-SSE")

class mcpserver:
    flg = "LOTTER-MCP-SSE"
    def __init__(self, name:str="mcp_server"):
        # mcp.name = f"{self.flg} {name}"
        print(f'{mcp.name}')
        
    @mcp.tool()
    def get_gui_status(self) -> str:
        return "Flet Window status: active"
    
    def run_mcp_server(self):
        def run_sse():
            try:
                print("Trying to start MCP SSE service...")
                # 你可以指定端口，防止冲突
                mcp.run(transport="sse", port=8000) 
            except Exception as e:
                print(f"MCP Service startup failed: {e}")
        print(f"Starting MCP SSE service in a separate thread...")
        threading.Thread(target=run_sse, daemon=True).start()