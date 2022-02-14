from importlib import resources
import json
from maplibre.basemodel import Root

if __name__ == "__main__":

    style_text = resources.read_text("maplibre", "style.json")
    style = json.loads(style_text)

    root_two = Root.parse_obj(style)
    print(root_two)
    with resources.path("maplibre", "style_out.json") as p:
        with open(p, "w") as f:
            f.write(root_two.json(indent=4, exclude_unset=True))
