import cv2
import numpy as np
import pandas as pd
import itertools
import pytesseract
from PIL import Image
from typing import List, Tuple
from image_processing import load_image, load_template, convert_to_grayscale

def kks_recognition_mceo(df: pd.DataFrame, image_path: str) -> List[str]:  
    img = cv2.imread(image_path)
    text_list = []
    for i in range(len(df)):
        x1, y1, x2, y2 = list(itertools.chain(*list(map(list, df[i]))))
        x1_text, y1_text , x2_text, y2_text = (x1, y2, x2, round(y2 + 4*6.17))
        extracted_rect = img[y1_text:y2_text, x1_text:x2_text]
        text = pytesseract.image_to_string(extracted_rect, lang='eng')
        
        text = text.strip().replace(' ', '')
        if text[0] != '1': 
            text = text.replace(text[0], '1')
        if text[1] != '0': 
            text = text.replace(text[1], '0')
        text = text.strip().replace('\n', '')
        text_list.append(text)
    return text_list # .strip() - для удаления пробелов


def add_border_to_image(image, border_width = 50):
    '''Потребуется передача в функцию "изображения", в данном случае вырезка
KKS из элемента, тип - numpy.ndarray 
def add_border_to_image(kks_image: numpy.ndarray, border_width) ->  numpy.ndarray'''
    # Загрузка изображения
    # image = cv2.imread(image_path)

    # Получаем размеры изображения
    height, width = image.shape[:2]

    # Вычисляем новые размеры с учетом границ
    new_height = height + 2 * border_width
    new_width = width + 2 * border_width

    # Создаем новое изображение с белыми границами
    new_image = np.zeros((new_height, new_width, 3), dtype=np.uint8)
    new_image.fill(255)  # Заполняем белым цветом

    # Вычисляем координаты для размещения ROI
    x_offset = border_width
    y_offset = border_width

    # Копируем ROI на новое изображение
    new_image[y_offset:y_offset+height, x_offset:x_offset+width] = image

    # img2 = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
    # text = pytesseract.image_to_string(img2, lang='rus')
    return new_image

def kks_recognition_armatura(df: pd.DataFrame, image_path: str, save_added_text = False) -> List[str]:  
    img = cv2.imread(image_path)
    text_list = []
    for i in range(len(df)):
        x1, y1, x2, y2 = list(itertools.chain(*list(map(list, df[i]))))
        x1_text, y1_text , x2_text, y2_text = (x1, y2+20, x2+40, y2 + 90) # 4*2.76*3
        
        extracted_rect = img[y1_text:y2_text, x1_text:x2_text]
        extracted_rect = add_border_to_image(extracted_rect)
        if save_added_text == True: 
            cv2.imwrite(f"added_text_{i}.png", extracted_rect) #сохранение обведенных серийников по номеру итерации
        text = pytesseract.image_to_string(extracted_rect, lang='eng')
        
        table = str.maketrans('', '', "!@#$%^&*()_+-=[]{}|;:,.<>?/~`")
        text.translate(table)
        text_list.append(text)#(text[:12])#.strip().replace(' ', ''))
        
    return text_list # .strip() - для удаления пробелов

def kks_recognition_indicator(df: pd.DataFrame, image_path: str, save_added_text = False) -> List[str]:  
    img = cv2.imread(image_path)
    text_list = []
        
    delta_y1_text = 2 #пикселя
    delta_y2_text = 38 #пикселя
    
    delta_x1_text = 20 #пикселя
    delta_x2_text = 60 #пикселя

    for i in range(len(df)):
        
        x1, y1, x2, y2 = list(itertools.chain(*list(map(list, df[i]))))
        x1_text, y1_text , x2_text, y2_text = (x1+delta_x1_text, y2 + delta_y1_text, x2 + delta_x2_text, y2 + delta_y2_text) # 4*2.76*3
        
        extracted_rect = img[y1_text:y2_text, x1_text:x2_text]
        extracted_rect = add_border_to_image(extracted_rect)
        
        if save_added_text == True: 
            cv2.imwrite(f"added_text_{i}.png", extracted_rect) #сохранение обведенных серийников по номеру итерации
            
        text = pytesseract.image_to_string(extracted_rect, lang='eng')
        
        table = str.maketrans('', '', "!@#$%^&*()_+-=[]{}|;:,.<>?/~`")
        text.translate(table)
        text_list.append(text[:12])#.strip().replace(' ', ''))
        
    return text_list # .strip() - для удаления пробелов

def unit_recognition(df: pd.DataFrame, image_path: str, save_added_text = False) -> List[str]:  
    img = cv2.imread(image_path)
    text_list_rus = [] 

    delta_y1_text = -100 #пикселя
    delta_y2_text = 0 #пикселя
    
    delta_x1_text = 2 #пикселя
    delta_x2_text = 130 #пикселя

    for i in range(len(df)):
        
        x1, y1, x2, y2 = list(itertools.chain(*list(map(list, df[i]))))
        x1_text, y1_text , x2_text, y2_text = (x2+delta_x1_text, y2 + delta_y1_text, x2 + delta_x2_text, y2 + delta_y2_text) # 4*2.76*3
        
        extracted_rect = img[y1_text:y2_text, x1_text:x2_text]
        extracted_rect = add_border_to_image(extracted_rect)
        
        if save_added_text == True: 
            cv2.imwrite(f"added_text_{i}.png", extracted_rect) #сохранение обведенных серийников по номеру итерации
            
        unit_text_rus = pytesseract.image_to_string(extracted_rect, lang='rus')
        if unit_text_rus == '':
            unit_text_rus = pytesseract.image_to_string(extracted_rect, config='--psm 10', lang='rus')
        table = str.maketrans('', '', "!@#$%^&*()_+-=[]{}|;:,.<>?/~`")
        
        unit_text_rus.translate(table)
        
        text_list_rus.append(unit_text_rus.replace('\n', ''))#[:12])#.strip().replace(' ', ''))
        
    return text_list_rus # заменили пустые значения на символ "А", потому что НЕЙРОНКА БЛЯТЬ НЕ МОЖЕТ БУКВУ А ПРОЧИТАТЬ


def kks_norm(data: List[str]):
    kks_norm_data = []
    for i in range(len(data)):
        text = data[i]
        # print(f'{i} text orig: ',text)
        if len(text) > 2:
            if text[1] != '0': 
                text = text.replace(text[1], '0')
            if text[0] != '1': 
                text = text.replace(text[0], '1')
            if text[2] == '0': 
                text = text.replace(text[2], 'O')
            if text[-3] == 'O': 
                text = text.replace(text[-3], '0')
            if text[5] == 'S': 
                text = text.replace(text[5], '5')
            if text[6] == 'O':
                text = text.replace(text[6], '0')
            kks_norm_data.append(text)
        else: kks_norm_data.append(text)
        # print(f'{i} text norm: ',text)
    return kks_norm_data