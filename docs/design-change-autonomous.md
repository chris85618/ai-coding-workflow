# Design Change: Autonomous Execution + DAG State Absorption

> **Triggered by**: User change request 2026-05-14T18:39
> **Change Type**: MAJOR (blast_radius=23, cross_stage=6+)
> **Last Updated**: 2026-05-14T18:40+08:00

---

## 1. Change Summary

| # | Change | From | To |
|---|--------|------|----|
| 1 | Execution model | HITL gates at every stage exit | Fully autonomous single-run; AI makes all assumptions; user corrects via subsequent runs |
| 2 | State persistence | workflow-state.md file | LangGraph DAG checkpointing (internal state) |
| 3 | Output model | Document-driven (unchanged) | Still outputs Markdown docs to `{target_repo}/docs/`; reads same docs on new projects |

---

## 2. Full-Chain Impact Trace

### 2.1 Affected BG

| ID | Current | Changed To | Impact |
|----|---------|-----------|--------|
| BG-003 | "透過 HITL 閘門最大化自主代理可靠性" | "透過全自主 DAG 執行最大化開發效率，錯誤由使用者後續修正" | Meaning shift: reliability via gates → efficiency via autonomy |

### 2.2 Affected FEA

| ID | Current | Changed To |
|----|---------|-----------|
| FEA-005 | "雙代理迭代協議...含...HITL 閘門" | "雙代理迭代協議...含自主收斂閘門 (auto-gate)" |
| FEA-010 | "狀態持久化與恢復...workflow-state.md" | "狀態持久化與恢復...LangGraph checkpoint" |

### 2.3 Affected FR

| ID | Current | Changed To | Rationale |
|----|---------|-----------|-----------|
| FR-013 | "不動點判定...REACHED→觸發HITL; DIVERGING→觸發HITL" | "不動點判定...REACHED→自動PASS; DIVERGING→記錄warning後自動PASS" | No human gate |
| FR-014 | "HITL 收斂確認（AI-first 模型）...HITL 閘門僅在AI自主達到不動點後觸發" | **SUPERSEDED** → FR-014-v2: "自主收斂確認: 不動點達成後自動PASS, 結果記入docs/" | No HITL involvement |
| FR-019 | "workflow-state.md 作為WBS單一事實來源" | FR-019-v2: "LangGraph DAG checkpoint 作為執行狀態來源; 管線結果仍輸出至docs/" | File → DAG |
| FR-021 | "中斷恢復協議...偵測到workflow-state.md" | FR-021-v2: "中斷恢復: LangGraph checkpoint restore; 不需外部state file" | File → DAG |

### 2.4 Affected UC

| ID | Current HITL Reference | Changed To |
|----|----------------------|-----------|
| UC-001 | "主要流程...ECC SessionStart...路徑判斷" | Unchanged (no HITL in main flow) |
| UC-003 | "HITL 閘門" in main flow, "HITL 選擇 [1] 繼續" in alt flow | "auto-gate" in main flow; alt flow removed (AI decides autonomously) |
| UC-010 | "HITL 選擇 [1] 從斷點繼續 / [2] 執行其他 / [3] 重置" | "自動從 checkpoint 恢復; 無HITL選擇" (LangGraph checkpoint handles this) |

### 2.5 Affected CLS (Domain Model)

| ID | Class | Change |
|----|-------|--------|
| CLS-001 | Pipeline | `advance(hitlConfirmation)` → `advance()` (no parameter; auto-advance) |
| CLS-003 | IterationLoop | `hitl_gate() → HitlChoice` → `auto_gate() → GateDecision` (always PASS at fixed point) |
| CLS-013 | WorkflowResumer | `loadState(statePath)` → `load_checkpoint(graph_checkpoint)` ; `presentHitlChoices()` → **REMOVED** |

### 2.6 Affected INV (Invariants)

