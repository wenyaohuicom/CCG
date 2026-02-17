# CCG - Claude-Codex-Gemini

让 Claude Code 将编码任务委派给 **Codex CLI** (OpenAI) 和 **Gemini CLI** (Google) 作为独立 agent 执行。

## 功能

- 统一接口调度 Codex 和 Gemini 两个编码 agent
- 自动检测并安装 CLI 工具（Codex CLI、Gemini CLI）
- 首次使用交互式配置：询问 API 密钥、端点地址、模型选择
- 结构化 JSON 输出，支持会话跟踪和多轮对话
- 流式和批量输出模式
- 沙箱隔离支持
- 配置存储在 `~/.ccg/config.json`，无需手动导出环境变量

## 安装

### 方式一：Plugin 命令安装（推荐）

```bash
/plugin marketplace add wenyaohuicom/CCG
/plugin install CCG@CCG
```

### 方式二：手动安装

```bash
git clone https://github.com/wenyaohuicom/CCG.git
cd CCG
bash install.sh
```

## 配置

首次使用时，Claude Code 会自动询问你以下信息：

- **API 密钥**（Codex 和 Gemini 共用）
- **Codex 端点**（默认：`https://cc.orcai.cc/openai`）
- **Gemini 端点**（默认：`https://cc.orcai.cc/gemini`）
- **模型选择**（默认：`gpt-5.3-codex` / `gemini-3-pro-preview`）

手动配置：

```bash
python3 scripts/configure.py --setup \
  --codex-url https://cc.orcai.cc/openai \
  --codex-key 你的密钥 \
  --gemini-url https://cc.orcai.cc/gemini \
  --gemini-key 你的密钥
```

查看当前配置：

```bash
python3 scripts/configure.py --show
```

## 文件结构

```
CCG/
├── .claude-plugin/
│   └── marketplace.json          # Plugin 注册信息
├── .claude/
│   └── skills/
│       └── CCG/
│           ├── SKILL.md          # Skill 定义（Claude Code 读取）
│           └── scripts/          # 桥接脚本和工具
│               ├── configure.py      # 配置管理器
│               ├── codex_bridge.py   # Codex CLI 桥接
│               ├── gemini_bridge.py  # Gemini CLI 桥接
│               └── setup_check.sh    # 依赖检测和自动安装
├── scripts/                      # 脚本（手动安装用）
├── install.sh                    # 手动安装脚本
├── SKILL.md                      # Skill 定义（手动安装用）
└── README.md                     # 本文件
```

## 默认 Agent 配置

| Agent | 默认模型 | 默认端点 |
|-------|---------|---------|
| Claude Code | Claude Opus 4.6 | Anthropic |
| Codex CLI | gpt-5.3-codex | cc.orcai.cc/openai |
| Gemini CLI | gemini-3-pro-preview | cc.orcai.cc/gemini |

## 使用方式

安装配置完成后，Claude Code 会自动识别 CCG skill。你可以直接说：

- "用 Codex 修复 main.py 里的 bug"
- "让 Gemini 重构数据库模块"
- "用 Codex full-auto 模式给 utils.py 写测试"

### 手动调用

```bash
# Codex
python3 scripts/codex_bridge.py -p "修复这个 bug" -C /项目路径 --full-auto

# Gemini
python3 scripts/gemini_bridge.py -p "重构这个模块" -C /项目路径 --yolo
```

## 系统要求

- Linux
- Node.js 18+
- npm
- Python 3.8+

## 许可证

MIT
