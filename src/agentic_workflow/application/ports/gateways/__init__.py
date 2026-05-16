"""Port Interfaces — Gateway Contracts.

Traceable to: FR-015, FR-016, FR-026, FR-027, FR-028, ADR-STR-001
Clean Architecture: domain/application depend only on these abstractions.
Adapters in adapters/llm/, adapters/mcp/ implement these interfaces.
"""

from agentic_workflow.application.ports.gateways.llm_gateway import LLMGateway
from agentic_workflow.application.ports.gateways.mcp_gateway import MCPGateway
from agentic_workflow.application.ports.gateways.quality_gateway import QualityGateway
from agentic_workflow.application.ports.gateways.security_gateway import SecurityGateway

__all__ = ["LLMGateway", "MCPGateway", "SecurityGateway", "QualityGateway"]
