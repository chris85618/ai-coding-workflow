from typing import Any

class SonarCloudClient:
    measures: Any
    issues: Any
    metrics: Any
    def __init__(self, sonarqube_url: str, token: str | None = ...) -> None: ...
