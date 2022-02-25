"""
The color type is a color in the sRGB color space.
Colors are JSON strings in a variety of permitted formats: HTML-style hex values,
RGB, RGBA, HSL, and HSLA. Predefined HTML colors names
 like yellow and blue, are also permitted.
"""


"#ff0"
"#ffff00"
"rgb(255, 255, 0)"
"rgba(255, 255, 0, 1)"
"hsl(100, 50%, 50%)"
"hsla(100, 50%, 50%, 1)"
"yellow"


Color = str
