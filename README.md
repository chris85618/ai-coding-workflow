# AI Coding Workflow Configuration

> **Single Source of Truth** for agentic development workflow orchestration.

本目錄管理跨 AI 工具鏈的統一開發流程配置，整合四個子模組為一套端對端迭代管線。

## Architecture

```
ai_coding/
├── AGENTS.md        # 統一配置：workflow + agent instructions + skill routing
├── .gitignore       # 排除生成物
└── skills/
    ├── everything-claude-code/   # ECC — 開發護欄、hooks、agents
    ├── gstack/                   # gstack — 工作流引擎（QA、ship、review）
    ├── understand-anything/      # Understand Anything — 程式碼理解、知識圖譜
    └── skillfortify/             # SkillFortify — 供應鏈安全、SBOM
```

## Workflow Pipeline

所有開發任務遵循 6 階段序列式迭代管線（完整定義見 [AGENTS.md](./AGENTS.md)）：

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

所有開發任務遵循完整管線，**無簡化路徑**。

## Symlink Setup

```bash
# Antigravity (Gemini)
# Windows: mklink "C:\Users\<user>\.gemini\GEMINI.md" "C:\Users\<user>\.setup\ai_coding\AGENTS.md"
# Linux:   ln -sf ~/.setup/ai_coding/AGENTS.md ~/.gemini/GEMINI.md

# Claude Code (按需)
# ln -sf ~/.setup/ai_coding/AGENTS.md <project>/CLAUDE.md
```

## Quick Start

```bash
# 1. Clone（從 repo 根目錄 .setup）: `git submodule update --init --recursive`
# 2. 建立 symlink（見上方）
# 3. 驗證環境
```

## Key Files

| File | Purpose |
|------|---------|
| [AGENTS.md](./AGENTS.md) | 統一配置：完整管線定義、審查維度、HITL 閘門、skill routing、agent instructions |
