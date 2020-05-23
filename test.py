from google.cloud import bigquery
from google.oauth2 import service_account
import io
import os
# Imports the Google Cloud client library
import argparse
from enum import Enum
import io
from google.cloud import vision
from google.cloud.vision import types
from PIL import Image, ImageDraw

key_path = r"C:\Users\kaust\Desktop\workspaces\Emorhis\emorhis-49e39873b6f0.json"
credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

image_file = "frame312.jpg"

with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

client = vision.ImageAnnotatorClient(credentials=credentials)
image = types.Image(content=content)
response = client.document_text_detection(image=image)
document = response.full_text_annotation