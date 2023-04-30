import os
import time

import pyautogui
from PIL import ImageGrab
import cv2
import numpy as np

RESSOURCES = ["tin", "iron", "kobalt", "bronze"]

def non_max_suppression(boxes_and_scores, overlap_threshold):
    if len(boxes_and_scores) == 0:
        return []

    boxes = np.array([box for box, _ in boxes_and_scores])
    scores = np.array([score for _, score in boxes_and_scores])

    x1 = boxes[:, 0, 0]
    y1 = boxes[:, 0, 1]
    x2 = boxes[:, 1, 0]
    y2 = boxes[:, 1, 1]

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(scores)

    pick = []
    while len(idxs) > 0:
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)

        overlap = (w * h) / (areas[i] + areas[idxs[:last]] - w * h)
        idxs = np.delete(idxs, np.concatenate(([last], np.where(overlap > overlap_threshold)[0])))

    return [boxes_and_scores[i] for i in pick]


def match_image(template_path, screenshot_path, method=cv2.TM_CCOEFF_NORMED, threshold=0.8, overlap_threshold=0.5):
    # Load the template image and screenshot as grayscale images
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    screenshot = cv2.imread(screenshot_path, cv2.IMREAD_GRAYSCALE)

    # Perform template matching
    result = cv2.matchTemplate(screenshot, template, method)

    # Get the locations of matches above the threshold
    locations = np.where(result >= threshold)

    # Calculate the bounding boxes and confidence scores for each match
    width, height = template.shape[::-1]
    boxes_and_scores = []
    for pt in zip(*locations[::-1]):
        top_left = pt
        bottom_right = (pt[0] + width, pt[1] + height)
        confidence = result[pt[1], pt[0]]
        boxes_and_scores.append(((top_left, bottom_right), confidence))

    # Apply non-maximum suppression to remove overlapping boxes
    boxes_and_scores = non_max_suppression(boxes_and_scores, overlap_threshold)

    # Return the list of bounding boxes and confidence scores
    return boxes_and_scores

def find_in_screen(template_path, output_path, delete_screenshot=True):
    # Capture the screenshot
    screenshot = ImageGrab.grab()

    # Save the screenshot to a file
    screenshot.save(output_path)

    # Process the screenshot using the match_image function
    boxes = match_image(template_path, output_path, overlap_threshold=0.5, threshold=0.97)
    for box in boxes:
        bounding_box, confidence = box

    # Delete the screenshot file if delete_screenshot is set to True
    if delete_screenshot:
        os.remove(output_path)
    return boxes