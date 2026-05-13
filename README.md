# AI Coding Workflow Configuration

> **Single Source of Truth** for agentic development workflow orchestration.

本目錄管理跨 AI 工具鏈的統一開發流程配置，整合四個子模組為一套端對端迭代管線。

## Architecture

```
ai_coding/
├── GEMINI.md        # Antigravity agent 配置（symlink → ~/.gemini/GEMINI.md）
├── CLAUDE.md        # Claude Code / ECC 編排規則
├── AGENTS.md        # 跨工具共用 agent 指令
├── WORKFLOW.md      # 6 階段迭代管線定義（825 行）
├── .gitignore       # 排除生成物
└── skills/
    ├── everything-claude-code/   # ECC — 開發護欄、hooks、agents
    ├── gstack/                   # gstack — 工作流引擎（QA、ship、review）
    ├── understand-anything/      # Understand Anything — 程式碼理解、知識圖譜
    └── skillfortify/             # SkillFortify — 供應鏈安全、SBOM
```

## Workflow Pipeline

所有開發任務遵循 6 階段序列式迭代管線（完整定義見 [WORKFLOW.md](./WORKFLOW.md)）：

```
Phase 0   [自動] 環境啟動
Phase 1   /understand (既有 codebase)
Phase 2   /office-hours → /plan-ceo-review
─── 迭代管線 ───
Stage 3   技術規劃           → HITL ✅
Stage 4   演算法 + 安全審計  → HITL ✅
Stage 5   OOAD + 安全審計    → HITL ✅
Stage 6   形式化驗證設計     → HITL ✅
Stage 7   BDD/ATDD + 驗證    → HITL ✅
Stage 8   TDD + 測試 + 修復  → HITL ✅
─── 管線結束 ───
Phase 9   /ship → /land-and-deploy → /canary
Phase 10  /retro → /understand → /evolve
```

**精簡路徑（小型任務）：** Phase 0 → Phase 1 → Phase 2 → Stage 3 → Stage 8 → Phase 9 → Phase 10

## Quick Start

```bash
# 1. Clone（從 repo 根目錄 .setup/）: `git submodule update --init --recursive`
# 2. 建立 symlink
# 3. 驗證環境
```

## Key Files

| File | Purpose |
|------|---------|
| [WORKFLOW.md](./WORKFLOW.md) | 完整管線定義、審查維度、HITL 閘門 |
| [GEMINI.md](./GEMINI.md) | Antigravity 專用配置、skill routing |
| [CLAUDE.md](./CLAUDE.md) | Claude Code 編排、測試指令 |
| [AGENTS.md](./AGENTS.md) | 跨工具共用安全基線、架構摘要 |
