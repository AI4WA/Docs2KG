# Open Source Framework: Docs2KG

**Unified Knowledge Graph Construction from Heterogeneous Documents Assisted by Large
Language Models**

![PyPI](https://img.shields.io/pypi/v/Docs2KG)
[![Demo](https://img.shields.io/badge/Demo-Available-blue)](https://docs2kg.ai4wa.com/Video/)
![Lint](https://github.com/AI4WA/Docs2KG/actions/workflows/lint.yml/badge.svg)
![Documentation](https://github.com/AI4WA/Docs2KG/actions/workflows/docs.yml/badge.svg)
![Status](https://img.shields.io/badge/Status-Work%20in%20Progress-yellow)

## Installation

We have published the package to PyPi, you can install it via:

```bash
pip install Docs2KG
```

---

## Motivation

Three pillars of the LLM applications in our opinion:

- Data
- RAG
- LLM

Most of the tools in the market nowadays are focusing on the **Retrieval Augmented Generation (RAG) pipelines** or
How to get Large Language Models (LLMs) to run locally.

Typical tools include: Ollama, LangChain, LLamaIndex, etc.

However, to make sure the wider community can benefit from the latest research, we need to first solve the data problem.

The Wider community includes personal users, small business, and even large enterprises.
Some of them might have developed databases, while most of them do have a lot of data, but they are all in unstructured
form, and distributed in different places.

So the first challenges will be:

- **How can we easily process the unstructured data into a centralized place?**
- **What is the best way to organize the data within the centralized place?**

## Proposed Solution

This package is a proposed solution to the above challenges.

- We developed the tool for the wider community to easily process the unstructured data into a centralized place.
- We proposed a way to organize the data within the centralized place, via a Unified Multimodal Knowledge Graph
  altogether with semi-structured data.

### Overall Architecture

The overall workflow will be:

![img.png](docs/images/Docs2KG.jpg)

### Implemented System Architecture

![img.png](docs/images/Modules.jpg)

### Unified Multimodal Knowledge Graph

How we construct this unified multimodal knowledge graph step by step:

![img.png](docs/images/KGConstruction.jpg)

---

## Setup and Development

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements.dev.txt

pip install -e .
```
