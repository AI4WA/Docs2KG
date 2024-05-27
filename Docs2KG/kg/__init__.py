"""

## Design
We will follow the steps here to create the KG:

- Layout Structure KG
    - Document -> Page -> h1, h2, h3, h4, h5, h6, p, li
    - Link Image to the Page
    - Link Table to the Page
    - Link image to content in the Page (will be hard)
    - Link Table to content in the Page (will be hard)

Input will be an output folder of the parser
Output will be the KG, in the format of JSON, which can allow you to easily import into a graph database


- Layout Structure KG Schema
    - Document
    - Page
    - h1
    - h2
    - h3
    - h4
    - h5
    ...

## Output Schema

pandas.DataFrame with the following columns:
- source_node_type
- source_node_uuid
- source_node_properties (json)
- edge_type
- edge_uuid (optional, do we need this?)
- edge_properties (json)
- destination_node_type
- destination_node_uuid
- destination_node_properties (json)

"""
