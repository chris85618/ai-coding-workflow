---------------------------- MODULE PipelineStateMachine ----------------------------
(***************************************************************************)
(* TLA+ specification of the Unified Agentic Workflow pipeline aggregate.  *)
(*                                                                         *)
(* Traceable to: INV-001, INV-002-v2, INV-016, FR-001, FR-068, FR-069,     *)
(*               ADR-STR-029, docs/formal-verification-spec.md             *)
(*                                                                         *)
(* Model-check with TLC:                                                   *)
(*   tlc PipelineStateMachine.tla  (graceful degradation: the pytest gate  *)
(*   only validates spec structure when TLC is not installed, ADR-GOV-017) *)
(***************************************************************************)

EXTENDS Naturals, Sequences

CONSTANTS StageCount          \* 11 canonical positions (phase0 .. phase10)

ASSUME StageCount \in Nat /\ StageCount > 1

VARIABLES position,           \* current stage index, 0-based
          status,             \* pipeline lifecycle status
          gate,               \* last auto-gate decision
          debts,              \* absorbed dynamic-debt count (FR-068)
          hitlRequired        \* delayed-HITL flag (FR-071)

vars == <<position, status, gate, debts, hitlRequired>>

Statuses  == {"not_started", "running", "completed", "failed"}
Gates     == {"none", "pass", "pass_with_warnings", "fail"}

TypeInvariant ==
    /\ position \in 0..(StageCount - 1)
    /\ status \in Statuses
    /\ gate \in Gates
    /\ debts \in Nat
    /\ hitlRequired \in BOOLEAN

Init ==
    /\ position = 0
    /\ status = "not_started"
    /\ gate = "none"
    /\ debts = 0
    /\ hitlRequired = FALSE

Start ==
    /\ status = "not_started"
    /\ status' = "running"
    /\ UNCHANGED <<position, gate, debts, hitlRequired>>

RecordGate(decision) ==
    /\ status = "running"
    /\ decision \in Gates \ {"none"}
    /\ gate' = decision
    /\ UNCHANGED <<position, status, debts, hitlRequired>>

\* INV-002-v2: advancement demands a passing gate; INV-001: strictly +1.
Advance ==
    /\ status = "running"
    /\ gate \in {"pass", "pass_with_warnings"}
    /\ position < StageCount - 1
    /\ position' = position + 1
    /\ UNCHANGED <<status, gate, debts, hitlRequired>>

\* FR-068: a failing gate is absorbed as debt and downgraded, never a hard stop.
AbsorbDebt ==
    /\ status = "running"
    /\ gate = "fail"
    /\ debts' = debts + 1
    /\ gate' = "pass_with_warnings"
    /\ UNCHANGED <<position, status, hitlRequired>>

\* FR-069: divergence rolls the position back to the universal base (index 0)
\* and raises the delayed-HITL flag (FR-071).
RollbackToUniversalBase ==
    /\ status = "running"
    /\ position' = 0
    /\ hitlRequired' = TRUE
    /\ UNCHANGED <<status, gate, debts>>

Complete ==
    /\ status = "running"
    /\ position = StageCount - 1
    /\ status' = "completed"
    /\ UNCHANGED <<position, gate, debts, hitlRequired>>

Next ==
    \/ Start
    \/ \E d \in Gates \ {"none"} : RecordGate(d)
    \/ Advance
    \/ AbsorbDebt
    \/ RollbackToUniversalBase
    \/ Complete

Spec == Init /\ [][Next]_vars

\* INV-001 (weakened for rollback): outside the degradation path the position
\* only moves forward; a backward move always raises hitlRequired.
MonotonicOrRollback ==
    [][ (position' < position) => hitlRequired' ]_vars

\* FR-068 safety: absorbing debt never leaves the gate hard-failed.
DebtNeverHardStops ==
    [][ (debts' > debts) => (gate' # "fail") ]_vars

\* Completion only happens from the final position.
CompletionSafety ==
    [][ (status' = "completed") => (position = StageCount - 1) ]_vars

THEOREM Spec => []TypeInvariant

=======================================================================================
