"""
Shared telemetry type aliases.
"""

from typing import NewType

RequestId = NewType("RequestId", str)
WorkflowId = NewType("WorkflowId", str)
UserId = NewType("UserId", str)