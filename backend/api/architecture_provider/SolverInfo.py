from pydantic import BaseModel, ConfigDict


class SolverInfo(BaseModel):
    """One registered solver: its name, kind, and whether it's the default (§5.5.6)."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    kind: str            # "reinforcement-learning" | "DFS"
    default: bool = False
