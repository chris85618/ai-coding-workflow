"""Adapters Layer — Archon workflow document mapper.

Traceable to: FR-073, FR-077, FR-078, ADR-STR-030, ADR-STR-033
Pure string logic that renders the full master pipeline topology as an
Archon YAML workflow document. Every step invokes the single-node runner
(scripts/run_node.py), so all deterministic algorithms stay in-process
while sequencing, loops, conditions and gates are owned by Archon —
the sole orchestration engine (ADR-STR-033). No I/O and no external
dependencies, so the engine remains a replaceable detail (ADR-STR-027).
"""

from __future__ import annotations

from agentic_workflow.domain.entities.stage import MAX_ITERATIONS

_HEADER_TEMPLATE = "name: agentic-workflow-{pipeline_id}\nisolation: worktree\nsteps:\n"

_RUN_TEMPLATE = "python scripts/run_node.py --pipeline-id {pipeline_id} --node {node}"

_SIMPLE_STEP_TEMPLATE = "  - id: {step_id}\n    run: {run}\n"

_INIT_NODES = [("inject", "inject"), ("start", "start")]

_PHASE_NODES = {"phase0": "phase_0", "phase1": "phase_1", "phase2": "phase_2"}

_STAGE_PLANNING_NODES = {
    "stage3": "stage_3_planning",
    "stage4": "stage_4_algorithm",
    "stage5": "stage_5_ooad",
    "stage6": "stage_6_formal",
    "stage7": "stage_7_bdd",
    "stage8": "stage_8_tdd",
}

_MICRO_VAL_NODES = [
    "micro_val_step_0_format",
    "micro_val_step_1_id_structure",
    "micro_val_step_2_forward_trace",
    "micro_val_step_3_backward_trace",
    "micro_val_step_4_semantic",
    "micro_val_step_5_orphan",
    "micro_val_step_5_5_lateral_trace",
    "micro_val_step_5_7_lesson_reuse",
    "micro_val_step_6_trigger_impact",
    "micro_val_step_7_record_change",
]

_LOOP_HEADER_TEMPLATE = "  - id: {stage_id}\n    loop:\n      max_iterations: {max_iterations}\n      steps:\n"

_LOOP_STEP_TEMPLATE = "        - id: {step_id}\n          run: {run}\n"

_FIXED_POINT_TEMPLATE = (
    "        - id: {stage_id}-fixed-point\n"
    "          route: {run}\n"
    "          routes:\n"
    "            beta: continue\n"
    "            exit_loop: break\n"
    "            rollback: {stage_id}-rollback\n"
)

_HITL_LOOP_TEMPLATE = (
    "        - id: {stage_id}-hitl\n"
    "          route: {run}\n"
    "          routes:\n"
    "            alpha: repeat\n"
    "            pass: break\n"
)

_ALIGN_TEMPLATE = (
    "  - id: {stage_id}-align\n"
    "    run: {align_run}\n"
    "  - id: {stage_id}-align-gate\n"
    "    route: {gate_run}\n"
    "    routes:\n"
    "      alpha: {stage_id}\n"
    "      pass: continue\n"
)

_ROLLBACK_TEMPLATE = "  - id: {stage_id}-rollback\n    when: {stage_id}-fixed-point == rollback\n    run: {run}\n"

_DEBT_TEMPLATE = "  - id: {step_id}\n    when:\n      route: {route_run}\n      equals: debt\n    run: {run}\n"

_QUALITY_GATE_STEP = (
    "  - id: quality-gate\n"
    "    agent: coding-agent\n"
    "    prompt: Run ruff check, mypy and pytest; require 100 percent statement and branch coverage.\n"
)