| ID | Current | Changed To |
|----|---------|-----------|
| INV-002 | "advance() 必須在 HITL ✅ 確認後才可呼叫" | **SUPERSEDED** → INV-002-v2: "advance() 必須在 auto_gate PASS 後才可呼叫" |
| INV-005 | "stepM 必須在 hitlGate 之前執行" | INV-005-v2: "stepM 必須在 auto_gate 之前執行" |
| INV-018 | "已通過的閘門不可重置，Pipeline Position 不可倒退" | Unchanged (still valid with DAG checkpoint) |

### 2.7 Affected ALG

| ID | Change |
|----|--------|
| ALG-001 | `hitl_gate()` call in loop → `auto_gate()`: if REACHED → auto PASS; if DIVERGING → log warning + auto PASS; MAX_ITER → auto PASS with warning |

### 2.8 Affected EVT

| ID | Change |
|----|--------|
| EVT-001 StageAdvanced | `hitlChoice: HitlChoice` → `gateDecision: GateDecision` |
| EVT-006 WorkflowResumed | `recoveryChoice: HitlRecoveryChoice` → `resumeSource: CheckpointSource` |

### 2.9 Affected SC (BDD Scenarios)

| ID | Change Summary |
|----|---------------|
| SC-001 | Remove "Advance requires HITL confirmation" scenario; add "Advance auto-passes after gate check" |
| SC-003 | Remove "HITL 選擇加入新需求" scenario; change REACHED/DIVERGING to auto-pass; keep NOT_REACHED loop |
| SC-010 | Rewrite entirely: "Resume from LangGraph checkpoint" instead of workflow-state.md; remove HITL choice scenarios |

### 2.10 Affected Design Docs

| Doc | Changes |
|-----|---------|
| clean-architecture.md | Remove `HITLPresenter` port; add `AutoGate` domain service; `WorkflowStateRepository` → `CheckpointRepository` |
| ooad-design.md | Update class diagram (Pipeline.advance, IterationLoop.auto_gate); update sequence diagrams (remove HITL actor); update component diagram (remove hitl/ adapter) |
| formal-verification-spec.md | Update INV-002, INV-005 contract code |
| state-machines.md | SM-001: remove "HITL ✅" guard; SM-002: replace HITL choice with auto-gate |

---

## 3. Clean Architecture Adjustments

### 3.1 Removed Components

| Layer | Component | Reason |
|-------|-----------|--------|
| Application | `ports/presenters.py` (HITLPresenter) | No HITL interaction |
| Adapters | `adapters/hitl/console_presenter.py` | No HITL interaction |

### 3.2 Modified Components

| Layer | Component | Change |
|-------|-----------|--------|
| Domain/Services | `iteration_loop.py` (CLS-003) | `hitl_gate()` → `auto_gate()` |
| Domain/Services | `workflow_resumer.py` (CLS-013) | File-based → checkpoint-based; remove `present_hitl_choices()` |
| Domain/Models | `pipeline.py` (CLS-001) | `advance(hitl)` → `advance()` |
| Application/Ports | `repositories.py` | `WorkflowStateRepository` → `CheckpointRepository` |
| Adapters | `persistence/state_repository.py` | → `persistence/checkpoint_repository.py` (LangGraph checkpoint) |

### 3.3 New Components

| Layer | Component | Purpose |
|-------|-----------|---------|
| Domain/Services | `auto_gate.py` | Autonomous gate decision logic: fixed-point → PASS, diverging → PASS+warning |
| Domain/Models | `enums.py` | `GateDecision` enum replaces `HitlChoice` for gate results |
| Adapters | `persistence/markdown_writer.py` | Write domain artifacts to `{target_repo}/docs/*.md` |
| Adapters | `persistence/markdown_reader.py` | Read existing docs from `{target_repo}/docs/*.md` |

### 3.4 Document I/O Architecture

