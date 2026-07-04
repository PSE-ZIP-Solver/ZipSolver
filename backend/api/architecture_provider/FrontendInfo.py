from pydantic import BaseModel, ConfigDict, Field


class FrontendInfo(BaseModel):
    """Frontend toolchain summary — framework, build tool, styling (§5.5.6)."""

    model_config = ConfigDict(populate_by_name=True)

    framework: str
    build_tool: str = Field(..., alias="buildTool")
    styling: str
