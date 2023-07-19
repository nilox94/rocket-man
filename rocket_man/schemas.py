from typing import Self

from pydantic import BaseModel, TypeAdapter


class BaseSchema(BaseModel):
    """Base schema class."""

    @classmethod
    def validate_json(cls, json_data: str | bytes | bytearray) -> Self:
        """Validate the given JSON data against the Pydantic model.

        Args:
            json_data: The JSON data to validate.

        Returns:
            The validated model instance.
        """
        return cls.model_validate_json(json_data)

    @classmethod
    def validate_json_list(cls, json_list_data: str | bytes | bytearray) -> list[Self]:
        """Validate the given JSON list data against the Pydantic model.

        Args:
            json_list_data: The JSON list data to validate.

        Returns:
            The list of validated model instances.
        """
        return TypeAdapter(list[cls]).validate_json(json_list_data)  # type: ignore[valid-type]


class Video(BaseSchema):
    """FrameX Video schema."""

    name: str
    width: int
    height: int
    frames: int
    frame_rate: tuple[int, int]
    url: str
    first_frame: str
    last_frame: str