```
┌─────────────────────────────────────────┐
│          LangGraph DAG Execution         │
│                                          │
│  ┌──────────┐    ┌───────────────────┐  │
│  │ Markdown  │───▶│  Domain Layer     │  │
│  │ Reader    │    │  (CLS, ALG, INV)  │  │
│  │ (adapter) │    └────────┬──────────┘  │
│  └──────────┘             │              │
│                           ▼              │
│                  ┌────────────────┐      │
│                  │  Markdown      │      │
│                  │  Writer        │      │
│                  │  (adapter)     │      │
│                  └───────┬────────┘      │
│                          │               │
│  State: LangGraph        │               │
│  checkpoint (internal)   │               │
└──────────────────────────┼───────────────┘
                           ▼
              {target_repo}/docs/*.md
              (same format as before)
```

**Key principle**: The LangGraph system **reads** existing `docs/*.md` at pipeline start and **writes** updated `docs/*.md` at each stage completion. The docs ARE the deliverables. Internal execution state lives in LangGraph checkpoint only.

---

## 4. Updated Algorithm: ALG-001-v2 Autonomous Convergence

```
converge(stage, dimensions[]):
  iteration = 0
  MAX_ITERATIONS = 10

  LOOP:
    findings = agent_α.critique(dimensions, current_artifacts)

    # Autonomous fixed-point detection
    IF all(f.severity == YAGNI for f in findings):
      log("Fixed point REACHED at iteration {iteration}")
      BREAK  # Auto-PASS, no HITL

    improvements = agent_β.resolve(findings)

    FOR each improvement IN improvements:
      result = micro_validate(improvement)
      IF result.FAIL AND retry_count >= 3:
        log_warning("Auto-skipping after 3 retries: {improvement}")
        CONTINUE  # No HITL escalation; log and move on

    impact = impact_analysis(improvements)
    IF impact.severity == MAJOR:
      log_warning("MAJOR impact detected: {impact}")
      # No HITL; log warning and continue

    iteration += 1
    IF iteration >= MAX_ITERATIONS:
      log_warning("MAX_ITERATIONS reached; auto-advancing")
      BREAK  # No HITL; force advance

  write_stage_artifacts_to_docs(stage)  # Document-driven output
```

**Changes from ALG-001**:
- `hitl_confirms()` → auto PASS
- `escalate_to_hitl()` → `log_warning()` + continue
- `force_hitl()` → `log_warning()` + auto BREAK
- Added `write_stage_artifacts_to_docs()` at end

---

## 5. Updated Invariants

### INV-002-v2: Auto-Gate Required for Advance

```
∀ pipeline: Pipeline
  pipeline.advance() ⟹ auto_gate.decision == GateDecision.PASS
```

**icontract**:
```python
@icontract.require(lambda self: self._last_gate_decision == GateDecision.PASS)
def advance(self) -> None: ...
```

### INV-005-v2: Step M Before Auto-Gate

```
∀ iteration: IterationLoop
  iteration.auto_gate() ⟹ iteration.step_m_completed == true
```

**icontract**:
```python
@icontract.require(lambda self: self._step_m_completed)
def auto_gate(self) -> GateDecision: ...
```

---

## 6. Updated BDD Scenarios

### SC-001-v2: Pipeline Start (Autonomous)

```gherkin
Scenario: Pipeline auto-advances through all stages
  Given the project docs directory exists
  When the pipeline executes
  Then all stages run sequentially without human intervention
  And each stage writes its artifacts to docs/
  And the pipeline completes with status COMPLETED

Scenario: Pipeline reads existing docs on resume
  Given docs/ contains requirements.md and domain-model.md
  When the pipeline starts
  Then it reads existing artifacts before processing
  And builds upon existing IDs and trace links
```

### SC-003-v2: Iteration Convergence (Autonomous)

```gherkin
Scenario: Auto-convergence at fixed point
  Given Stage N is iterating
  When all Agent alpha findings are YAGNI
  Then the stage auto-passes without human confirmation
  And stage artifacts are written to docs/

Scenario: Max iterations reached auto-advances
  Given iteration count has reached 10
  When the next iteration would begin
  Then a warning is logged
  And the stage auto-advances
  And no human intervention is requested

Scenario: MAJOR impact logged but not escalated
  Given impact analysis classifies severity as MAJOR
  When the result is processed
  Then a warning is logged with full blast radius details
  And execution continues autonomously
```

