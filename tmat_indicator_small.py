# Конфигурационные параметры
panel_name = '10CWA62GA201'
element_name = 'indicator'
flags_indicator = ['big', 'small']
flag = flags_indicator[1]

IMAGE_PATH = f"C://Users//user//Desktop//template_programm_divided//{panel_name}.png"
TEMPLATE_PATH = f"C://Users//user//Desktop//template_programm_divided//templates//{element_name}_{flag}.png"
OUTPUT_FILE = f'{element_name}_output_{panel_name}.xlsx'

OUTPUT_FOLDER = 'C://Users//user//Desktop//template_programm_divided'

# Импорт библиотек
import pandas as pd
import numpy as np
import cv2
from tqdm import tqdm  # Импортируем tqdm

# Импорт модулей пользователя
import object_detection
import text_recognition
import data_preprocessing
import utils

# Переходим в директорию
import os
os.chdir(r'C:\Users\user\Desktop\template_programm_divided')
print('Ща поедем')

# Получаем серые изображения оригинала и шаблона, а также цветные изображения и шаблон
gray_image, gray_template, image, template = object_detection.preprocess_images(IMAGE_PATH, TEMPLATE_PATH)

# Этап 1: Обнаружение объектов
with tqdm(total=1, desc="Обнаружение объектов", ncols=75) as pbar:  # Ограничение длины шкалы
    locations_of_all_objects = object_detection.detect_objects(gray_image, gray_template, threshold=0.8)
    pbar.update(1)

# Этап 2: Фильтрация уникальных объектов
with tqdm(total=1, desc="Фильтрация уникальных объектов", ncols=75) as pbar:
    df_of_all_objects = object_detection.filter_unique_objects(locations_of_all_objects)
    pbar.update(1)

# Этап 3: Удаление перекрывающихся объектов
with tqdm(total=1, desc="Удаление перекрывающихся объектов", ncols=75) as pbar:
    df_of_target_objects = object_detection.remove_overlapping_objects(df_of_all_objects)
    pbar.update(1)

# Этап 4: Визуализация результатов
with tqdm(total=1, desc="Визуализация результатов", ncols=75) as pbar:
    list_two_coord_of_object = object_detection.visualize_results_indicator(panel_name, image, template, df_of_target_objects, flag, visual_show=False, visual_save = True)
    pbar.update(1)

# Этап 5: Распознавание текста KKS
with tqdm(total=1, desc="Распознавание текста KKS", ncols=75) as pbar:
    kks_text = text_recognition.kks_recognition_indicator(list_two_coord_of_object, IMAGE_PATH, save_added_text=False)
    pbar.update(1)

# Этап 6: Распознавание единиц измерения
with tqdm(total=1, desc="Распознавание единиц измерения", ncols=75) as pbar:
    units_list_rus = text_recognition.unit_recognition(list_two_coord_of_object, IMAGE_PATH, save_added_text=False)
    pbar.update(1)

# Этап 7: Форматирование текста KKS
with tqdm(total=1, desc="Форматирование текста KKS", ncols=75) as pbar:
    kks_text_formatted = text_recognition.kks_norm(kks_text)
    pbar.update(1)

# Этап 8: Предобработка данных
with tqdm(total=1, desc="Предобработка данных", ncols=75) as pbar:
    preprocessed_data= data_preprocessing.preprocess_data_indicator(list_two_coord_of_object, kks_text_formatted, units_list_rus)
    pbar.update(1)

# print(preprocessed_data)

# Этап 9: Сохранение данных
with tqdm(total=1, desc="Сохранение данных", ncols=75) as pbar:
    utils.save_data_indicator(preprocessed_data, OUTPUT_FILE, OUTPUT_FOLDER)
    pbar.update(1)

print("Обработка завершена!")