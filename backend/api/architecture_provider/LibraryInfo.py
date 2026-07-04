from pydantic import BaseModel, ConfigDict


class LibraryInfo(BaseModel):
    """A single dependency reported as name + resolved version (§5.5.6).

    Reused for validation (Pydantic), numerical (NumPy), and every RL-stack library.
    """

    model_config = ConfigDict(populate_by_name=True)

    name: str
    version: str
