"""
Based on whether the documentation is natively in digital form or not
It will go through different process.

However, the output will be general:

- markdown for text
- json for structured data
- image json and image files for images


The current SOTA of the image process is going to be improved by time, so we make this module extendable.

For image based on, we will use image path, for native digital one, we will use native path

And each method will have a name, which will be used to call it.
"""
