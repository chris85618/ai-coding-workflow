"""LangGraph DAG Builder.

Parses config.yaml to construct the LangGraph StateGraph, binding the Python node functions
to establish the complete edge flow.
"""

import yaml
from pathlib import Path
from langgraph.graph import StateGraph, START, END
from agentic_workflow.adapters.langgraph.state_mapper import WorkflowState
import agentic_workflow.adapters.langgraph.nodes as nodes_module

def build_graph_from_config(config_path: str = "config.yaml") -> StateGraph:
    """Builds the LangGraph DAG dynamically from config.yaml."""
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    workflow_config = config.get("workflow_graph", {})
    if not workflow_config:
        raise ValueError("workflow_graph configuration missing in config.yaml")
        
    # 1. Initialize StateGraph
    builder = StateGraph(WorkflowState)
    
    # 2. Add Nodes
    for node_name in workflow_config.get("nodes", []):
        func_name = f"node_{node_name}"
        node_func = getattr(nodes_module, func_name)
        builder.add_node(node_name, node_func)
        
    # 3. Add Edges
    for edge in workflow_config.get("edges", []):
        source = START if edge["source"] == "__start__" else edge["source"]
        target = END if edge["target"] == "__end__" else edge["target"]
        builder.add_edge(source, target)
        
    # 4. Add Conditional Edges
    for c_edge in workflow_config.get("conditional_edges", []):
        source = c_edge["source"]
        condition_func_name = c_edge["condition_func"]
        mapping = c_edge["mapping"]
        
        condition_func = getattr(nodes_module, condition_func_name)
        builder.add_conditional_edges(source, condition_func, mapping)
        
    return builder.compile()

if __name__ == "__main__":  # pragma: no cover
    # Test compilation
    graph = build_graph_from_config()
    print("LangGraph successfully compiled from YAML configuration.")

