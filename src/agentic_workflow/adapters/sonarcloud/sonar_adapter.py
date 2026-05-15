"""SonarCloud API Adapter.

Traceable to: FEA-015, FR-015
"""

import requests
from typing import Any
from agentic_workflow.frameworks.config import SonarCloudConfig

class SonarCloudAdapter:
    """Adapter for interacting with SonarCloud Web API."""

    BASE_URL = "https://sonarcloud.io/api"

    def __init__(self, config: SonarCloudConfig):
        self.config = config
        self.auth = (config.token, "")

    def get_metrics(self) -> dict[str, dict[str, Any]]:
        """Fetch measures for the project.
        
        Ref: https://sonarcloud.io/api/measures/component
        """
        metric_keys = [
            "coverage",
            "duplicated_lines_density",
            "complexity",
            "cognitive_complexity",
            "vulnerabilities",
            "bugs",
            "code_smells",
            "sqale_debt_ratio",
            "reliability_rating"
        ]
        
        params = {
            "component": self.config.project_key,
            "metricKeys": ",".join(metric_keys)
        }
        
        response = requests.get(
            f"{self.BASE_URL}/measures/component",
            params=params,
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"SonarCloud API error: {response.status_code} - {response.text}")
            
        data = response.json()
        component = data.get("component", {})
        measures = component.get("measures", [])
        
        # Transform into Domain format
        result = {}
        for m in measures:
            metric = m["metric"]
            # Map API keys to our Domain internal keys if necessary
            key_map = {
                "complexity": "cyclomatic_complexity",
                "duplicated_lines_density": "duplication",
                "vulnerabilities": "security_vulnerabilities",
                "sqale_debt_ratio": "tech_debt_ratio",
                "bugs": "blocker_critical_smells", # Simplified mapping
                "code_smells": "major_smells"
            }
            target_key = key_map.get(metric, metric)
            
            val = m.get("value")
            # Try to convert to float if it looks like a number
            try:
                val = float(val) if val is not None else 0.0
            except ValueError:
                pass
                
            result[target_key] = {"global": val}
            
        return result

    def get_issues(self) -> list[dict[str, Any]]:
        """Fetch open issues for the project.
        
        Ref: https://sonarcloud.io/api/issues/search
        """
        params = {
            "componentKeys": self.config.project_key,
            "resolved": "false",
            "ps": 50 # Page size
        }
        
        response = requests.get(
            f"{self.BASE_URL}/issues/search",
            params=params,
            auth=self.auth
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"SonarCloud API error: {response.status_code}")
            
        return response.json().get("issues", [])
