---
name: CCG
description: "Claude-Codex-Gemini: 将编码任务委派给 Codex CLI 和 Gemini CLI 作为独立 agent 执行。支持自动依赖检测安装、交互式配置、多轮会话、沙箱隔离、流式输出。默认模型: gpt-5.3-codex / gemini-3-pro-preview。"
---

# CCG - Claude-Codex-Gemini

将编码任务委派给 **Codex CLI** (OpenAI) 和 **Gemini CLI** (Google) 作为独立 agent 执行。

## 首次使用设置（重要）

使用任何 CCG 命令前，必须先检查是否已配置：

```bash
python3 skills/CCG/scripts/configure.py --check
```

如果输出 `"configured": false`，需要执行以下设置流程：

### 第 1 步：检查 CLI 安装

```bash
bash skills/CCG/scripts/setup_check.sh
```

自动检测并安装缺失的 CLI 工具（Codex CLI、Gemini CLI）。

### 第 2 步：向用户询问配置

使用 AskUserQuestion 向用户收集以下信息：

1. **API Key**："请提供你的 API 密钥（用于 Codex 和 Gemini 端点）"
2. **Codex 端点**："Codex API 端点地址？"（默认：`https://cc.orcai.cc/openai`）
3. **Gemini 端点**："Gemini API 端点地址？"（默认：`https://cc.orcai.cc/gemini`）
4. **是否更换默认模型**：Codex 默认 `gpt-5.3-codex`，Gemini 默认 `gemini-3-pro-preview`

如果用户提供同一个 API key，则 Codex 和 Gemini 共用。

### 第 3 步：保存配置

```bash
python3 skills/CCG/scripts/configure.py --setup \
  --codex-url "端点地址" \
  --codex-key "密钥" \
  --codex-model "模型名" \
  --gemini-url "端点地址" \
  --gemini-key "密钥" \
  --gemini-model "模型名"
```

配置保存到 `~/.ccg/config.json`，Codex CLI 配置自动写入 `~/.codex/config.toml`。

## 何时使用哪个 Agent

- **Codex**：代码生成、Bug 修复、重构。支持沙箱隔离和图片附件。适合 OpenAI 模型（gpt-5.3-codex、o3、o4-mini）。
- **Gemini**：代码分析、文档生成、大上下文任务。支持 YOLO（自动批准）模式。适合 Google 模型（gemini-3-pro-preview）。

## 调用 Codex

```bash
python3 skills/CCG/scripts/codex_bridge.py \
  --prompt "你的任务描述" \
  --workdir /项目路径 \
  --full-auto
```

### Codex 参数

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--prompt` | `-p` | **必填**。任务提示词 |
| `--workdir` | `-C` | 工作目录 |
| `--sandbox` | `-s` | 沙箱模式：`read-only`、`workspace-write`、`danger-full-access` |
| `--model` | `-m` | 覆盖模型（默认从配置读取） |
| `--full-auto` | | 自动批准 + workspace-write |
| `--image` | `-i` | 附加图片文件，可重复 |
| `--session-id` | | 恢复上一次会话 |
| `--stream` | | 实时流式输出 |
| `--verbose` | `-v` | 输出调试信息到 stderr |

## 调用 Gemini

```bash
python3 skills/CCG/scripts/gemini_bridge.py \
  --prompt "你的任务描述" \
  --workdir /项目路径 \
  --yolo
```

### Gemini 参数

| 参数 | 缩写 | 说明 |
|------|------|------|
| `--prompt` | `-p` | **必填**。任务提示词 |
| `--workdir` | `-C` | 工作目录（作为子进程 cwd） |
| `--sandbox` | `-s` | 启用沙箱模式 |
| `--yolo` | `-y` | 自动批准所有操作 |
| `--model` | `-m` | 覆盖模型（默认从配置读取） |
| `--resume` | `-r` | 恢复会话（`latest` 或索引号） |
| `--stream` | | 实时流式输出 |
| `--verbose` | `-v` | 输出调试信息到 stderr |

## 输出格式

两个桥接脚本都返回 JSON（不使用 `--stream` 时）：

```json
{
  "exit_code": 0,
  "session_id": "session_abc123",
  "message_count": 5,
  "messages": [ ... ],
  "stderr": ""
}
```

使用 `--stream` 时，agent 文本实时输出到 stdout。

## 查看 / 更新配置

```bash
python3 skills/CCG/scripts/configure.py --show
python3 skills/CCG/scripts/configure.py --setup --codex-model gpt-5.3-codex
```

## 默认模型

| Agent | 默认模型 | 默认端点 |
|-------|---------|---------|
| Codex | gpt-5.3-codex | cc.orcai.cc/openai |
| Gemini | gemini-3-pro-preview | cc.orcai.cc/gemini |

## 使用技巧

1. 始终指定 `--workdir` 确保 agent 在正确的项目目录中操作。
2. 使用 `--stream` 查看实时进度。
3. 需要修改文件时，使用 `--full-auto`（Codex）或 `--yolo`（Gemini）。
4. 保存输出中的 `session_id` 以便恢复多轮会话。
5. 桥接脚本自动读取 `~/.ccg/config.json`，无需手动导出环境变量。
