# utils/camera_config.py
"""
Configuración y gestión de cámara para detección de códigos de barras
"""

import cv2
from config import CAMERA_CONFIG


class CameraManager:
    """
    Gestiona la configuración y operaciones de la cámara
    """

    def __init__(self, camera_index=None):
        """
        Inicializa el gestor de cámara

        Args:
            camera_index (int): Índice de cámara (usa config si es None)
        """
        self.config = CAMERA_CONFIG
        self.camera_index = camera_index or self.config['index']
        self.cap = None

    def initialize_camera(self):
        """
        Inicializa y configura la cámara

        Returns:
            cv2.VideoCapture: Objeto de captura configurado
        """
        self.cap = cv2.VideoCapture(self.camera_index)

        if not self.cap.isOpened():
            raise RuntimeError(
                f"No se puede abrir la cámara con índice {self.camera_index}")

        # Aplicar configuraciones
        self._apply_camera_settings()

        return self.cap

    def _apply_camera_settings(self):
        """
        Aplica las configuraciones de cámara definidas en config
        """
        if not self.cap:
            return

        # Configurar resolución
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config['width'])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config['height'])

        # Configurar FPS
        self.cap.set(cv2.CAP_PROP_FPS, self.config['fps'])

        # Configurar autofocus si es compatible
        if self.config['autofocus']:
            try:
                self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)
            except:
                pass

        # Configurar enfoque manual si es compatible
        try:
            self.cap.set(cv2.CAP_PROP_FOCUS, self.config['focus'])
        except:
            pass

    def get_camera_info(self):
        """
        Obtiene información actual de la cámara

        Returns:
            dict: Información de la cámara
        """
        if not self.cap:
            return {}

        return {
            'width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            'height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            'fps': int(self.cap.get(cv2.CAP_PROP_FPS)),
            'autofocus': bool(self.cap.get(cv2.CAP_PROP_AUTOFOCUS)),
            'focus': int(self.cap.get(cv2.CAP_PROP_FOCUS)),
            'brightness': int(self.cap.get(cv2.CAP_PROP_BRIGHTNESS)),
            'contrast': int(self.cap.get(cv2.CAP_PROP_CONTRAST)),
            'saturation': int(self.cap.get(cv2.CAP_PROP_SATURATION))
        }

    def optimize_for_barcodes(self):
        """
        Aplica configuraciones específicas para mejorar detección de códigos de barras
        """
        if not self.cap:
            return

        # Configuraciones adicionales para códigos de barras
        try:
            # Aumentar contraste
            self.cap.set(cv2.CAP_PROP_CONTRAST, 50)

            # Reducir saturación para mejor procesamiento en escala de grises
            self.cap.set(cv2.CAP_PROP_SATURATION, 30)

            # Configurar exposición automática
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)

        except Exception as e:
            # Algunas cámaras no soportan todas las propiedades
            pass

    def test_camera_capabilities(self):
        """
        Prueba las capacidades de la cámara y reporta qué funciona

        Returns:
            dict: Capacidades disponibles
        """
        if not self.cap:
            return {}

        capabilities = {}
        test_properties = {
            'autofocus': cv2.CAP_PROP_AUTOFOCUS,
            'focus': cv2.CAP_PROP_FOCUS,
            'brightness': cv2.CAP_PROP_BRIGHTNESS,
            'contrast': cv2.CAP_PROP_CONTRAST,
            'saturation': cv2.CAP_PROP_SATURATION,
            'auto_exposure': cv2.CAP_PROP_AUTO_EXPOSURE,
            'exposure': cv2.CAP_PROP_EXPOSURE,
            'zoom': cv2.CAP_PROP_ZOOM
        }

        for name, prop in test_properties.items():
            try:
                # Intentar leer el valor
                value = self.cap.get(prop)
                capabilities[name] = {
                    'supported': True,
                    'current_value': value
                }

                # Intentar escribir un valor para probar si es modificable
                test_value = value + 1 if value < 100 else value - 1
                self.cap.set(prop, test_value)
                new_value = self.cap.get(prop)

                capabilities[name]['writable'] = new_value != value

                # Restaurar valor original
                self.cap.set(prop, value)

            except:
                capabilities[name] = {
                    'supported': False,
                    'writable': False
                }

        return capabilities

    def release(self):
        """
        Libera los recursos de la cámara
        """
        if self.cap:
            self.cap.release()
            self.cap = None
