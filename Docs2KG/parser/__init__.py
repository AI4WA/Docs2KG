"""
The input can be

- PDF
    - Scanned PDF
    - Exported PDF
- CSV
- Email
- Excel
- Web

The output we generate need to consider two types of metadata:

- Layout metadata
- Semantic metadata

So from design perspective, let's use PDF as an example:

Columns:
    - File Name
    - File Path
    - File Type
    - Page Index
    - Content Type: Text, Figures, Table
    - Layout Level: h1, h2, h3, h4, h5, h6, p, figcaption, table, td, th
    - Content: The actual content. (For figures, it can be the image path)
"""
