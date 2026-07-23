# BuildFLET

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Flet](https://img.shields.io/badge/Flet-Latest-007ACC.svg)](https://flet.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](#)

基于 [Flet](https://flet.dev/)（Flutter for Python）开发的跨平台应用程序项目。集成了 GitHub Actions 自动化构建工作流，支持一键将 Python 应用打包生成适用于 Windows、Linux、macOS、Android (APK) 及嵌入式系统 (IPK) 的安装包。

---

## 🚀 项目特性

- **跨平台 GUI**：基于 Flet 框架，只需编写 Python 代码即可运行在桌面端与移动端。
- **云端自动化构建**：借助 GitHub Actions 进行多平台交叉编译，无需在本地配置复杂的 Android SDK 或 Flutter 构建环境。
- **高效数据处理**：集成 Upstash Redis 数据库支持与 MessagePack（msgpack）高性能二进制数据序列化。
- **精简架构**：*（已全面移除 MCP 支持）*，依赖关系更清晰，专注于应用核心逻辑与打包流程。

---

## 🛠️ 技术栈与依赖

本项目基于 Python 运行环境，主要依赖如下：

- **核心 UI 框架**：`flet`
- **网络通信**：`requests`
- **云端数据库/缓存**：`upstash_redis`
- **数据序列化**：`msgpack`
- **图像处理**：`Pillow`

> 📌 **依赖说明**：项目已不再包含 `mcp` (Model Context Protocol) 及其相关组件。

---

## 📁 项目目录结构

```text
BuildFLET/
├── .github/
│   └── workflows/        # GitHub Actions 各平台构建脚本
├── Customs/              # 自定义 UI 组件与视图逻辑
├── assets/               # 应用静态资源文件（图标、图片等）
├── storage/
│   └── data/            # 本地数据存储与缓存目录
├── main.py               # 项目主程序入口文件
├── pyproject.toml        # 项目依赖与配置文件
└── README.md             # 项目说明文档
