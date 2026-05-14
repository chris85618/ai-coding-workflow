"""Application Layer — Use Case Interactors + Port Interfaces.

Orchestrates domain objects. Depends on Domain layer only via ports.
Each use case is a single class with one public execute() method.

UC-001..011 mapped to individual use case files.
Ports define abstract interfaces for repositories, gateways, doc I/O, event bus.
"""
