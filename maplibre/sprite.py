from pydantic import BaseModel, Field

"""
A style's sprite property supplies a URL template for loading small
images to use in rendering background-pattern,
fill-pattern, line-pattern,fill-extrusion-pattern
and icon-image style properties.
"""


class Sprite(BaseModel):
    width: int = 32
    height: int = 32
    x: int = 0
    y: int = 0
    pixelRatio: int = 1
    content: tuple[float, float, float, float] | None = Field(
        None,
        description="An array of four numbers, with the first two specifying the left, top corner, and the last two specifying the right, bottom corner. If present, and if the icon uses icon-text-fit, the symbol's text will be fit inside the content box.",
    )
    stretchX: tuple[float, float] | None = Field(
        None,
        description="An array of two-element arrays, consisting of two numbers that represent the from position and the to position of areas that can be stretched.",
    )
    stretchY: tuple[float, float] | None = None
