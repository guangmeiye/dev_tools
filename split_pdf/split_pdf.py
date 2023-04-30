#!/usr/bin/env
from __future__ import annotations
from typing import TYPE_CHECKING

import os, sys, cv2
import numpy as np
from pdf2image import convert_from_path
from cli_command_parser import Command, Option, main #noqa
from PIL import Image

if TYPE_CHECKING:
    from PIL.PpmImagePlugin import PpmImageFile

PDF_PATH = './data/PocketTarotCards2023.pdf'
OUTPUT_PATH = './data/tarot_cards/'
POPPLER_PATH = r'C:\Program Files (x86)\poppler-0.68.0\bin'

class Image_Creater(Command, description='Simple greeting example'):
    file_path = Option('-p', default=PDF_PATH, help='The pdf file we tried to split')
    output_path = Option('-o', default=OUTPUT_PATH, help='The pdf file we tried to split')
    images: list[PpmImageFile]

    def main(self):
        self.images = convert_from_path(PDF_PATH, poppler_path=POPPLER_PATH)
        for page in range(len(self.images)):
            self.save_tarot_cards(page)

    def save_tarot_cards(self, page: int):
        # Convert the image to grayscale
        image = np.array(self.images[page])
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Threshold the image to separate the black frames
        ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # Find the contours of the black frames
        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        # Loop through the contours and extract the contents of each black frame
        for i, contour in enumerate(contours):
            # Find the bounding box of the contour
            x, y, w, h = cv2.boundingRect(contour)
            # Crop the image to the bounding box
            crop = image[y:y+h, x:x+w]
            # TODO: Skip if image is pure black and white (not a tarot card, it is a charactor image)
            # Save the cropped image as a separate file
            # TODO: Name it with the real card name
            Image.fromarray(crop).save(f'{OUTPUT_PATH}page_{page}_frame_{i}.jpg')

if __name__ == '__main__':
    Image_Creater.parse_and_run()