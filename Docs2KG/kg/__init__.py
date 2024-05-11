"""
We will follow the steps here to create the KG:

- Create the Skeleton of the KG via the Markdown
- Then do the supplementary entity link via the **entity_linker** module, driven by *text kg* module
- Next we will do is to link the tables and images to the KG
    - this will be via with an entity linking and spatial context link

Input will be an output folder of the parser
Output will be the KG, in the format of a txt or csv file, which can allow you to easily import into a graph database

"""
