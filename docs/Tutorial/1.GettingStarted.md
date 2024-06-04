# How to get started with Docs2KG?

## Installation

We have published the package to PyPi: [Docs2KG](https://pypi.org/project/Docs2KG),

You can install it via:

```bash
pip install Docs2KG
```

### Confirm the Installation

Run python in your terminal, and then import the package:

```python
import Docs2KG

print(Docs2KG.__author__)  # ai4wa

```

## Set up the OpenAI API Key

We are using the OpenAI to help us during the unified multimodal knowledge graph construction.

So we will need to set up the OpenAI API Key first.

You can get the API Key from the OpenAI website: [OpenAI](https://platform.openai.com/)

Then you can set it up via:

```bash
export OPENAI_API_KEY=sk-proj-xxx
```

And after this, you can start to use the Docs2KG.

Another way you can set this up is to create a `.env` file in the root directory of your project, and then add the
following line:

```bash
OPENAI_API_KEY=sk-proj-xxx
```

Then you can use the `python-dotenv` package to load the environment variables.

```python
from dotenv import load_dotenv

load_dotenv()
```

## Setup data directory

You need to specify the data input and output directory for your documents.

Otherwise, we will default the output into the folder under your project.

```
data/output/
```