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

import pandas as pd
# TODO(developer): Set key_path to the path to the service account key
#                  file.
key_path = r"C:\Users\kaust\Desktop\workspaces\Emorhis\emorhis-49e39873b6f0.json"

credentials = service_account.Credentials.from_service_account_file(
    key_path,
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)

# Instantiates a client
#client = vision.ImageAnnotatorClient(credentials=credentials)




class FeatureType(Enum):
    PAGE = 1
    BLOCK = 2
    PARA = 3
    WORD = 4
    SYMBOL = 5


def draw_boxes(image, bounds, color):
    """Draw a border around the image using the hints in the vector list."""
    draw = ImageDraw.Draw(image)

    for bound in bounds:
        draw.polygon([
            bound.vertices[0].x, bound.vertices[0].y,
            bound.vertices[1].x, bound.vertices[1].y,
            bound.vertices[2].x, bound.vertices[2].y,
            bound.vertices[3].x, bound.vertices[3].y], None, color)
    return image

def CreateWord(word):
    ret_word = ""
    for symbol in word.symbols:
        ret_word = ret_word + symbol.text
    return ret_word 

def Word2DataFrame(word):
    se_word = pd.Series()
    se_word['x1'] = word[0].bounding_box.vertices[0].x
    se_word['x2'] = word[0].bounding_box.vertices[1].x
    se_word['x3'] = word[0].bounding_box.vertices[2].x
    se_word['x4'] = word[0].bounding_box.vertices[3].x
    se_word['y1'] = word[0].bounding_box.vertices[0].y
    se_word['y2'] = word[0].bounding_box.vertices[1].y
    se_word['y3'] = word[0].bounding_box.vertices[2].y
    se_word['y4'] = word[0].bounding_box.vertices[3].y
    se_word['X']  = round((se_word['x1']+se_word['x2']+se_word['x3']+se_word['x4'])/4)
    se_word['Y']  = round((se_word['y1']+se_word['y2']+se_word['y3']+se_word['y4'])/4)
    se_word['slope'] = (se_word['y2'] - se_word['y1'])/(se_word['x2'] - se_word['x1'])
    se_word['text'] = CreateWord(word[0])
    se_word['Para_Id'] = word[1]
    return se_word

def GetStruturedWords(words):
    global df_StructWords 
    df_StructWords = pd.DataFrame()
    for word in words:
        df_StructWords = df_StructWords.append(Word2DataFrame(word),ignore_index = True)
        df_StructWords = df_StructWords.sort_values(['Y','X'],ascending=[True,True],ignore_index=True)
        df_StructWords['dX'] = df_StructWords['X'].diff()
        AverageSlope = df_StructWords['slope'].mean()
    return df_StructWords

def GetCSV_2(df_StructWords):
    line = ''
    f = open(r"test.csv",'w')
    for index, row in df_StructWords.iterrows():
        if(row.dX < 0 or pd.isnull(row['dX'])):
            line = line + ' ' + row.text + '\n'
            f.write(line)
            print(line)
            line = ''
        else:
            line = line + ' ' + row.text 
    f.close()
    Data_df = pd.read_csv(r"test.csv",names = [1,2,3,4,5,6,7,8,9,10])
    return Data_df

def GetCSV(df_StructWords):
    df_StructWords = df_StructWords.iloc[::-1]
    line = ''
    last_para_id = 0
    f = open(r"test.csv",'w')
    for index, row in df_StructWords.iterrows():
        if(row.dX < 0 or pd.isnull(row['dX'])):
            line = line + ' ' + row.text + '\n'
            f.write(line)
            print(line)
            line = ''
        else:
            if(last_para_id != 0 and last_para_id != row['Para_Id'] and line != ''):
                line = line + ';' + row.text 
            else:
                line = line + ' ' + row.text 
        last_para_id = row['Para_Id']
    f.close()
    Data_df = pd.read_csv(r"test.csv",names = [1,2,3,4,5,6,7,8,9,10], delimiter= ";")
    return Data_df

def get_document_bounds(image_file_path, feature):
    """Returns document bounds given an image."""
    client = vision.ImageAnnotatorClient(credentials=credentials)

    bounds = []
    Features = []
    with io.open(image_file_path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation

    # Collect specified feature bounds by enumerating all document features
    para_id = 0
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                para_id = para_id + 1
                for word in paragraph.words:
                    for symbol in word.symbols:
                        if (feature == FeatureType.SYMBOL):
                            bounds.append(symbol.bounding_box)
                            Features.append(symbol)
                    if (feature == FeatureType.WORD):
                        bounds.append(word.bounding_box)
                        Features.append((word,para_id))
                        print(para_id)
                if (feature == FeatureType.PARA):
                    bounds.append(paragraph.bounding_box)
                    Features.append(paragraph)

            if (feature == FeatureType.BLOCK):
                bounds.append(block.bounding_box)
                Features.append(block)
    # The list `bounds` contains the coordinates of the bounding boxes.
    return bounds, Features

def Cleanup(Data_df):
    # check which column is having costs and remove other rows
    DF_cl1 = Data_df[1].replace(",",".")
    SE_cl1 = DF_cl1.str.findall("\d+\.\d+")

    # clean costs column  rows to keep just cost values


def render_doc_text(filein, fileout):
    image = Image.open(filein)
    bounds,Features = get_document_bounds(filein, FeatureType.BLOCK)
    draw_boxes(image, bounds, 'blue')
    bounds,Features = get_document_bounds(filein, FeatureType.PARA)
    draw_boxes(image, bounds, 'red')
    bounds,Features = get_document_bounds(filein, FeatureType.WORD)
    draw_boxes(image, bounds, 'yellow')
    df_StructWords = GetStruturedWords(Features)
    global Data_df
    Data_df = GetCSV_2(df_StructWords)

    if fileout != 0:
        image.save(fileout)
    else:
        image.show()


if __name__ == '__main__':
    #parser = argparse.ArgumentParser()
    #parser.add_argument('detect_file', help='The image for text detection.')
    #parser.add_argument('-out_file', help='Optional output file', default=0)
    #args = parser.parse_args()

    render_doc_text("frame150.jpg", "out150.jpg")