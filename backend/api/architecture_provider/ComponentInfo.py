from pydantic import BaseModel, ConfigDict


class ComponentInfo(BaseModel):
    """One registered backend module: its name and its role at the boundary (§5.5.6)."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    role: str
