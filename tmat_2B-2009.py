# Конфигурационные параметры
# IMAGE_PATH = "C://Users//user//Desktop//template_programm_divided//comp_1.png"
# TEMPLATE_PATH = "C://Users//user//Desktop//template_programm_divided//templates//comp_svg_pd_armatura.png"
# OUTPUT_FILE = 'C://Users//user//Desktop//template_programm_divided//templates//tmat_armatura_small_output.csv'
panel_name = '11'
flags_armatura = ['switch', 'armatura']
flag = flags_armatura[1]
flag = '2B-2009'

IMAGE_PATH = f"C://Users//user//Desktop//template_programm_divided//{panel_name}.png"
TEMPLATE_PATH = f"C://Users//user//Desktop//template_programm_divided//templates//{flag}.png"
OUTPUT_FILE = f'{flag}_output_{panel_name}.xlsx'

OUTPUT_FOLDER = 'C://Users//user//Desktop//template_programm_divided'

#импорт библиотек
import pandas as pd
import numpy as np
import cv2

#импорт модулей пользователя
import object_detection
import text_recognition
import data_preprocessing
import utils

# Переходим в директорию
import os
os.chdir(r'C:\Users\user\Desktop\template_programm_divided')
print('хорош')

# # получаем серые изображения оригинала и шаблона, а также цветные изображения и шаблон
gray_image, gray_template, image, template = object_detection.\
                                                 preprocess_images(IMAGE_PATH, TEMPLATE_PATH)
                                                 
# cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
# width, height = 800, 1200
# cv2.imshow("Detected Objects", gray_image)
# cv2.resizeWindow("Detected Objects", width, height)
# cv2.waitKey(0)
# cv2.destroyAllWindows()

locations_of_all_objects = object_detection.\
                            detect_objects(gray_image, gray_template, threshold=0.8)
# print(locations_of_all_objects)        
            
df_of_all_objects = object_detection.\
                            filter_unique_objects(locations_of_all_objects)
# print('df_of_all_objects:', df_of_all_objects)                      
df_of_target_objects = object_detection.\
                            remove_overlapping_objects(df_of_all_objects)
                            
# print(len(df_of_target_objects))

list_two_coord_of_object = object_detection.\
                                 visualize_results_2B_2009(panel_name, image, template, df_of_target_objects, flag, visual_show = False, visual_save = True)
# print(len(list_two_coord_of_object))
                          

kks_text = text_recognition.\
                    kks_recognition_armatura(list_two_coord_of_object, IMAGE_PATH, save_added_text = False)
kks_text_formatted = text_recognition.kks_norm(kks_text)

print(*kks_text_formatted)
preprocessed_data= data_preprocessing.\
                                    preprocess_data_2B_2009(list_two_coord_of_object)

# print(preprocessed_data)

utils.save_data_2B_2009(preprocessed_data, OUTPUT_FILE, OUTPUT_FOLDER)

