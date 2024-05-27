from pathlib import Path


class Image2Description:
    def __init__(self, image_path: Path):
        """
        Extract Semantic Description from Image
        """
        self.image_path = image_path

    def get_image_description(self):
        """
        Get the description of the image

        Read the image, and then pass to the OpenAI API to get the description
        """
        pass
