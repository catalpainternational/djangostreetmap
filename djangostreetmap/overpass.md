# Examples of using the Overpass API

## Select the border of Timor

```
rel["ISO3166-1"="TL"];
out;
```

## Select all points tagged "healthcare" in Timor
```
area["ISO3166-1"="TL"]->.Country_area;
node[healthcare](area.Country_area);
out;
```

## Get the tags and points for hospitals in Timor
```
import xml.etree.ElementTree as ET
tree = ET.parse('country_data.xml')
root = tree.getroot()`
