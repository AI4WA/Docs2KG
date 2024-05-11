# Docs2KG 
**An Open Source Framework for Transforming Unstructured Data into Unified Knowledge Graph**

The generative AI attracts a lot of attention, one of the goals is using it with our own data.
Our data mainly in two forms:

- Unstructured data: text, image
- Structured data: database, csv, etc.

To handle the unstructured data, one of the common approaches we do is to get the chunk of text into embeddings,
and then do vector search.
This is the first and naive generation of RAG (Retrieval Augmented Generation).

However, we do want to be able to do the information retrieval under the global context (which includes the structured
data and unstructured data).

So, find a way to unify the structured data and unstructured data, and then does the information retrieval across the
whole data context be an ultimate goal.

So the end of goal of this project is to build a unified framework to allow you to talk with your databases and
documents in a unified way.

## Unstructured Data Processing

The Main data under this category is PDF.

So we need to be able to extract the text and images from the PDF.

The overall workflow will be:

![img.png](docs/images/pdf_process.jpg)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.dev.txt

pip install -e .
```
