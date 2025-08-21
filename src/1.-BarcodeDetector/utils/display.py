# utils/display.py
"""
Funciones para visualización y interfaz de usuario
"""

import cv2
from config import UI_CONFIG, MESSAGES


class DisplayManager:
    """
    Gestiona la visualización y elementos de interfaz de usuario
    """

    def __init__(self):
        self.ui_config = UI_CONFIG
        self.messages = MESSAGES

    def draw_barcode_info(self, frame, barcode, scale_factor=1.0):
        """
        Dibuja información del código de barras en el frame

        Args:
            frame: Frame donde dibujar
            barcode: Objeto barcode de pyzbar
            scale_factor: Factor de escala aplicado

        Returns:
            tuple: (código, tipo_código)
        """
        # Ajustar coordenadas por el factor de escala
        (x, y, w, h) = barcode.rect
        x = int(x / scale_factor)
        y = int(y / scale_factor)
        w = int(w / scale_factor)
        h = int(h / scale_factor)

        # Dibujar rectángulo alrededor del código
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            self.ui_config['rectangle_color'],
            self.ui_config['rectangle_thickness']
        )

        # Mostrar valor del código
        barcode_value = barcode.data.decode('utf-8')
        cv2.putText(
            frame,
            barcode_value,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.ui_config['rectangle_color'],
            2
        )

        # Mostrar tipo de código
        cv2.putText(
            frame,
            barcode.type,
            (x, y + h + 20),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            self.ui_config['type_color'],
            1
        )

        return barcode_value, barcode.type

    def draw_interface_info(self, frame, detected_count, current_mode, mode_names):
        """
        Dibuja información de la interfaz en el frame

        Args:
            frame: Frame donde dibujar
            detected_count: Número de códigos detectados
            current_mode: Modo de procesamiento actual
            mode_names: Lista de nombres de modos
        """
        # Información principal
        info_text = f"Codigos detectados: {detected_count} | Modo: {mode_names[current_mode]}"
        cv2.putText(
            frame,
            info_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            self.ui_config['font_scale'],
            self.ui_config['font_color'],
            self.ui_config['font_thickness']
        )

        # Instrucciones en la parte inferior
        instructions = "q: salir | c: limpiar | s: cambiar modo"
        cv2.putText(
            frame,
            instructions,
            (10, frame.shape[0] - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            self.ui_config['font_color'],
            1
        )

    def display_frame(self, frame):
        """
        Muestra el frame en la ventana

        Args:
            frame: Frame a mostrar
        """
        cv2.imshow(self.ui_config['window_name'], frame)

    def print_startup_messages(self):
        """
        Muestra mensajes de inicio en consola
        """
        startup = self.messages['startup']
        print(startup['title'])
        for instruction in startup['instructions']:
            print(instruction)
        print("\n" + startup['separator'])

    def print_detection_message(self, code_data, code_type, timestamp, is_valid, total_count):
        """
        Muestra mensaje de detección en consola

        Args:
            code_data: Código detectado
            code_type: Tipo de código
            timestamp: Marca de tiempo
            is_valid: Si es válido según validación
            total_count: Total de códigos detectados
        """
        detection = self.messages['detection']

        if is_valid and code_type == 'EAN13':
            print(f"\n{detection['valid_code']}")
            print(f"   Código: {code_data}")
            print(f"   Tipo: {code_type}")
            print(f"   Hora: {timestamp}")
            print(f"   Total detectados: {total_count}")
        else:
            print(f"\n{detection['general_code']}")
            print(f"   Código: {code_data}")
            print(f"   Tipo: {code_type}")
            print(f"   Hora: {timestamp}")
            if code_type != 'EAN13':
                print(f"   {detection['not_ean13']}")

    def print_system_message(self, message_type, extra_info=None):
        """
        Muestra mensajes del sistema

        Args:
            message_type: Tipo de mensaje ('camera_error', 'user_interrupt', etc.)
            extra_info: Información adicional para el mensaje
        """
        system_msg = self.messages['system'].get(message_type, message_type)

        if extra_info:
            print(f"\n{system_msg} {extra_info}")
        else:
            print(f"\n{system_msg}")

    def print_final_summary(self, detected_codes):
        """
        Muestra resumen final de códigos detectados

        Args:
            detected_codes: Lista de códigos detectados
        """
        print(f"\n📊 RESUMEN FINAL:")
        print(f"   Total de códigos detectados: {len(detected_codes)}")

        if detected_codes:
            # Separar códigos válidos e inválidos
            valid_codes = [
                code for code in detected_codes if code.get('valido', False)]
            invalid_codes = [
                code for code in detected_codes if not code.get('valido', False)]

            if valid_codes:
                print(f"\n✅ CÓDIGOS EAN-13 VÁLIDOS ({len(valid_codes)}):")
                for i, code_info in enumerate(valid_codes, 1):
                    print(
                        f"   {i}. {code_info['codigo']} - {code_info['timestamp']}")

            if invalid_codes:
                print(f"\n📦 OTROS CÓDIGOS DETECTADOS ({len(invalid_codes)}):")
                for i, code_info in enumerate(invalid_codes, 1):
                    print(
                        f"   {i}. {code_info['codigo']} ({code_info['tipo']}) - {code_info['timestamp']}")

        print(f"\n{self.messages['system']['goodbye']}")

    def cleanup(self):
        """
        Limpia recursos de visualización
        """
        cv2.destroyAllWindows()
