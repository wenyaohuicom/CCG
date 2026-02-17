# CCG - Claude-Codex-Gemini

将用户的任务委派给 Codex CLI 或 Gemini CLI 执行。

## 使用说明

用户输入 `/CCG <任务描述>` 时，按以下流程执行：

### 1. 检查配置

```bash
python3 ~/.claude/skills/CCG/scripts/configure.py --check
```

如果未配置，使用 AskUserQuestion 向用户收集：
- API 密钥
- Codex 端点（默认 `https://cc.orcai.cc/openai`）
- Gemini 端点（默认 `https://cc.orcai.cc/gemini`）
- 模型选择（默认 Codex: `gpt-5.3-codex`，Gemini: `gemini-3-pro-preview`）

然后运行：
```bash
python3 ~/.claude/skills/CCG/scripts/configure.py --setup --codex-url "URL" --codex-key "KEY" --gemini-url "URL" --gemini-key "KEY"
```

### 2. 判断使用哪个 Agent

根据用户输入判断：
- 明确说了"codex"或"Codex" → 用 Codex
- 明确说了"gemini"或"Gemini" → 用 Gemini
- 没指定 → 使用 AskUserQuestion 让用户选择

### 3. 执行任务

**Codex：**
```bash
python3 ~/.claude/skills/CCG/scripts/codex_bridge.py --prompt "$ARGUMENTS" --workdir "$(pwd)" --full-auto --stream
```

**Gemini：**
```bash
python3 ~/.claude/skills/CCG/scripts/gemini_bridge.py --prompt "$ARGUMENTS" --workdir "$(pwd)" --yolo --stream
```

### 4. 返回结果

将 agent 的输出结果总结给用户。
