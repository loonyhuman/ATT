import pandas as pd
import numpy as np
from typing import List, Tuple
import copy
import db_postgres


def zeroing_out(x):
    # добавление строчного нуля перед цифрами в координатах
    # используется для модификации столбца df_rectangles
    return '0'+ x if len(x) == 1 else x

def preprocess_data_2B_2009(rectangles):# -> pd.DataFrame:
    """Преобразует прямоугольники в DataFrame."""
    df = pd.DataFrame(rectangles)
    df.columns = ['first_coor', 'second_coor']
    """создаем два столбца с кортежами вида (х,у), где 
    первый является верхней левой координатой, а второй - нижней правой"""
    
        #создаем 4 новых столбца для каждого из элементов кортежей, значения в пикселях
    df['first_coor_x_template'] = df['first_coor'].apply(lambda x: x[0])
    df['first_coor_y_template'] = df['first_coor'].apply(lambda x: x[1])
    df['second_coor_x_template'] = df['second_coor'].apply(lambda x: x[0])
    df['second_coor_y_template'] = df['second_coor'].apply(lambda x: x[1])
    
    
    # Убираем исходные столбцы
    df = df[['first_coor_x_template',
                        'first_coor_y_template', 
                        'second_coor_x_template', 
                        'second_coor_y_template']]
    # добавляем столбец с ККS

    # делаем глубокую копию df
    df_rectangles = copy.deepcopy(df)
    
    mm_pxl = 3.793627
    value_to_add = 0
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента),
    # в миллиметровом эквиваленте
    df_rectangles['x_coor_indicator'] = df_rectangles.\
        apply(lambda row: row['first_coor_x_template'] + value_to_add, axis=1)
        
    df_rectangles['y_coor_indicator'] = df_rectangles.\
        apply(lambda row: row['first_coor_y_template'] + value_to_add, axis=1)

    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    # sq_side = 24 * mm_pxl  * 3.12504049239 # <- деление нового изображения на старое
    sq_side = 317.475
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента)
    df_rectangles['column_num'] = round(df_rectangles['x_coor_indicator']/sq_side) 
    df_rectangles['row_num'] = round(df_rectangles['y_coor_indicator']/sq_side)
    
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента),
    # с числом для горизонтального положения и с латиницей для вертикального
    df_rectangles['str_x'] = df_rectangles.apply(lambda row: str(1 + int(row['column_num'] % sq_side)), axis=1)
    df_rectangles['str_y'] = df_rectangles.apply(lambda row: 
        str(alphabet[np.int64(row['row_num'] // len(alphabet)).astype(int)] + 
            alphabet[np.int64(row['row_num'] % len(alphabet)).astype(int)]), 
        axis=1)

    # применила функцию добавления строчного нуля перед цифрами в координатах
    df_rectangles['str_x'] = df_rectangles['str_x'].apply(zeroing_out)
    
    # создание массива со строками-координатами элементом для экспорта в .csv-файл
    coor_array = np.array(df_rectangles['str_y']) + '-' + np.array(df_rectangles['str_x'])

    df_rectangles['Coordinate'] = pd.Series(coor_array.flatten(), name='Coordinate')
    
    '''
    # подключение к БД с данными о ККS
    # columns_of_db - список строк названий столбцов из бд
    # selected_data_from_db - список кортежей с полным перечнем данных из бд
    selected_data_from_db, columns_of_db = db_postgres.main()[:2]
    
    column_names = columns_of_db[1:]
    kks_data = [x[0]  for x in selected_data_from_db]
    
    df_kks_db = copy.deepcopy(df_rectangles)
    
    # цикл по добавлению столбцов, заполненных символом #, из списка строк названий столбцов бд
    # не считая значения kks, который уже есть в исходной таблице
    for i in column_names:
        df_kks_db[f'{i}'] = '#'
    
      
    index_count = 0
    for i in df_kks_db['KKS']:
        index_count +=1
        if i in kks_data: 
            index_kks_df = index_count
            index_kks_db= kks_data.index(i)
            df_kks_db.loc[index_kks_df, column_names] = list(selected_data_from_db[index_kks_db][1:])
    '''
    return df_rectangles

def preprocess_data_indicator(rectangles, kks_list, units_list_rus):# -> pd.DataFrame:
    """Преобразует прямоугольники в DataFrame."""
    df = pd.DataFrame(rectangles)
    df.columns = ['first_coor', 'second_coor']
    """создаем два столбца с кортежами вида (х,у), где 
    первый является верхней левой координатой, а второй - нижней правой"""
    
        #создаем 4 новых столбца для каждого из элементов кортежей, значения в пикселях
    df['first_coor_x_template'] = df['first_coor'].apply(lambda x: x[0])
    df['first_coor_y_template'] = df['first_coor'].apply(lambda x: x[1])
    df['second_coor_x_template'] = df['second_coor'].apply(lambda x: x[0])
    df['second_coor_y_template'] = df['second_coor'].apply(lambda x: x[1])
    
    
    # Убираем исходные столбцы
    df = df[['first_coor_x_template',
                        'first_coor_y_template', 
                        'second_coor_x_template', 
                        'second_coor_y_template']]
    # добавляем столбец с ККS
    df['KKS'] = pd.Series(kks_list)

    # добавляем столбец с названием элемента
    
    df['Units'] = pd.Series(units_list_rus)
    
    # делаем глубокую копию df
    df_rectangles = copy.deepcopy(df)
    
    mm_pxl = 3.793627
    value_to_add = 0
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента),
    # в миллиметровом эквиваленте
    df_rectangles['x_coor_indicator'] = df_rectangles.\
        apply(lambda row: row['first_coor_x_template'] + value_to_add, axis=1)
        
    df_rectangles['y_coor_indicator'] = df_rectangles.\
        apply(lambda row: row['first_coor_y_template'] + value_to_add, axis=1)

    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    # sq_side = 24 * mm_pxl  * 3.12504049239 # <- деление нового изображения на старое
    sq_side = 317.475
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента)
    df_rectangles['column_num'] = round(df_rectangles['x_coor_indicator']/sq_side) 
    df_rectangles['row_num'] = round(df_rectangles['y_coor_indicator']/sq_side)
    
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента),
    # с числом для горизонтального положения и с латиницей для вертикального
    df_rectangles['str_x'] = df_rectangles.apply(lambda row: str(1 + int(row['column_num'] % sq_side)), axis=1)
    df_rectangles['str_y'] = df_rectangles.apply(lambda row: 
        str(alphabet[np.int64(row['row_num'] // len(alphabet)).astype(int)] + 
            alphabet[np.int64(row['row_num'] % len(alphabet)).astype(int)]), 
        axis=1)

    # применила функцию добавления строчного нуля перед цифрами в координатах
    df_rectangles['str_x'] = df_rectangles['str_x'].apply(zeroing_out)
    
    # создание массива со строками-координатами элементом для экспорта в .csv-файл
    coor_array = np.array(df_rectangles['str_y']) + '-' + np.array(df_rectangles['str_x'])

    df_rectangles['Coordinate'] = pd.Series(coor_array.flatten(), name='Coordinate')
    
    
    # подключение к БД с данными о ККS
    # columns_of_db - список строк названий столбцов из бд
    # selected_data_from_db - список кортежей с полным перечнем данных из бд
    selected_data_from_db, columns_of_db = db_postgres.main()[:2]
    
    column_names = columns_of_db[1:]
    kks_data = [x[0]  for x in selected_data_from_db]
    
    df_kks_db = copy.deepcopy(df_rectangles)
    
    # цикл по добавлению столбцов, заполненных символом #, из списка строк названий столбцов бд
    # не считая значения kks, который уже есть в исходной таблице
    r = False
    if r == True:
        for i in column_names:
            df_kks_db[f'{i}'] = '#'

        index_count = 0
        for i in df_kks_db['KKS']:
            index_count +=1
            if i in kks_data: 
                index_kks_df = index_count
                index_kks_db= kks_data.index(i)
                df_kks_db.loc[index_kks_df, column_names] = list(selected_data_from_db[index_kks_db][1:])

    return df_kks_db

def preprocess_data_armatura(rectangles, kks_list, list_presence_of_circle):# -> pd.DataFrame:
    """Преобразует прямоугольники в DataFrame."""
    df = pd.DataFrame(rectangles)
    df.columns = ['first_coor', 'second_coor']
    """создаем два столбца с кортежами вида (х,у), где 
    первый является верхней левой координатой, а второй - нижней правой"""
    
        #создаем 4 новых столбца для каждого из элементов кортежей, значения в пикселях
    df['first_coor_x_template'] = df['first_coor'].apply(lambda x: x[0])
    df['first_coor_y_template'] = df['first_coor'].apply(lambda x: x[1])
    df['second_coor_x_template'] = df['second_coor'].apply(lambda x: x[0])
    df['second_coor_y_template'] = df['second_coor'].apply(lambda x: x[1])
    
    
    # Убираем исходные столбцы
    df = df[['first_coor_x_template',
                        'first_coor_y_template', 
                        'second_coor_x_template', 
                        'second_coor_y_template']]
    # добавляем столбец с ККS
    df['KKS'] = pd.Series(kks_list)

    # добавляем столбец с названием элемента
    
    df['Name'] = pd.Series(list_presence_of_circle)
    
    # делаем глубокую копию df
    df_rectangles = copy.deepcopy(df)
    
    mm_pxl = 3.793627
    value_to_add = 0
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента),
    # в миллиметровом эквиваленте
    df_rectangles['x_coor_indicator'] = df_rectangles.\
        apply(lambda row: row['first_coor_x_template'] + value_to_add, axis=1)
        
    df_rectangles['y_coor_indicator'] = df_rectangles.\
        apply(lambda row: row['first_coor_y_template'] + value_to_add, axis=1)

    alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
    # sq_side = 24 * mm_pxl  * 3.12504049239 # <- деление нового изображения на старое
    sq_side = 317.475
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента)
    df_rectangles['column_num'] = round(df_rectangles['x_coor_indicator']/sq_side) 
    df_rectangles['row_num'] = round(df_rectangles['y_coor_indicator']/sq_side)
    
    
    # создали 2 столбца для новых координат (верхний левый угол самого элемента),
    # с числом для горизонтального положения и с латиницей для вертикального
    df_rectangles['str_x'] = df_rectangles.apply(lambda row: str(1 + int(row['column_num'] % sq_side)), axis=1)
    df_rectangles['str_y'] = df_rectangles.apply(lambda row: 
        str(alphabet[np.int64(row['row_num'] // len(alphabet)).astype(int)] + 
            alphabet[np.int64(row['row_num'] % len(alphabet)).astype(int)]), 
        axis=1)

    # применила функцию добавления строчного нуля перед цифрами в координатах
    df_rectangles['str_x'] = df_rectangles['str_x'].apply(zeroing_out)
    
    # создание массива со строками-координатами элементом для экспорта в .csv-файл
    coor_array = np.array(df_rectangles['str_y']) + '-' + np.array(df_rectangles['str_x'])

    df_rectangles['Coordinate'] = pd.Series(coor_array.flatten(), name='Coordinate')
    
    
    # подключение к БД с данными о ККS
    # columns_of_db - список строк названий столбцов из бд
    # selected_data_from_db - список кортежей с полным перечнем данных из бд
    selected_data_from_db, columns_of_db = db_postgres.main()[:2]
    
    column_names = columns_of_db[1:]
    kks_data = [x[0]  for x in selected_data_from_db]
    
    df_kks_db = copy.deepcopy(df_rectangles)
    print('print(df_rectangles)')
    print(df_rectangles)
    # цикл по добавлению столбцов, заполненных символом #, из списка строк названий столбцов бд
    # не считая значения kks, который уже есть в исходной таблице
    for i in column_names:
        df_kks_db[f'{i}'] = '#'
    
      
    index_count = 0
    for i in df_kks_db['KKS']:
        index_count +=1
        if i in kks_data: 
            index_kks_df = index_count
            index_kks_db= kks_data.index(i)
            df_kks_db.loc[index_kks_df, column_names] = list(selected_data_from_db[index_kks_db][1:])

    return df_rectangles, column_names