### SC-010-v2: Checkpoint Resume (No workflow-state.md)

```gherkin
Scenario: Resume from LangGraph checkpoint
  Given a previous execution was interrupted
  And a LangGraph checkpoint exists
  When the pipeline starts
  Then execution resumes from the checkpoint position
  And previously completed stages are not re-executed
  And existing docs/ artifacts are preserved

Scenario: No checkpoint starts fresh
  Given no LangGraph checkpoint exists
  And docs/ directory is empty
  When the pipeline starts
  Then execution begins from Phase 0
```

---

## 7. Updated State Machine: SM-002-v2

```
         ┌─────────┐
         │ PENDING │
         └────┬────┘
              │ previous Stage auto-PASS
              ▼
         ┌──────────┐
    ┌───▶│ITERATING │◀───┐
    │    └────┬─────┘    │
    │         │           │
    │    ┌────▼─────┐    │
    │    │ Agent α   │    │
    │    │ → Agent β │    │
    │    │ → Step M  │    │
    │    │ → AutoGate│    │
    │    └────┬─────┘    │
    │         │           │
    │    ┌────▼──────┐   │
    │    │ AutoGate  │   │
    │    └─┬─────┬───┘   │
    │  NOT │     │REACHED │
    │REACHED     ▼       │
    └──────┘ ┌──────┐   │
             │PASSED │   │
             └──────┘   │
                        │
         [INV-003] unidirectional
         [INV-004] iterationCount ≤ 10
         [INV-002-v2] auto_gate PASS required
         [INV-005-v2] stepM before auto_gate
```

---

## 8. Traceability: Change → ID Mapping

| Changed ID | Type | Old | New | Downstream Impact |
|-----------|------|-----|-----|-------------------|
| BG-003 | MODIFY | HITL gates | Autonomous execution | FEA-005 |
| FEA-005 | MODIFY | HITL 閘門 | auto-gate | FR-012,013,014 |
| FEA-010 | MODIFY | workflow-state.md | DAG checkpoint | FR-019,021 |
| FR-013 | MODIFY | HITL triggers | auto-decisions | UC-003 |
| FR-014 | SUPERSEDE | HITL convergence | FR-014-v2 auto convergence | UC-003 |
| FR-019 | SUPERSEDE | workflow-state.md | FR-019-v2 DAG checkpoint | UC-010 |
| FR-021 | SUPERSEDE | file-based recovery | FR-021-v2 checkpoint recovery | UC-010 |
| UC-003 | MODIFY | HITL in flow | auto-gate in flow | SC-003, CLS-003 |
| UC-010 | MODIFY | HITL choices | auto-resume | SC-010, CLS-013 |
| CLS-001 | MODIFY | advance(hitl) | advance() | INV-001,002 |
| CLS-003 | MODIFY | hitl_gate() | auto_gate() | INV-005, ALG-001 |
| CLS-013 | MODIFY | file load + HITL | checkpoint load | INV-018 |
| INV-002 | SUPERSEDE | HITL required | INV-002-v2 auto-gate required | SC-001 |
| INV-005 | SUPERSEDE | stepM before HITL | INV-005-v2 stepM before auto | SC-003 |
| ALG-001 | MODIFY | HITL in loop | auto-gate in loop | — |
| EVT-001 | MODIFY | hitlChoice field | gateDecision field | — |
| EVT-006 | MODIFY | recoveryChoice | resumeSource | — |
| SC-001 | MODIFY | HITL scenarios | autonomous scenarios | TC-001 |
| SC-003 | MODIFY | HITL scenarios | autonomous scenarios | TC-003 |
| SC-010 | MODIFY | workflow-state scenarios | checkpoint scenarios | TC-010 |
| SM-001 | MODIFY | HITL guard | auto guard | — |
| SM-002 | MODIFY | HITL choice | auto-gate | — |

**Total affected IDs**: 22 modified + 4 superseded = 26 changes
