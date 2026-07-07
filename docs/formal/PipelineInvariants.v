(***************************************************************************)
(* Coq proofs of the Unified Agentic Workflow pipeline arithmetic          *)
(* invariants (kanban: 形式化驗證加入 Coq).                                 *)
(*                                                                         *)
(* Complements the TLA+ state-machine spec (PipelineStateMachine.tla) and  *)
(* the Z3 proofs (tests/formal/test_z3_invariants.py) with foundational,   *)
(* machine-checked theorems over unbounded integers.                       *)
(*                                                                         *)
(* Traceable to: INV-001, INV-026, FR-071, ADR-STR-029,                    *)
(*               docs/formal-verification-spec.md                          *)
(*                                                                         *)
(* Check with: coqc PipelineInvariants.v (graceful degradation: the pytest *)
(* gate only validates proof structure when coqc is absent, ADR-GOV-017)   *)
(***************************************************************************)

Require Import ZArith.
Require Import Lia.

Open Scope Z_scope.

(* 11 canonical positions: phase0 .. phase10 *)
Definition stage_count : Z := 11.

(* kappa scaled by 2 to stay integral:                                      *)
(* 2 * kappa = 2 * iterations * ITERATION_WEIGHT(1.0) + debts * 2 * 0.5    *)
Definition kappa2 (iterations debts : Z) : Z := 2 * iterations + debts.

(* INV-001: advancing never moves the position backwards. *)
Theorem advance_strictly_monotonic :
  forall idx : Z, 0 <= idx < stage_count - 1 -> idx < idx + 1.
Proof. intros. lia. Qed.

(* INV-001: advancing from any in-range position stays in range. *)
Theorem advance_stays_in_range :
  forall idx : Z, 0 <= idx < stage_count - 1 -> 0 <= idx + 1 < stage_count.
Proof. intros. unfold stage_count in *. lia. Qed.

(* FR-071: governance cost kappa is non-negative for all valid inputs. *)
Theorem kappa_non_negative :
  forall iterations debts : Z,
    0 <= iterations -> 0 <= debts -> 0 <= kappa2 iterations debts.
Proof. intros. unfold kappa2. lia. Qed.

(* FR-071: absorbing more debt can never lower the HITL trigger. *)
Theorem kappa_monotonic_in_debt :
  forall iterations debts : Z,
    0 <= iterations -> 0 <= debts ->
    kappa2 iterations debts <= kappa2 iterations (debts + 1).
Proof. intros. unfold kappa2. lia. Qed.

(* INV-026: 1-based sequential debt numbering never collides. *)
Theorem debt_numbering_collision_free :
  forall start offset_a offset_b : Z,
    offset_a <> offset_b -> start + offset_a <> start + offset_b.
Proof. intros. lia. Qed.
