from pydantic import BaseModel

"""
A transition property controls timing for the interpolation between a
transitionable style property's previous value and new value.
A style's root transition property provides global
transition defaults for that style.
"""


class Transition(BaseModel):
    duration: int = 300
    delay: int = 0
