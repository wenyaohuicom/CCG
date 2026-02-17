# CCG - Claude-Codex-Gemini

让 Claude Code 将编码任务委派给 **Codex CLI** (OpenAI) 和 **Gemini CLI** (Google) 作为独立 agent 执行。

## 功能

- 统一接口调度 Codex 和 Gemini 两个编码 agent
- 自动检测并安装 CLI 工具（Codex CLI、Gemini CLI）
- 首次使用交互式配置：询问 API 密钥、端点地址、模型选择
- 结构化 JSON 输出，支持会话跟踪和多轮对话
- 流式和批量输出模式
- 沙箱隔离支持
- 配置和脚本统一存储在 `~/.ccg/`，无需手动导出环境变量

## 安装

```
/plugin marketplace add wenyaohuicom/CCG
/plugin install CCG@CCG
```

## 配置

首次使用时，Claude Code 会自动询问以下信息：

- **API 密钥**（Codex 和 Gemini 共用）
- **Codex 端点**（默认：`https://cc.orcai.cc/openai`）
- **Gemini 端点**（默认：`https://cc.orcai.cc/gemini`）
- **模型选择**（默认：`gpt-5.3-codex` / `gemini-3-pro-preview`）

## 默认 Agent 配置

| Agent | 默认模型 | 默认端点 |
|-------|---------|---------|
| Claude Code | Claude Opus 4.6 | Anthropic |
| Codex CLI | gpt-5.3-codex | cc.orcai.cc/openai |
| Gemini CLI | gemini-3-pro-preview | cc.orcai.cc/gemini |

## 使用方式

### 斜杠命令

```
/CCG 用 Codex 修复 main.py 里的 bug
/CCG 让 Gemini 重构数据库模块
```

### 自然语言

直接对 Claude Code 说：

- "用 Codex 修复 main.py 里的 bug"
- "让 Gemini 重构数据库模块"
- "用 Codex full-auto 模式给 utils.py 写测试"

## 系统要求

- Linux
- Node.js 18+
- npm
- Python 3.10+

## 许可证

MIT
