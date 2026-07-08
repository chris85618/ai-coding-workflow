"""Adapters Layer — Archon workflow document mapper.

Traceable to: FR-073, FR-077, FR-078, ADR-STR-030, ADR-STR-033
Pure string logic that renders the full master pipeline topology as an
Archon nodes-DAG workflow document (the only format accepted by the
archon CLI; the deprecated steps format is rejected at load time).
Every deterministic step is a bash node invoking the single-node runner
(scripts/run_node.py), so all deterministic algorithms stay in-process
while sequencing (depends_on), loops (loop/until_bash), conditions
(when) and HITL gates (approval) are owned by Archon — the sole
orchestration engine (ADR-STR-033). No I/O and no external
dependencies, so the engine remains a replaceable detail (ADR-STR-027).
"""

from __future__ import annotations

from agentic_workflow.domain.entities.stage import MAX_ITERATIONS

_HEADER_TEMPLATE = (
    "name: agentic-workflow-{pipeline_id}\n"
    "description: >\n"
    "  Agentic master pipeline exported from the Pipeline aggregate (ADR-STR-033).\n"
    "  Every bash node executes exactly one deterministic in-process workflow node\n"
    "  through scripts/run_node.py; Archon owns all sequencing, loops and gates.\n"
    "  Runs on the live checkout: the pipeline operates on the target repository\n"
    "  itself (rollback is guarded by the read-only version-control gateway).\n"
    "interactive: true\n"
    "worktree:\n"
    "  enabled: false\n"
    "nodes:\n"
)

_RUN_TEMPLATE = ".venv/bin/python scripts/run_node.py --pipeline-id {pipeline_id} --node {node}"

_BASH_NODE_TEMPLATE = "  - id: {node_id}\n    bash: {run}\n"

_DEPENDS_TEMPLATE = "    depends_on: [{deps}]\n"

_WHEN_TEMPLATE = '    when: "{condition}"\n'

_TRIGGER_TEMPLATE = "    trigger_rule: {rule}\n"

_LOOP_NODE_TEMPLATE = (
    "  - id: {stage_id}-iterate\n"
    "    depends_on: [{stage_id}]\n"
    "    loop:\n"
    "      prompt: |\n"
    "        Execute exactly one alpha/beta convergence iteration (ALG-001) for\n"
    "        {stage_id} by running these deterministic commands in order,\n"
    "        reporting each command's output:\n"
    "{iteration_commands}"
    "        Then run `{check_run}`; when it prints exit_loop or rollback,\n"
    "        output <promise>CONVERGED</promise>.\n"
    "      until: CONVERGED\n"
    "      max_iterations: {max_iterations}\n"
    "      fresh_context: true\n"
    "      until_bash: |\n"
    '        test "$({check_run})" != "beta"\n'
)

_LOOP_COMMAND_TEMPLATE = "        {run}\n"

_APPROVAL_NODE_TEMPLATE = '  - id: {node_id}\n    approval:\n      message: "{message}"\n    depends_on: [{deps}]\n'

_HITL_GATE_MESSAGE = (
    "HITL gate for {stage_id} (ADR-GOV-021): review the stage artifacts; approve to advance the pipeline."
)

_QUALITY_GATE_TEMPLATE = (
    "  - id: quality-gate\n"
    "    bash: |\n"
    "      .venv/bin/python -m pytest -q && .venv/bin/python -m ruff check src tests scripts\n"
    "      .venv/bin/python -m mypy src tests scripts\n"
    "    timeout: 600000\n"
    "    depends_on: [{deps}]\n"
)

_PHASE_NODES = {"phase0": "phase_0", "phase1": "phase_1", "phase2": "phase_2"}

_STAGE_PLANNING_NODES = {
    "stage3": "stage_3_planning",
    "stage4": "stage_4_algorithm",
    "stage5": "stage_5_ooad",
    "stage6": "stage_6_formal",
    "stage7": "stage_7_bdd",
    "stage8": "stage_8_tdd",
}

_ITERATION_NODES = [
    "alpha",
    "beta",
    "iterate",
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
    "rca",
]

_CONTINUOUS_TRIGGER = "none_failed_min_one_success"


