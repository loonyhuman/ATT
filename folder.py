import os

# Определяем базовую директорию (текущую директорию скрипта)
base_dir = os.path.dirname(os.path.abspath(__file__))
# Определяем путь к папке проекта
project_folder = os.path.join(base_dir, 'template_programm_divided')


output_folder = rf'{project_folder}'
print(output_folder)

panel_name = '10CWA62GA201'
image_path = f"{f'{output_folder}'}//{panel_name}.png"

print(image_path)
'''
# Создаем папку проекта, если она не существует
if not os.path.exists(project_folder):
    os.makedirs(project_folder)

# Список папок, которые нужно создать внутри проектной папки
folders = ['data', 'scripts', 'output', 'logs', 'config']

# Создаем папки внутри проектной папки
for folder in folders:
    folder_path = os.path.join(project_folder, folder)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f'Папка создана: {folder_path}')
    else:
        print(f'Папка уже существует: {folder_path}')

# Выводим путь к проектной папке
print(f'Проектная папка: {project_folder}')'''