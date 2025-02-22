import cv2
import numpy as np

def load_image(image_path: str) -> np.ndarray:
    """Загружает изображение."""
    return cv2.imread(image_path)

def load_template(template_path: str) -> np.ndarray:
    """Загружает шаблон."""
    return cv2.imread(template_path)

def convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """Преобразует изображение в оттенки серого."""
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
