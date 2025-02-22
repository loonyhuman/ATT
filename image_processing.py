import cv2
import numpy as np
import pandas as pd
from typing import List, Tuple

class ImageProcessor:
    def __init__(self, min_distance: int = 20, threshold: float = 0.8):
        self.min_distance = min_distance
        self.threshold = threshold

    @staticmethod
    def load_image(image_path: str) -> np.ndarray:
        return cv2.imread(image_path)

    @staticmethod
    def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def preprocess_images(self, image_path: str, template_path: str) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        try:
            # Загружаем изображения
            image = self.load_image(image_path)
            template = self.load_image(template_path)
            
            # Проверяем, что изображения загружены
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            if template is None:
                raise ValueError(f"Failed to load template: {template_path}")
            
            # Преобразуем в оттенки серого
            gray_image = self.convert_to_grayscale(image)
            gray_template = self.convert_to_grayscale(template)
            
            # Проверяем, что преобразование выполнено успешно
            if gray_image is None or gray_template is None:
                raise ValueError("Failed to convert images to grayscale")
            
            # Возвращаем результаты
            return gray_image, gray_template, image, template
        
        except Exception as e:
            print(f"Error in preprocess_images: {e}")
            return None, None, None, None  # Возвращаем 4 значения, чтобы избежать ошибки распаковки

    def detect_objects(self, gray_image: np.ndarray, gray_template: np.ndarray) -> List[Tuple[int, int]]:
        result = cv2.matchTemplate(gray_image, gray_template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= self.threshold)
        return list(zip(locations[1], locations[0]))

    def filter_unique_objects(self, locations: List[Tuple[int, int]]) -> pd.DataFrame:
        df = pd.DataFrame(locations, columns=['x', 'y'])
        return df.drop_duplicates().sort_values(by=['x', 'y']).reset_index(drop=True)

    def remove_overlapping_objects(self, df: pd.DataFrame) -> pd.DataFrame:
        objects_to_remove = []
        for i in range(len(df)):
            if i in objects_to_remove:
                continue
            current_row = df.iloc[i]
            for j in range(i + 1, len(df)):
                if j in objects_to_remove:
                    continue
                other_row = df.iloc[j]
                if abs(current_row['x'] - other_row['x']) < self.min_distance and abs(current_row['y'] - other_row['y']) < self.min_distance:
                    objects_to_remove.append(j)
        return df.drop(index=objects_to_remove).reset_index(drop=True)

    def visualize_results(self, image: np.ndarray, template: np.ndarray, unique_data: pd.DataFrame, visual_show: bool = False, visual_save: bool = False) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        rectangles = []
        output = image.copy()
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        color_text = (0, 0, 255)
        color_outline = (0, 0, 255)
        thickness = 2

        for i, (x, y) in unique_data.iterrows():
            top_left = (x, y)
            bottom_right = (x + template.shape[1], y + template.shape[0])
            rectangles.append((top_left, bottom_right))
            
            cv2.rectangle(output, top_left, bottom_right, color_outline, 2)
            text = f"Object {i+1} - {self.calculate_quadrant_number(top_left)}"
            text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
            text_origin = (top_left[0], top_left[1] - int(1.3 * text_size[1]))
            cv2.putText(output, text, text_origin, font, font_scale, color_text, thickness, lineType=cv2.LINE_AA)

        if visual_save:
            cv2.imwrite("detected_objects.png", output)

        if visual_show:
            cv2.namedWindow("Detected Objects", cv2.WINDOW_NORMAL)
            cv2.imshow("Detected Objects", output)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        return rectangles

    @staticmethod
    def calculate_quadrant_number(coor: Tuple[int, int]) -> str:
        alphabet = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        sq_side = 317.475
        column_num = round(coor[1] / sq_side)
        row_num = round(coor[0] / sq_side)
        return f"{alphabet[column_num // len(alphabet)]}{alphabet[column_num % len(alphabet)]}-{int(1 + row_num % len(alphabet))}"