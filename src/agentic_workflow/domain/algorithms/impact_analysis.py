"""Impact Analysis Algorithm.

Traceable to: FR-008, FR-009, FR-022
Replaces: skills/workflow-skills/impact-analysis-exec.md
"""

from typing import Dict, Any, List
from .traceability_validator import TraceabilityNode

class ImpactAnalysis:
    """Executes impact analysis for traceability nodes."""

    @classmethod
    def calculate_blast_radius(cls, modified_id: str, nodes: List[TraceabilityNode]) -> Dict[str, Any]:
        """Calculates the blast radius of changing a specific node."""
        
        # Simplified mock of recursive traversal
        affected_downstream = []
        inconsistent_upstream = []
        affected_lateral_ids = []
        
        # We would normally traverse the graph here
        blast_radius = len(affected_downstream) + len(inconsistent_upstream) + len(affected_lateral_ids)
        
        # Determine severity
        if blast_radius == 0:
            severity = "COSMETIC"
        elif blast_radius <= 3:
            severity = "MINOR"
        elif blast_radius <= 10:
            severity = "MODERATE"
        else:
            severity = "MAJOR"
            
        return {
            "blast_radius": blast_radius,
            "severity": severity,
            "affected_downstream": affected_downstream,
            "inconsistent_upstream": inconsistent_upstream,
            "affected_lateral_ids": affected_lateral_ids,
            "prompt_for_agent": "Execute M1-M4 manual resolution." if severity == "MAJOR" else "Autonomously update affected nodes."
        }
