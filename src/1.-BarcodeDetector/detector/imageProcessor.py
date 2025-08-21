# detector/image_processor.py
"""
Módulo para procesamiento de imágenes y mejora de detección
"""

import cv2
import numpy as np
from pyzbar import pyzbar
from config import IMAGE_PROCESSING, DETECTION_CONFIG


class ImageProcessor:
    """
    Clase para procesar imágenes y mejorar la detección de códigos de barras
    """

    def __init__(self):
        self.config = IMAGE_PROCESSING
        self.detection_config = DETECTION_CONFIG

    def preprocess_frame(self, frame):
        """
        Preprocesa el frame aplicando múltiples técnicas

        Args:
            frame: Frame de la cámara

        Returns:
            tuple: (frame_original, lista_frames_procesados)
        """
        processed_frames = []

        # 1. Frame original
        processed_frames.append(frame)

        # 2. Escala de grises
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_frames.append(gray)

        # 3. Mejora de contraste con CLAHE
        clahe = cv2.createCLAHE(
            clipLimit=self.config['clahe_clip_limit'],
            tileGridSize=self.config['clahe_tile_grid_size']
        )
        enhanced = clahe.apply(gray)
        processed_frames.append(enhanced)

        # 4. Binarización adaptativa
        binary = cv2.adaptiveThreshold(
            gray,
            self.config['adaptive_threshold_max_value'],
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            self.config['adaptive_threshold_block_size'],
            self.config['adaptive_threshold_c']
        )
        processed_frames.append(binary)

        # 5. Operaciones morfológicas
        kernel = np.ones(self.config['morphology_kernel_size'], np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        processed_frames.append(morph)

        return frame, processed_frames

    def apply_bilateral_filter(self, frame):
        """
        Aplica filtro bilateral para reducir ruido manteniendo bordes

        Args:
            frame: Frame a filtrar

        Returns:
            Frame filtrado
        """
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        return cv2.bilateralFilter(
            gray,
            self.config['bilateral_filter_d'],
            self.config['bilateral_filter_sigma_color'],
            self.config['bilateral_filter_sigma_space']
        )

    def detect_with_multiple_scales(self, frame):
        """
        Detecta códigos de barras usando múltiples escalas

        Args:
            frame: Frame a procesar

        Returns:
            tuple: (lista_barcodes, factor_escala_usado)
        """
        # Aplicar filtro bilateral
        filtered = self.apply_bilateral_filter(frame)

        # Símbolos específicos para medicamentos
        symbols = [
            pyzbar.ZBarSymbol.EAN13,
            pyzbar.ZBarSymbol.UPCA,
            pyzbar.ZBarSymbol.CODE128
        ]

        # Probar diferentes escalas
        for scale in self.detection_config['scales']:
            try:
                if scale != 1.0:
                    height, width = filtered.shape
                    new_width = int(width * scale)
                    new_height = int(height * scale)

                    if new_width > 0 and new_height > 0:
                        scaled = cv2.resize(filtered, (new_width, new_height))
                        barcodes = pyzbar.decode(scaled, symbols=symbols)
                    else:
                        continue
                else:
                    barcodes = pyzbar.decode(filtered, symbols=symbols)

                if barcodes:
                    return barcodes, scale

            except Exception as e:
                continue

        return [], 1.0

    def enhance_barcode_region(self, frame, barcode_rect):
        """
        Mejora específicamente la región donde se detectó un código de barras

        Args:
            frame: Frame original
            barcode_rect: Rectángulo del código de barras (x, y, w, h)

        Returns:
            Región mejorada
        """
        x, y, w, h = barcode_rect

        # Expandir la región ligeramente
        padding = 10
        x_start = max(0, x - padding)
        y_start = max(0, y - padding)
        x_end = min(frame.shape[1], x + w + padding)
        y_end = min(frame.shape[0], y + h + padding)

        # Extraer región
        region = frame[y_start:y_end, x_start:x_end]

        if len(region.shape) == 3:
            region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)

        # Aplicar mejoras específicas
        enhanced = cv2.GaussianBlur(region, (3, 3), 0)
        enhanced = cv2.convertScaleAbs(enhanced, alpha=1.2, beta=10)

        return enhanced