class ArchonWorkflowMapper:
    """Maps a pipeline and its canonical position order to an Archon nodes-DAG workflow."""

    def workflow_name(self, workflow_doc: str) -> str:
        """Extract the workflow name from the document's first line."""
        first_line = workflow_doc.split("\n", 1)[0]
        return first_line.removeprefix("name:").strip()

    def _run(self, pipeline_id: str, node: str) -> str:
        """Render the single-node runner command for node."""
        run_template = _RUN_TEMPLATE
        return run_template.format(pipeline_id=pipeline_id, node=node)

    def _bash_node(
        self,
        pipeline_id: str,
        node_id: str,
        node: str,
        deps: list[str],
        when: str | None = None,
        trigger: str | None = None,
    ) -> str:
        """Render one bash node running exactly one in-process workflow node."""
        bash_template = _BASH_NODE_TEMPLATE
        depends_template = _DEPENDS_TEMPLATE
        when_template = _WHEN_TEMPLATE
        trigger_template = _TRIGGER_TEMPLATE
        parts = [bash_template.format(node_id=node_id, run=self._run(pipeline_id, node))]
        if deps:
            parts.append(depends_template.format(deps=", ".join(deps)))
        if when is not None:
            parts.append(when_template.format(condition=when))
        if trigger is not None:
            parts.append(trigger_template.format(rule=trigger))
        return "".join(parts)

    def _iteration_loop(self, pipeline_id: str, stage_id: str) -> str:
        """Render the α/β iteration loop node for one stage (ALG-001).

        The Archon loop construct owns the iteration; convergence is decided
        deterministically by until_bash running the in-process fixed-point
        router (check_fixed_point), never by the AI output alone.
        """
        loop_template = _LOOP_NODE_TEMPLATE
        command_template = _LOOP_COMMAND_TEMPLATE
        iteration_nodes = _ITERATION_NODES
        max_iterations = MAX_ITERATIONS
        commands = "".join(command_template.format(run=self._run(pipeline_id, node)) for node in iteration_nodes)
        return loop_template.format(
            stage_id=stage_id,
            iteration_commands=commands,
            check_run=self._run(pipeline_id, "check_fixed_point"),
            max_iterations=max_iterations,
        )

    def _stage_block(self, pipeline_id: str, stage_id: str, prev: str) -> tuple[str, str]:
        """Render planning node + iteration loop + route + rollback/align + HITL gate."""
        planning_nodes = _STAGE_PLANNING_NODES
        approval_template = _APPROVAL_NODE_TEMPLATE
        gate_message = _HITL_GATE_MESSAGE
        route_id = f"{stage_id}-route"
        parts = [self._bash_node(pipeline_id, stage_id, planning_nodes[stage_id], [prev])]
        parts.append(self._iteration_loop(pipeline_id, stage_id))
        parts.append(self._bash_node(pipeline_id, route_id, "check_fixed_point", [f"{stage_id}-iterate"]))
        parts.append(
            self._bash_node(
                pipeline_id,
                f"{stage_id}-rollback",
                "rollback",
                [route_id],
                when=f"${route_id}.output == 'rollback'",
            )
        )
        parts.append(
            self._bash_node(
                pipeline_id,
                f"{stage_id}-align",
                "align",
                [route_id],
                when=f"${route_id}.output != 'rollback'",
            )
        )
        parts.append(
            approval_template.format(
                node_id=f"{stage_id}-gate",
                message=gate_message.format(stage_id=stage_id),
                deps=f"{stage_id}-align",
            )
        )
        return "".join(parts), f"{stage_id}-gate"

    def _gated_debt_pair(
        self,
        pipeline_id: str,
        prefix: str,
        gate_node: str,
        deps: list[str],
        trigger: str | None = None,
    ) -> tuple[str, str, str]:
        """Render gate + debt routing pair; FAIL gates flow into debt absorption (ADR-STR-029)."""
        gate_id = f"{prefix}-gate"
        route_id = f"{prefix}-route"
        debt_id = f"{prefix}-debt"
        parts = [self._bash_node(pipeline_id, gate_id, gate_node, deps, trigger=trigger)]
        parts.append(self._bash_node(pipeline_id, route_id, "route_debt", [gate_id]))
        parts.append(
            self._bash_node(
                pipeline_id,
                debt_id,
                f"{prefix}_debt",
                [route_id],
                when=f"${route_id}.output == 'debt'",
            )
        )
        return "".join(parts), route_id, debt_id

    def _phase_9_block(self, pipeline_id: str, prev: str) -> tuple[str, str]:
        """Render sonar gate, security audit, conditional debt absorption and shipping."""
        continuous_trigger = _CONTINUOUS_TRIGGER
        sonar_doc, sonar_route, sonar_debt = self._gated_debt_pair(pipeline_id, "sonar", "sonar_gate", [prev])
        security_doc, security_route, security_debt = self._gated_debt_pair(
            pipeline_id, "security", "security_audit", [sonar_route, sonar_debt], trigger=continuous_trigger
        )
        parts = [sonar_doc, security_doc]
        parts.append(
            self._bash_node(
                pipeline_id,
                "phase9",
                "phase_9",
                [security_route, security_debt],
                trigger=continuous_trigger,
            )
        )
        return "".join(parts), "phase9"

    def _phase_10_block(self, pipeline_id: str, prev: str) -> tuple[str, str]:
        """Render retrospective plus the Ouroboros constraint closure."""
        parts = [self._bash_node(pipeline_id, "phase10", "phase_10", [prev])]
        parts.append(self._bash_node(pipeline_id, "update-constraints", "update_constraints", ["phase10"]))
        return "".join(parts), "update-constraints"

    def _position_block(self, pipeline_id: str, position: str, prev: str) -> tuple[str, str]:
        """Render the node block for one canonical pipeline position."""
        planning_nodes = _STAGE_PLANNING_NODES
        phase_nodes = _PHASE_NODES
        if position in planning_nodes:
            return self._stage_block(pipeline_id, position, prev)
        if position == "phase9":
            return self._phase_9_block(pipeline_id, prev)
        if position == "phase10":
            return self._phase_10_block(pipeline_id, prev)
        node = phase_nodes.get(position, position)
        return self._bash_node(pipeline_id, position, node, [prev]), position

    def to_workflow_yaml(self, pipeline_id: str, stages: list[str]) -> str:
        """Render the Archon workflow document for pipeline_id over positions."""
        header_template = _HEADER_TEMPLATE
        gate_template = _QUALITY_GATE_TEMPLATE
        parts = [header_template.format(pipeline_id=pipeline_id)]
        parts.append(self._bash_node(pipeline_id, "inject", "inject", []))
        parts.append(self._bash_node(pipeline_id, "start", "start", ["inject"]))
        prev = "start"
        for position in stages:
            block, prev = self._position_block(pipeline_id, position, prev)
            parts.append(block)
        parts.append(self._bash_node(pipeline_id, "complete", "complete", [prev]))
        parts.append(gate_template.format(deps="complete"))
        return "".join(parts)
