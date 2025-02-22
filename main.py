import os
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from image_processing import ImageProcessor
from data_processing import DataProcessor
from text_recognition import TextRecognizer

def process_single_template(image_processor, data_processor, text_recognizer, image_path, template_path, element_name, panel_name, output_folder):
    """
    Обрабатывает один шаблон на изображении и сохраняет результаты.
    """
    print(f"Processing template: {os.path.basename(template_path)}")

    # Предварительная обработка изображений
    gray_image, gray_template, image, template = image_processor.preprocess_images(image_path, template_path)
    
    # Проверяем, что все значения возвращены корректно
    if gray_image is None or gray_template is None or image is None or template is None:
        print("Error: Failed to preprocess images")
        return None

    # Обнаружение объектов
    with tqdm(total=4, desc="Processing", ncols=75) as pbar:
        try:
            locations = image_processor.detect_objects(gray_image, gray_template)
            pbar.update(1)

            df_unique = image_processor.filter_unique_objects(locations)
            pbar.update(1)

            df_target = image_processor.remove_overlapping_objects(df_unique)
            pbar.update(1)

            rectangles = image_processor.visualize_results(image, template, df_target, visual_show=False, visual_save=True)
            pbar.update(1)
            
        except Exception as e:
            print(f"Error during object detection: {e}")
            return None
    # Распознавание текста
    try:
        kks_text = text_recognizer.kks_recognition(rectangles, image_path)
        units_list = text_recognizer.unit_recognition(rectangles, image_path)
        kks_text_formatted = text_recognizer.kks_norm(kks_text)
    except Exception as e:
        print(f"Error during text recognition: {e}")
        return None

    # Предварительная обработка данных и сохранение в Excel
    try:
        preprocessed_data = data_processor.preprocess_data(rectangles, kks_text_formatted, units_list)
        output_file = f"{element_name}_output_{panel_name}.xlsx"
        data_processor.save_data(preprocessed_data, output_file, output_folder)
    except Exception as e:
        print(f"Error during data processing: {e}")
        return None

    print(f"Results saved to {output_file}\n")
    return output_file

def main():
    # Настройки
    
    # Определяем базовую директорию (текущую директорию скрипта)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    # Определяем путь к папке проекта
    project_folder = base_dir
    #os.path.join(base_dir, 'template_programm_divided')
    
    panel_name = '10CWA62GA201'
    element_names = ['indicator']  # Добавьте сюда все необходимые элементы
    flags_indicator = ['small']
    output_folder = rf'{project_folder}'

    # Путь к изображению
    image_path = rf"{output_folder}\{panel_name}.png"

    print(image_path)
    
    # Инициализация классов
    image_processor = ImageProcessor()
    data_processor = DataProcessor()
    text_recognizer = TextRecognizer()

    # Список задач для многопоточной обработки
    tasks = []

    # Создаем пул потоков
    with ThreadPoolExecutor(max_workers=4) as executor:  # max_workers - количество потоков
        for element_name in element_names:
            for flag in flags_indicator:
                template_path = rf"{output_folder}\templates\{element_name}_{flag}.png"
                if os.path.exists(template_path):
                    # Добавляем задачу в пул потоков
                    future = executor.submit(
                        process_single_template,
                        image_processor, data_processor, text_recognizer,
                        image_path, template_path, element_name, panel_name, output_folder
                    )
                    tasks.append(future)
                else:
                    print(f"Template not found: {template_path}")

        # Ожидаем завершения всех задач и собираем результаты
        for future in as_completed(tasks):
            try:
                result = future.result()
                print(f"Task completed: {result}")
            except Exception as e:
                print(f"Task failed: {e}")

    print("All templates processed!")

if __name__ == "__main__":
    main()