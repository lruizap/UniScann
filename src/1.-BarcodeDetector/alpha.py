import cv2
from pyzbar import pyzbar
import numpy as np
from datetime import datetime


class BarcodeDetector:
    def __init__(self, camera_index=0):
        """
        Inicializa el detector de códigos de barras

        Args:
            camera_index (int): Índice de la cámara (0 por defecto)
        """
        self.cap = cv2.VideoCapture(camera_index)

        # Configuración de cámara optimizada para códigos de barras
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)  # Mayor resolución
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        self.cap.set(cv2.CAP_PROP_AUTOFOCUS, 1)  # Autofocus activado

        # Intentar configurar el enfoque si es posible
        try:
            self.cap.set(cv2.CAP_PROP_FOCUS, 0)  # Enfoque automático
        except:
            pass

        # Variables para evitar detecciones duplicadas
        self.last_barcode = None
        self.last_detection_time = None
        self.detection_cooldown = 2.0  # segundos

        # Lista para almacenar códigos detectados
        self.detected_codes = []

    def is_valid_ean13(self, code):
        """
        Verifica si un código es un EAN-13 válido

        Args:
            code (str): Código a validar

        Returns:
            bool: True si es válido, False en caso contrario
        """
        # Verificar longitud
        if len(code) != 13:
            return False

        # Verificar que solo contenga dígitos
        if not code.isdigit():
            return False

        # Calcular dígito de control EAN-13
        odd_sum = sum(int(code[i]) for i in range(0, 12, 2))
        even_sum = sum(int(code[i]) for i in range(1, 12, 2))
        checksum = (10 - ((odd_sum + even_sum * 3) % 10)) % 10

        return checksum == int(code[12])

    def preprocess_frame(self, frame):
        """
        Preprocesa el frame para mejorar la detección de códigos de barras

        Args:
            frame: Frame de la cámara

        Returns:
            tuple: Frame original y lista de frames procesados
        """
        processed_frames = []

        # 1. Frame original (a veces funciona mejor)
        processed_frames.append(frame)

        # 2. Escala de grises simple
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        processed_frames.append(gray)

        # 3. Mejorar contraste con CLAHE
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        processed_frames.append(enhanced)

        # 4. Binarización adaptativa (muy útil para códigos de barras)
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                       cv2.THRESH_BINARY, 11, 2)
        processed_frames.append(binary)

        # 5. Operaciones morfológicas para limpiar la imagen
        kernel = np.ones((2, 2), np.uint8)
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        processed_frames.append(morph)

        return frame, processed_frames

    def draw_barcode_info(self, frame, barcode, scale_factor=1.0):
        """
        Dibuja información del código de barras en el frame (como tu código original)

        Args:
            frame: Frame donde dibujar
            barcode: Objeto barcode de pyzbar
            scale_factor: Factor de escala si se redimensionó la imagen
        """
        # Usar el mismo estilo que tu código original pero ajustar por escala
        (x, y, w, h) = barcode.rect

        # Ajustar coordenadas por el factor de escala
        x = int(x / scale_factor)
        y = int(y / scale_factor)
        w = int(w / scale_factor)
        h = int(h / scale_factor)

        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        barcodeValue = barcode.data.decode('utf-8')
        cv2.putText(frame, barcodeValue, (x, y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Añadir tipo de código
        cv2.putText(frame, barcode.type, (x, y + h + 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

        return barcodeValue, barcode.type

    def should_process_detection(self, barcode_data):
        """
        Verifica si debe procesar una nueva detección
        (evita duplicados por detecciones consecutivas)

        Args:
            barcode_data (str): Código detectado

        Returns:
            bool: True si debe procesar, False en caso contrario
        """
        current_time = datetime.now()

        if (self.last_barcode != barcode_data or
            self.last_detection_time is None or
                (current_time - self.last_detection_time).total_seconds() > self.detection_cooldown):

            self.last_barcode = barcode_data
            self.last_detection_time = current_time
            return True

        return False

    def process_detected_code(self, barcode_data, barcode_type):
        """
        Procesa un código detectado

        Args:
            barcode_data (str): Datos del código
            barcode_type (str): Tipo de código
        """
        if self.is_valid_ean13(barcode_data):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            detection_info = {
                'codigo': barcode_data,
                'tipo': barcode_type,
                'timestamp': timestamp,
                'valido': True
            }

            self.detected_codes.append(detection_info)

            print(f"\n✅ CÓDIGO VÁLIDO DETECTADO:")
            print(f"   Código: {barcode_data}")
            print(f"   Tipo: {barcode_type}")
            print(f"   Hora: {timestamp}")
            print(f"   Total detectados: {len(self.detected_codes)}")

        else:
            print(f"❌ Código inválido detectado: {barcode_data}")

    def detect_with_multiple_scales(self, frame):
        """
        Intenta detectar códigos con diferentes escalas, optimizado para reducir warnings

        Args:
            frame: Frame a procesar

        Returns:
            tuple: (barcodes, scale_factor_used)
        """
        # Convertir a escala de grises para mejor rendimiento
        if len(frame.shape) == 3:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        else:
            gray = frame

        # Filtrar el frame para reducir ruido que causa warnings
        # Aplicar un filtro bilateral para suavizar pero mantener bordes
        filtered = cv2.bilateralFilter(gray, 9, 75, 75)

        # Intentar con diferentes escalas
        # Reducir escalas para menos procesamiento
        scales = [1.0, 1.2, 0.8, 1.4]

        for scale in scales:
            try:
                if scale != 1.0:
                    height, width = filtered.shape
                    new_width = int(width * scale)
                    new_height = int(height * scale)
                    if new_width > 0 and new_height > 0:
                        scaled = cv2.resize(filtered, (new_width, new_height))
                        # Solo buscar códigos específicos para medicamentos
                        barcodes = pyzbar.decode(scaled, symbols=[
                                                 pyzbar.ZBarSymbol.EAN13, pyzbar.ZBarSymbol.UPCA, pyzbar.ZBarSymbol.CODE128])
                    else:
                        continue
                else:
                    # Solo buscar códigos específicos para medicamentos
                    barcodes = pyzbar.decode(filtered, symbols=[
                                             pyzbar.ZBarSymbol.EAN13, pyzbar.ZBarSymbol.UPCA, pyzbar.ZBarSymbol.CODE128])

                if barcodes:
                    return barcodes, scale

            except Exception as e:
                # Si hay error en una escala, continuar con la siguiente
                continue

        return [], 1.0

    def run(self):
        """
        Ejecuta el detector en tiempo real (basado en tu código original mejorado)
        """
        print("🎥 Iniciando detector de códigos de barras...")
        print("📋 Instrucciones:")
        print("   - Presiona 'q' para salir")
        print("   - Presiona 'c' para limpiar historial")
        print("   - Presiona 's' para cambiar modo de procesamiento")
        print("   - Mantén el código de barras estable frente a la cámara")
        print("\n" + "="*50)

        processing_mode = 0  # Modo de procesamiento actual
        mode_names = ["Original", "Escala de grises",
                      "Contraste mejorado", "Binarización", "Morfológico"]

        try:
            while self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret:
                    print("❌ Error: No se puede leer de la cámara")
                    break

                # Preprocesar frame con múltiples técnicas
                original_frame, processed_frames = self.preprocess_frame(frame)

                # Intentar detectar en múltiples versiones procesadas
                barcodes = []
                scale_factor = 1.0

                # Primero intentar con frames procesados
                for processed_frame in processed_frames:
                    detected_barcodes, detected_scale = self.detect_with_multiple_scales(
                        processed_frame)
                    if detected_barcodes:
                        barcodes = detected_barcodes
                        scale_factor = detected_scale
                        break

                # Procesar códigos encontrados (como tu código original)
                for barcode in barcodes:
                    barcodeValue, barcode_type = self.draw_barcode_info(
                        original_frame, barcode, scale_factor)

                    # Solo procesar si no es duplicado reciente
                    if self.should_process_detection(barcodeValue):
                        # Para medicamentos, verificar si es EAN-13
                        if barcode_type == 'EAN13':
                            self.process_detected_code(
                                barcodeValue, barcode_type)
                        else:
                            # Procesar otros tipos también
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            detection_info = {
                                'codigo': barcodeValue,
                                'tipo': barcode_type,
                                'timestamp': timestamp,
                                'valido': barcode_type == 'EAN13'
                            }

                            self.detected_codes.append(detection_info)

                            print(f"\n📦 CÓDIGO DETECTADO:")
                            print(f"   Código: {barcodeValue}")
                            print(f"   Tipo: {barcode_type}")
                            print(f"   Hora: {timestamp}")
                            if barcode_type != 'EAN13':
                                print(
                                    f"   ⚠️ No es EAN-13, pero se ha detectado un código.")

                # Mostrar información en pantalla
                info_text = f"Codigos detectados: {len(self.detected_codes)} | Modo: {mode_names[processing_mode]}"
                cv2.putText(original_frame, info_text, (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

                cv2.putText(original_frame, "q: salir | c: limpiar | s: cambiar modo",
                            (10, original_frame.shape[0] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

                # Mostrar frame (como tu código original)
                cv2.imshow('Barcode Scanner', original_frame)

                # Manejar teclas
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('c'):
                    self.detected_codes.clear()
                    self.last_barcode = None
                    self.last_detection_time = None
                    print("\n🧹 Historial limpiado")
                elif key == ord('s'):
                    processing_mode = (processing_mode + 1) % len(mode_names)
                    print(
                        f"\n🔄 Modo cambiado a: {mode_names[processing_mode]}")

        except KeyboardInterrupt:
            print("\n⚠️ Detenido por el usuario")

        finally:
            self.cleanup()

    def cleanup(self):
        """
        Limpia recursos y muestra resumen final
        """
        print(f"\n📊 RESUMEN FINAL:")
        print(f"   Total de códigos detectados: {len(self.detected_codes)}")

        if self.detected_codes:
            # Separar códigos válidos e inválidos
            valid_codes = [
                code for code in self.detected_codes if code.get('valido', False)]
            invalid_codes = [
                code for code in self.detected_codes if not code.get('valido', False)]

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

        self.cap.release()
        cv2.destroyAllWindows()
        print("\n👋 ¡Hasta luego!")


def main():
    """
    Función principal - Versión completa con todas las funcionalidades
    """
    print("Iniciando detector completo...")

    try:
        detector = BarcodeDetector()
        detector.run()

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
