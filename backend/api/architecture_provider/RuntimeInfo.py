from pydantic import BaseModel, ConfigDict, Field


class RuntimeInfo(BaseModel):
    """Language + ASGI framework + server, each with its resolved version (§5.5.6)."""

    model_config = ConfigDict(populate_by_name=True)

    language: str
    language_version: str = Field(..., alias="languageVersion")
    asgi_framework: str = Field(..., alias="asgiFramework")
    framework_version: str = Field(..., alias="frameworkVersion")
    server: str
    server_version: str = Field(..., alias="serverVersion")
