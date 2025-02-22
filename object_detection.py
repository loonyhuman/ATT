import cv2
import numpy as np
import pandas as pd
import itertools
import pytesseract
from PIL import Image
from typing import List, Tuple
from image_processing import load_image, load_template, convert_to_grayscale


def preprocess_images(image_path: str, template_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """Загружает изображения и преобразует их в оттенки серого."""
    image = load_image(image_path)
    template = load_template(template_path)
    return convert_to_grayscale(image), convert_to_grayscale(template), image, template

def detect_objects(gray_image: np.ndarray, gray_template: np.ndarray, threshold: float) -> Tuple[List[Tuple[int, int]], List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
    """Находит шаблоны в изображении."""
    result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= threshold)
    return locations

def filter_unique_objects(locations: Tuple[List[int], List[int]]) -> pd.DataFrame:
    """Фильтрует уникальные объекты и сортирует их по координатам."""
    location_dict = {}
    for i, (x, y) in enumerate(zip(locations[0], locations[1])):
        location_dict[f'object_{i}'] = {'x': x, 'y': y}
    
    df = pd.DataFrame(location_dict)
    unique_data = df.transpose().copy()
   # unique_data = unique_data.sort_values(['x', 'y']).reset_index(drop=True)
    return unique_data

def remove_overlapping_objects(df: pd.DataFrame, min_distance: int = 20) -> pd.DataFrame:
    # 
    # min_distance = 20 - при разрешении 12699х23811, 336х336 пкс/дюйм, размер 96х180
    # 
    """Удаляет объекты, слишком близко расположенные друг к другу."""
    # Сортируем DataFrame по координатам x и y
    df = df.sort_values(by=['x', 'y']).reset_index(drop=True)
    
    # Список для хранения индексов строк, которые нужно удалить
    objects_to_remove = []
    
    # Проходим по всем строкам и сравниваем их со всеми предыдущими
    for i in range(len(df)):
        if i in objects_to_remove:
            continue  # Пропускаем уже отмеченные для удаления строки
        
        current_row = df.iloc[i]
        
        for j in range(i + 1, len(df)):
            if j in objects_to_remove:
                continue  # Пропускаем уже отмеченные для удаления строки
            
            other_row = df.iloc[j]
            
            # Проверяем расстояние по x и y
            x_diff = abs(current_row['x'] - other_row['x'])
            y_diff = abs(current_row['y'] - other_row['y'])
            
            # Если расстояние меньше min_distance, добавляем индекс в список на удаление
            if x_diff < min_distance and y_diff < min_distance:
                objects_to_remove.append(j)
    
    # Удаляем строки с индексами из списка objects_to_remove
    df = df.drop(index=objects_to_remove)
    
    return df.reset_index(drop=True)

def calculating_quadrant_number(coor: tuple):
    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    sq_side = 317.475 # <- деление нового изображения на старое
    column_num = round(coor[1]/sq_side)
    row_num = round(coor[0]/sq_side)

    return str(alphabet[column_num// len(alphabet)] + alphabet[column_num % len(alphabet)]) +  '-' + str(int(1+ row_num % sq_side))


def visualize_results_2B_2009(panel_name, image: np.ndarray, template: np.ndarray, unique_data: pd.DataFrame, visual_show = False, visual_save = False):
    """Визуализирует результаты обнаружения объектов и создает кортежи двух координат."""
    locations = (np.array(unique_data['x']), np.array(unique_data['y']))
    
    list_presence_of_circle = [] # presence  - "наличие"
    
    rectangles_two_coordinates = []
    output = image.copy()
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1

    color_text = (0,0,255)
    color_outline = (0,0,255)
    thickness = 2

    for i in range(len(locations[0])):
        #алгоритмическая часть, где идет рассчет координат
        top_left = (locations[1][i], locations[0][i]) # (x,y)
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
        
        rectangles_two_coordinates.append((top_left, bottom_right))
      
        #графическая часть, генерация обводок и изображений
        cv2.rectangle(output, top_left, bottom_right, color_outline, 2)
        text = f"Indicator {i+1} - {calculating_quadrant_number(top_left)}"
        # text = f"Object {i+1} - {top_left}"
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_origin = (top_left[0], top_left[1] - int(1.3 * text_size[1]))
        cv2.putText(output, text, text_origin,
                    font, font_scale, color_text, thickness, lineType=cv2.LINE_AA)
        
    if visual_save is True:
        cv2.imwrite(f"detected_objects_{panel_name}_{flag}.png", output)
       
    if visual_show is True:   
        cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
        width, height = 800, 1200
        cv2.imshow("Detected Objects", output)
        cv2.resizeWindow("Detected Objects", width, height)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    return rectangles_two_coordinates


def visualize_results_indicator(panel_name, image: np.ndarray, template: np.ndarray, unique_data: pd.DataFrame, flag,  visual_show = False, visual_save = False):
    """Визуализирует результаты обнаружения объектов и создает кортежи двух координат."""
    locations = (np.array(unique_data['x']), np.array(unique_data['y']))
    
    list_presence_of_circle = [] # presence  - "наличие"
    
    rectangles_two_coordinates = []
    output = image.copy()
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1

    color_text = (0,255,0) 
    color_outline = (0,255,0) 
    thickness = 2

    for i in range(len(locations[0])):
        #алгоритмическая часть, где идет рассчет координат
        top_left = (locations[1][i], locations[0][i]) # (x,y)
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
        
        rectangles_two_coordinates.append((top_left, bottom_right))
      
        #графическая часть, генерация обводок и изображений
        cv2.rectangle(output, top_left, bottom_right, color_outline, 2)
        text = f"Indicator {i+1} - {calculating_quadrant_number(top_left)}"
        # text = f"Object {i+1} - {top_left}"
        text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
        text_origin = (top_left[0], top_left[1] - int(1.3 * text_size[1]))
        cv2.putText(output, text, text_origin,
                    font, font_scale, color_text, thickness, lineType=cv2.LINE_AA)
        
    if visual_save is True:
        cv2.imwrite(f"detected_objects_{panel_name}_{flag}.png", output)
       
    if visual_show is True:   
        cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
        width, height = 800, 1200
        cv2.imshow("Detected Objects", output)
        cv2.resizeWindow("Detected Objects", width, height)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    return rectangles_two_coordinates

def visualize_results_armatura(panel_name, image: np.ndarray, template: np.ndarray, unique_data: pd.DataFrame, flag, visual_show = False, visual_save = False):
    """Визуализирует результаты обнаружения объектов и создает кортежи двух координат."""
    locations = (np.array(unique_data['x']), np.array(unique_data['y']))
    
    list_presence_of_circle = [] # presence  - "наличие"
    
    rectangles_two_coordinates = []
    output = image.copy()
    
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1
    '''
    наоборот!
    (0,0,0) - черный
    (255,0,0) - красный
    (0,255,0) - зеленый
    (0,0,255) - синий
    (255,255,255) - белый
    '''
    color_text = (0,0,255)
    color_outline = (0, 0, 255)
    thickness = 2

    for i in range(len(locations[0])):
        
        #алгоритмическая часть, где идет рассчет координат
        top_left = (locations[1][i], locations[0][i]) # (x,y)
        bottom_right = (top_left[0] + template.shape[1], top_left[1] + template.shape[0])
        
        rectangles_two_coordinates.append((top_left, bottom_right))
        
        
        if flag == 'switch':
            right_shift = 0 # пикселей
            down_shift = 200 # пикселей
            x, y = (top_left[0] + right_shift, top_left[1]+down_shift) 
            pixel_color = image[y, x]
            bgr_color_of_circle = (str(pixel_color))
            
            if bgr_color_of_circle != '[191 191 191]':
                list_presence_of_circle.append('2B-2006')
            else:
                list_presence_of_circle.append('2В-2045')
            
        if flag == 'armatura':
            
            right_shift = 225 # пикселей
            down_shift = 200 # пикселей
            
            x, y = (top_left[0]+right_shift, top_left[1]+down_shift) 
            pixel_color = image[y, x]
            bgr_color_of_circle = (str(pixel_color))

            if bgr_color_of_circle == '[191 191 191]':
                
                right_shift = 0 # пикселей
                down_shift = 72 # пикселей
                
                x, y = (top_left[0]+right_shift, top_left[1]+down_shift) 
                pixel_color = image[y, x]
                bgr_color_of_circle = (str(pixel_color))
                
                if bgr_color_of_circle != '[255 255 255]': #[255 255 255] == белый
                    if bgr_color_of_circle == '[254, 214, 188]': #[254, 214, 188] == синий, буква Ш
                        list_presence_of_circle.append('Ш - Арматура')
                    else:
                        list_presence_of_circle.append('Регулирующая арматура')
                else:
                    list_presence_of_circle.append('2B-2059')
            else:
                list_presence_of_circle.append('2B-2001')
            
            # [ 67 101 206] - BGR, оранжевый
            # [191 191 191] - BGR, серый
        if visual_save is True:  
            #графическая часть, генерация обводок и изображений
            cv2.rectangle(output, top_left, bottom_right, color_outline, 2)
            text = f"{flag} {i+1} - {calculating_quadrant_number(top_left)}"
            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
            text_origin = (top_left[0], top_left[1] - int(1.3 * text_size[1]))
            cv2.putText(output, text, text_origin,
                        font, font_scale, color_text, thickness, lineType=cv2.LINE_AA)
            
    if visual_save is True:
        cv2.imwrite(f"detected_objects_{panel_name}_{flag}.png", output)
       
    if visual_show is True:   
        cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
        width, height = 800, 1200
        cv2.imshow("Detected Objects", output)
        cv2.resizeWindow("Detected Objects", width, height)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
    return rectangles_two_coordinates, list_presence_of_circle

# содержание и форма гегель

# def find_templates(image_path: str, template_path: str): #-> Tuple[List[Tuple[int, int]], List[Tuple[Tuple[int, int], Tuple[int, int]]]]:
#     """Находит шаблоны в изображении."""
#     gray_image, gray_template, image, template = preprocess_images(image_path, template_path)
#     locations = detect_objects(gray_image, gray_template, threshold=0.8)
#     df = filter_unique_objects(locations)
#     rectangles = remove_overlapping_objects(df)
#     rectangles_two_coord = visualize_results(image, template, rectangles)
#     # визуализация найденных элементов и удвоение координат
    
#     # return rectangles
    
#     return rectangles_two_coord, rectangles



