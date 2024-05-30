import ast
from typing import List

import pandas as pd


class BlockFinder:
    @classmethod
    def find_closest_blocks(
        cls,
        block_rect: str,
        text_blocks: List[str],
    ) -> dict:
        """
        Find the closest text block to the image block

        TODO:
        - Based on how large it close to the margin, we can decide whether it is a important image or not
        - Based on the size of the image, we can determine whether we need the left, right information

        Args:
            block_rect (str): The bounding box of the image block as a string
            text_blocks (List[str]): The bounding boxes of the text blocks as strings

        Returns:
            dict: The index of the closest text block to the image block in each direction
        """
        left_index = None
        right_index = None
        above_index = None
        below_index = None
        distances = []
        for i, text_block in enumerate(text_blocks):
            distance = cls.bbox_distance(block_rect, text_block)
            distance["index"] = i
            distance["bbox"] = text_block
            distances.append(distance)

        df = pd.DataFrame(distances)

        # for all the text blocks on top, get the closest one
        # get above one and also the abs(min_vertical_distance) is > 1
        above_blocks = df[df["position_vertical"] == "above"].copy(deep=True)
        # get is all value to be abs
        above_blocks["min_vertical_distance"] = above_blocks[
            "min_vertical_distance"
        ].apply(abs)
        above_blocks = above_blocks[abs(above_blocks["min_vertical_distance"]) > 1]

        if not above_blocks.empty:
            # if it is above it, then the closest one is the one with the highest vertical distance as the value is <0
            closest_above_block = above_blocks[
                above_blocks["min_vertical_distance"]
                == above_blocks["min_vertical_distance"].min()
            ]
            above_index = closest_above_block["index"].values[0]

        # for all the text blocks on bottom, get the closest one
        below_blocks = df[df["position_vertical"] == "below"].copy(deep=True)
        # get is all value to be abs
        below_blocks["min_vertical_distance"] = below_blocks[
            "min_vertical_distance"
        ].apply(abs)
        below_blocks = below_blocks[abs(below_blocks["min_vertical_distance"]) > 1]
        if not below_blocks.empty:
            # if it is below it, then the closest one is the one with the lowest vertical distance as the value is >0
            closest_below_block = below_blocks[
                below_blocks["min_vertical_distance"]
                == below_blocks["min_vertical_distance"].min()
            ]
            below_index = closest_below_block["index"].values[0]

        # for all the text blocks on left, get the closest one
        left_blocks = df[df["position_horizontal"] == "left"].copy(deep=True)
        # get is all value to be abs
        left_blocks["min_horizontal_distance"] = left_blocks[
            "min_horizontal_distance"
        ].apply(abs)
        left_blocks = left_blocks[abs(left_blocks["min_horizontal_distance"]) > 1]
        if not left_blocks.empty:
            closest_left_block = left_blocks[
                left_blocks["min_horizontal_distance"]
                == left_blocks["min_horizontal_distance"].min()
            ]
            left_index = closest_left_block["index"].values[0]

        # for all the text blocks on right, get the closest one
        right_blocks = df[df["position_horizontal"] == "right"].copy(deep=True)
        # get is all value to be abs
        right_blocks["min_horizontal_distance"] = right_blocks[
            "min_horizontal_distance"
        ].apply(abs)
        right_blocks = right_blocks[abs(right_blocks["min_horizontal_distance"]) > 1]
        if not right_blocks.empty:
            closest_right_block = right_blocks[
                right_blocks["min_horizontal_distance"]
                == right_blocks["min_horizontal_distance"].min()
            ]
            right_index = closest_right_block["index"].values[0]

        return {
            "left": left_index,
            "right": right_index,
            "above": above_index,
            "below": below_index,
        }

    @classmethod
    def parse_bbox(cls, s):
        """Parse a bounding box string into a tuple of floats."""
        return tuple(map(float, ast.literal_eval(s)))

    @classmethod
    def bbox_distance(cls, bbox_a, bbox_b) -> dict:
        """
        Calculate the minimum distance between two bounding boxes.
        The (0,0) point is the top-left corner of the image.

        So within the bbox

        x0, y0 = top-left corner
        x1, y1 = bottom-right corner
        x0 <= x1
        y0 <= y1

        Args:
            bbox_a:
            bbox_b:

        Returns:

        """
        bbox_a = cls.parse_bbox(bbox_a)
        bbox_b = cls.parse_bbox(bbox_b)

        x0_a, y0_a, x1_a, y1_a = bbox_a
        x0_b, y0_b, x1_b, y1_b = bbox_b

        # if both x0_a and x1_a are less than x0_b or x1_b
        # this means that bbox_a is to the left of bbox_b
        # if both y0_a and y1_a are less than y0_b or y1_b
        # this means that bbox_a is above bbox_b
        horizontal_distance = [x0_a - x0_b, x1_a - x0_b, x0_a - x1_b, x1_a - x1_b]
        vertical_distance = [y0_a - y1_b, y1_a - y0_b, y0_a - y0_b, y1_a - y1_b]
        abs_horizontal_distance = [abs(item) for item in horizontal_distance]
        abs_vertical_distance = [abs(item) for item in vertical_distance]

        # get the mini distance and then find their real value, keep the sign
        min_horizontal_distance = min(abs_horizontal_distance)
        min_vertical_distance = min(abs_vertical_distance)

        # get the index
        min_horizontal_distance_index = abs_horizontal_distance.index(
            min_horizontal_distance
        )
        min_vertical_distance_index = abs_vertical_distance.index(min_vertical_distance)

        # get the real value
        min_horizontal_distance_value = horizontal_distance[
            min_horizontal_distance_index
        ]
        min_vertical_distance_value = vertical_distance[min_vertical_distance_index]

        # whether it is left or right, above or below will be control by the
        # angle of the center of the two bounding boxes
        center_a = ((x0_a + x1_a) / 2, (y0_a + y1_a) / 2)
        center_b = ((x0_b + x1_b) / 2, (y0_b + y1_b) / 2)

        # use bbox_a as the reference point
        center_x_diff = center_a[0] - center_b[0]
        center_y_diff = center_a[1] - center_b[1]

        # if center_x_diff > 0, then mean bbox_a is to the right of bbox_b, so bbox_b is on the left
        position_horizontal = "left" if center_x_diff > 0 else "right"
        # if center_y_diff > 0, then mean bbox_a is below bbox_b, so bbox_b is above
        position_vertical = "above" if center_y_diff > 0 else "below"
        return {
            "min_horizontal_distance": min_horizontal_distance_value,
            "min_vertical_distance": min_vertical_distance_value,
            "min_distance": min(min_horizontal_distance, min_vertical_distance),
            "position_horizontal": position_horizontal,
            "position_vertical": position_vertical,
        }