class ArchonWorkflowMapper:
    """Maps a pipeline and its canonical position order to an Archon YAML workflow."""

    def _run(self, pipeline_id: str, node: str) -> str:
        """Render the single-node runner command for node."""
        run_template = _RUN_TEMPLATE
        return run_template.format(pipeline_id=pipeline_id, node=node)

    def _simple_step(self, pipeline_id: str, step_id: str, node: str) -> str:
        """Render one plain command step."""
        step_template = _SIMPLE_STEP_TEMPLATE
        return step_template.format(step_id=step_id, run=self._run(pipeline_id, node))

    def _iteration_loop(self, pipeline_id: str, stage_id: str) -> str:
        """Render the α/β iteration loop body for one stage (ALG-001)."""
        header_template = _LOOP_HEADER_TEMPLATE
        step_template = _LOOP_STEP_TEMPLATE
        fixed_point_template = _FIXED_POINT_TEMPLATE
        hitl_template = _HITL_LOOP_TEMPLATE
        micro_val_nodes = _MICRO_VAL_NODES
        max_iterations = MAX_ITERATIONS
        parts = [header_template.format(stage_id=stage_id, max_iterations=max_iterations)]
        parts.append(step_template.format(step_id=f"{stage_id}-alpha", run=self._run(pipeline_id, "alpha")))
        parts.append(fixed_point_template.format(stage_id=stage_id, run=self._run(pipeline_id, "check_fixed_point")))
        for node in ["beta", "iterate", *micro_val_nodes]:
            parts.append(step_template.format(step_id=f"{stage_id}-{node}", run=self._run(pipeline_id, node)))
        parts.append(step_template.format(step_id=f"{stage_id}-rca", run=self._run(pipeline_id, "rca")))
        parts.append(hitl_template.format(stage_id=stage_id, run=self._run(pipeline_id, "hitl_gate_choice")))
        return "".join(parts)

    def _stage_block(self, pipeline_id: str, stage_id: str) -> str:
        """Render planning step + iteration loop + align closure + rollback path."""
        planning_nodes = _STAGE_PLANNING_NODES
        align_template = _ALIGN_TEMPLATE
        rollback_template = _ROLLBACK_TEMPLATE
        planning_node = planning_nodes[stage_id]
        parts = [self._simple_step(pipeline_id, planning_node, planning_node)]
        parts.append(self._iteration_loop(pipeline_id, stage_id))
        parts.append(
            align_template.format(
                stage_id=stage_id,
                align_run=self._run(pipeline_id, "align"),
                gate_run=self._run(pipeline_id, "hitl_gate_choice"),
            )
        )
        parts.append(rollback_template.format(stage_id=stage_id, run=self._run(pipeline_id, "rollback")))
        return "".join(parts)

    def _debt_step(self, pipeline_id: str, step_id: str) -> str:
        """Render one conditional debt-absorption step (ADR-STR-029 routing)."""
        debt_template = _DEBT_TEMPLATE
        return debt_template.format(
            step_id=step_id, route_run=self._run(pipeline_id, "route_debt"), run=self._run(pipeline_id, step_id)
        )

    def _phase_9_block(self, pipeline_id: str) -> str:
        """Render sonar gate, security audit, debt absorption and shipping."""
        parts = [self._simple_step(pipeline_id, "sonar_gate", "sonar_gate")]
        parts.append(self._debt_step(pipeline_id, "sonar_debt"))
        parts.append(self._simple_step(pipeline_id, "security_audit", "security_audit"))
        parts.append(self._debt_step(pipeline_id, "security_debt"))
        parts.append(self._simple_step(pipeline_id, "phase9", "phase_9"))
        return "".join(parts)

    def _phase_10_block(self, pipeline_id: str) -> str:
        """Render retrospective plus the Ouroboros constraint closure."""
        parts = [self._simple_step(pipeline_id, "phase10", "phase_10")]
        parts.append(self._simple_step(pipeline_id, "update_constraints", "update_constraints"))
        return "".join(parts)

    def _position_block(self, pipeline_id: str, position: str) -> str:
        """Render the step block for one canonical pipeline position."""
        planning_nodes = _STAGE_PLANNING_NODES
        phase_nodes = _PHASE_NODES
        if position in planning_nodes:
            return self._stage_block(pipeline_id, position)
        if position == "phase9":
            return self._phase_9_block(pipeline_id)
        if position == "phase10":
            return self._phase_10_block(pipeline_id)
        node = phase_nodes.get(position, position)
        return self._simple_step(pipeline_id, position, node)

    def to_workflow_yaml(self, pipeline_id: str, stages: list[str]) -> str:
        """Render the Archon workflow document for pipeline_id over positions."""
        header_template = _HEADER_TEMPLATE
        init_nodes = _INIT_NODES
        gate_step = _QUALITY_GATE_STEP
        header = header_template.format(pipeline_id=pipeline_id)
        init = [self._simple_step(pipeline_id, step_id, node) for step_id, node in init_nodes]
        blocks = [self._position_block(pipeline_id, position) for position in stages]
        tail = self._simple_step(pipeline_id, "complete", "complete")
        return header + "".join(init) + "".join(blocks) + tail + gate_step
