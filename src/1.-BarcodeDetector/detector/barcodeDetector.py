# detector/barcode_detector.py
"""
Clase principal del detector de códigos de barras
"""

import cv2
from datetime import datetime
from typing import Optional

from utils.cameraConfig import CameraManager
from utils.display import DisplayManager
from detector.imageProcessor import ImageProcessor
from detector.validator import BarcodeValidator
from storage.codeStorage import CodeStorage
from config import DETECTION_CONFIG


class BarcodeDetector:
    """
    Detector principal de códigos de barras con todas las funcionalidades
    """

    def __init__(self, camera_index: Optional[int] = None):
        """
        Inicializa el detector de códigos de barras

        Args:
            camera_index: Índice de la cámara (usa configuración por defecto si es None)
        """
        # Inicializar componentes
        self.camera_manager = CameraManager(camera_index)
        self.display_manager = DisplayManager()
        self.image_processor = ImageProcessor()
        self.validator = BarcodeValidator()
        self.storage = CodeStorage()

        # Configuración
        self.detection_config = DETECTION_CONFIG

        # Estado del detector
        self.is_running = False
        self.processing_mode = 0
        self.cap = None

    def initialize(self) -> bool:
        """
        Inicializa todos los componentes del detector

        Returns:
            True si se inicializó correctamente
        """
        try:
            # Inicializar cámara
            self.cap = self.camera_manager.initialize_camera()

            # Optimizar cámara para códigos de barras
            self.camera_manager.optimize_for_barcodes()

            return True

        except Exception as e:
            print(f"Error inicializando detector: {e}")
            return False

    def process_detected_code(self, barcode_data: str, barcode_type: str):
        """
        Procesa un código detectado aplicando validaciones

        Args:
            barcode_data: Código detectado
            barcode_type: Tipo de código
        """
        # Validar el código
        is_valid = self.validator.validate_code(barcode_data, barcode_type)
        is_pharmaceutical = self.validator.is_pharmaceutical_code(
            barcode_data, barcode_type)

        # Añadir al almacenamiento
        detection_info = self.storage.add_detected_code(
            barcode_data,
            barcode_type,
            is_valid,
            extra_info={'es_farmaceutico': is_pharmaceutical}
        )

        # Mostrar mensaje
        self.display_manager.print_detection_message(
            barcode_data,
            barcode_type,
            detection_info['timestamp'],
            is_valid,
            len(self.storage.detected_codes)
        )

    def process_frame(self, frame):
        """
        Procesa un frame completo para detectar códigos de barras

        Args:
            frame: Frame de la cámara

        Returns:
            Frame procesado con información visual
        """
        # Preprocesar frame
        original_frame, processed_frames = self.image_processor.preprocess_frame(
            frame)

        # Intentar detectar códigos
        barcodes = []
        scale_factor = 1.0

        # Probar con diferentes frames procesados
        for processed_frame in processed_frames:
            detected_barcodes, detected_scale = self.image_processor.detect_with_multiple_scales(
                processed_frame)
            if detected_barcodes:
                barcodes = detected_barcodes
                scale_factor = detected_scale
                break

        # Procesar códigos encontrados
        for barcode in barcodes:
            barcode_value, barcode_type = self.display_manager.draw_barcode_info(
                original_frame, barcode, scale_factor
            )

            # Solo procesar si no es duplicado reciente
            if self.storage.should_process_detection(barcode_value):
                self.process_detected_code(barcode_value, barcode_type)

        # Añadir información de interfaz
        self.display_manager.draw_interface_info(
            original_frame,
            len(self.storage.detected_codes),
            self.processing_mode,
            self.detection_config['processing_modes']
        )

        return original_frame

    def handle_keyboard_input(self, key: int) -> bool:
        """
        Maneja la entrada del teclado

        Args:
            key: Código de tecla presionada

        Returns:
            True si debe continuar, False si debe salir
        """
        if key == ord('q'):
            return False

        elif key == ord('c'):
            self.storage.clear_history()
            self.display_manager.print_system_message('history_cleared')

        elif key == ord('s'):
            self.processing_mode = (
                self.processing_mode + 1) % len(self.detection_config['processing_modes'])
            mode_name = self.detection_config['processing_modes'][self.processing_mode]
            self.display_manager.print_system_message(
                'mode_changed', mode_name)

        elif key == ord('e'):
            # Exportar códigos a JSON
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"codigos_detectados_{timestamp}.json"
            if self.storage.export_to_json(filename):
                print(f"✅ Códigos exportados a {filename}")
            else:
                print("❌ Error exportando códigos")

        elif key == ord('r'):
            # Mostrar estadísticas
            stats = self.storage.get_statistics()
            print("\n📊 ESTADÍSTICAS:")
            print(f"   Total: {stats['total']}")
            print(f"   Válidos: {stats['valid']}")
            print(f"   Farmacéuticos: {stats['pharmaceutical']}")
            print(f"   Tasa de detección: {stats['detection_rate']:.2%}")

        return True

    def run(self):
        """
        Ejecuta el detector en tiempo real
        """
        if not self.initialize():
            print("❌ Error: No se pudo inicializar el detector")
            return

        # Mostrar mensajes de inicio
        self.display_manager.print_startup_messages()
        print("   - Presiona 'e' para exportar códigos a JSON")
        print("   - Presiona 'r' para ver estadísticas")

        self.is_running = True

        try:
            while self.is_running and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    self.display_manager.print_system_message('camera_error')
                    break

                # Procesar frame
                processed_frame = self.process_frame(frame)

                # Mostrar frame
                self.display_manager.display_frame(processed_frame)

                # Manejar entrada de teclado
                key = cv2.waitKey(1) & 0xFF
                if key != 255:  # Si se presionó alguna tecla
                    if not self.handle_keyboard_input(key):
                        break

        except KeyboardInterrupt:
            self.display_manager.print_system_message('user_interrupt')

        finally:
            self.cleanup()

    def cleanup(self):
        """
        Limpia recursos y muestra resumen final
        """
        # Mostrar resumen final
        self.display_manager.print_final_summary(self.storage.detected_codes)

        # Mostrar estadísticas finales
        stats = self.storage.get_statistics()
        if stats['total'] > 0:
            print("\n📈 ESTADÍSTICAS FINALES:")
            print(f"   Tasa de éxito: {stats['detection_rate']:.2%}")
            print(
                f"   Códigos farmacéuticos: {stats['pharmaceutical']}/{stats['total']}")

            if stats['types_distribution']:
                print("   Distribución por tipos:")
                for code_type, count in stats['types_distribution'].items():
                    print(f"     - {code_type}: {count}")

        # Liberar recursos
        self.camera_manager.release()
        self.display_manager.cleanup()
        self.is_running = False

    def get_detected_codes(self):
        """
        Obtiene la lista de códigos detectados

        Returns:
            Lista de códigos detectados
        """
        return self.storage.get_detected_codes()

    def export_codes(self, filename: str, format_type: str = 'json') -> bool:
        """
        Exporta códigos a archivo

        Args:
            filename: Nombre del archivo
            format_type: Formato ('json' o 'csv')

        Returns:
            True si se exportó correctamente
        """
        if format_type.lower() == 'json':
            return self.storage.export_to_json(filename)
        elif format_type.lower() == 'csv':
            return self.storage.export_to_csv(filename)
        else:
            return False
