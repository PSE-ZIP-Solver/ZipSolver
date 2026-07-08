from pydantic import BaseModel, ConfigDict, Field


class ModelInfo(BaseModel):
    """Trained-artifact metadata nested inside RLStackInfo (§5.5.6).

    Populated by the RL layer at startup; `loaded=False` when no artifact is present.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    supported_board_sizes: list[int] = Field(..., alias="supportedBoardSizes")
    loaded: bool