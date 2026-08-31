from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class ContainerPortMapping(BaseModel):
    container_port: int
    host_port: int
    protocol: str = "tcp"

class DesiredState(BaseModel):
    """Declarative specification defined in Git manifests."""
    app_name: str
    image: str
    tag: str
    ports: List[ContainerPortMapping] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    healthcheck_path: Optional[str] = "/healthz"
    healthcheck_port: Optional[int] = None

class ActualState(BaseModel):
    """Runtime state inspected directly from Docker engine."""
    container_id: Optional[str] = None
    app_name: str
    image: str
    tag: str
    ports: List[ContainerPortMapping] = Field(default_factory=list)
    env: Dict[str, str] = Field(default_factory=dict)
    status: str = "stopped"

class StateDiff(BaseModel):
    """Calculated difference between desired and actual state."""
    has_drift: bool
    reasons: List[str] = Field(default_factory=list)