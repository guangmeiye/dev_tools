#!/usr/bin/env
from __future__ import annotations
from typing import TYPE_CHECKING

import os, sys, cv2
import numpy as np
from cli_command_parser import Command, Option, main #noqa
from itertools import chain
from functools import cached_property
from pdf2image import convert_from_path
from PIL import Image

if TYPE_CHECKING:
    from PIL.PpmImagePlugin import PpmImageFile

PDF_PATH = './data/PocketTarotCards2023.pdf'
OUTPUT_PATH = './data/tarot_cards'
TAROT_CARDS_NAME_PATH = './data/tarot_cards_name.txt'
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
        # for (i, contour) in zip(reversed(range(len(contours))) ,contours):
        for i, contour in enumerate(reversed(contours)):
            # Find the bounding box of the contour
            x, y, w, h = cv2.boundingRect(contour)
            # Crop the image to the bounding box
            crop = image[y:y+h, x:x+w]

            # Hardcode to remove none tarot card image
            if page==2 and i in chain(range(3, 12), range(15, 22)):
                continue

            # Save the cropped image as a separate file
            Image.fromarray(crop).save(f'{OUTPUT_PATH}/{self.tarot_card_names.pop(0)}.jpg')

    @cached_property
    def tarot_card_names(self):
        with open(TAROT_CARDS_NAME_PATH, 'r') as f:
            return [name.strip() for name in f if name.strip()]


if __name__ == '__main__':
    Image_Creater.parse_and_run()