# storage/code_storage.py
"""
Gestión y almacenamiento de códigos detectados
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from config import DETECTION_CONFIG, LOGGING_CONFIG


class CodeStorage:
    """
    Gestiona el almacenamiento y recuperación de códigos detectados
    """

    def __init__(self):
        self.detected_codes = []
        self.last_barcode = None
        self.last_detection_time = None
        self.cooldown_seconds = DETECTION_CONFIG['cooldown_seconds']

    def should_process_detection(self, barcode_data: str) -> bool:
        """
        Verifica si debe procesar una nueva detección (evita duplicados)

        Args:
            barcode_data: Código detectado

        Returns:
            True si debe procesar, False en caso contrario
        """
        current_time = datetime.now()

        if (self.last_barcode != barcode_data or
            self.last_detection_time is None or
                (current_time - self.last_detection_time).total_seconds() > self.cooldown_seconds):

            self.last_barcode = barcode_data
            self.last_detection_time = current_time
            return True

        return False

    def add_detected_code(self, code_data: str, code_type: str, is_valid: bool = True,
                          extra_info: Optional[Dict] = None) -> Dict:
        """
        Añade un código detectado al almacenamiento

        Args:
            code_data: Código detectado
            code_type: Tipo de código
            is_valid: Si el código es válido
            extra_info: Información adicional

        Returns:
            Información del código añadido
        """
        timestamp = datetime.now().strftime(LOGGING_CONFIG['date_format'])

        detection_info = {
            'codigo': code_data,
            'tipo': code_type,
            'timestamp': timestamp,
            'valido': is_valid,
            'es_farmaceutico': self._is_pharmaceutical_type(code_type)
        }

        # Añadir información extra si se proporciona
        if extra_info:
            detection_info.update(extra_info)

        self.detected_codes.append(detection_info)
        return detection_info

    def _is_pharmaceutical_type(self, code_type: str) -> bool:
        """
        Determina si el tipo de código es típico de productos farmacéuticos
        """
        pharmaceutical_types = ['EAN13', 'UPCA', 'CODE128']
        return code_type in pharmaceutical_types

    def get_detected_codes(self, filter_valid: Optional[bool] = None,
                           filter_pharmaceutical: Optional[bool] = None) -> List[Dict]:
        """
        Obtiene códigos detectados con filtros opcionales

        Args:
            filter_valid: Filtrar por códigos válidos (None = todos)
            filter_pharmaceutical: Filtrar por códigos farmacéuticos (None = todos)

        Returns:
            Lista de códigos filtrados
        """
        codes = self.detected_codes

        if filter_valid is not None:
            codes = [code for code in codes if code.get(
                'valido', False) == filter_valid]

        if filter_pharmaceutical is not None:
            codes = [code for code in codes if code.get(
                'es_farmaceutico', False) == filter_pharmaceutical]

        return codes

    def get_statistics(self) -> Dict:
        """
        Obtiene estadísticas de los códigos detectados

        Returns:
            Diccionario con estadísticas
        """
        total = len(self.detected_codes)
        valid = len(
            [code for code in self.detected_codes if code.get('valido', False)])
        pharmaceutical = len(
            [code for code in self.detected_codes if code.get('es_farmaceutico', False)])

        # Contar por tipos
        types_count = {}
        for code in self.detected_codes:
            code_type = code.get('tipo', 'Unknown')
            types_count[code_type] = types_count.get(code_type, 0) + 1

        return {
            'total': total,
            'valid': valid,
            'invalid': total - valid,
            'pharmaceutical': pharmaceutical,
            'non_pharmaceutical': total - pharmaceutical,
            'types_distribution': types_count,
            'detection_rate': valid / total if total > 0 else 0
        }

    def clear_history(self):
        """
        Limpia el historial de códigos detectados
        """
        self.detected_codes.clear()
        self.last_barcode = None
        self.last_detection_time = None

    def export_to_json(self, filename: str) -> bool:
        """
        Exporta los códigos detectados a un archivo JSON

        Args:
            filename: Nombre del archivo

        Returns:
            True si se exportó correctamente
        """
        try:
            export_data = {
                'export_timestamp': datetime.now().isoformat(),
                'statistics': self.get_statistics(),
                'detected_codes': self.detected_codes
            }

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

            return True
        except Exception as e:
            print(f"Error exportando a JSON: {e}")
            return False

    def import_from_json(self, filename: str) -> bool:
        """
        Importa códigos desde un archivo JSON

        Args:
            filename: Nombre del archivo

        Returns:
            True si se importó correctamente
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)

            if 'detected_codes' in data:
                self.detected_codes.extend(data['detected_codes'])
                return True

        except Exception as e:
            print(f"Error importando desde JSON: {e}")
            return False

    def export_to_csv(self, filename: str) -> bool:
        """
        Exporta los códigos detectados a un archivo CSV

        Args:
            filename: Nombre del archivo

        Returns:
            True si se exportó correctamente
        """
        try:
            import csv

            with open(filename, 'w', newline='', encoding='utf-8') as f:
                if not self.detected_codes:
                    return True

                fieldnames = self.detected_codes[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)

                writer.writeheader()
                for code in self.detected_codes:
                    writer.writerow(code)

            return True
        except Exception as e:
            print(f"Error exportando a CSV: {e}")
            return False

    def find_duplicates(self) -> List[Dict]:
        """
        Encuentra códigos duplicados en el historial

        Returns:
            Lista de códigos que aparecen más de una vez
        """
        code_counts = {}
        duplicates = []

        for code_info in self.detected_codes:
            code = code_info['codigo']
            if code in code_counts:
                code_counts[code].append(code_info)
            else:
                code_counts[code] = [code_info]

        for code, occurrences in code_counts.items():
            if len(occurrences) > 1:
                duplicates.append({
                    'codigo': code,
                    'count': len(occurrences),
                    'occurrences': occurrences
                })

        return duplicates

    def get_recent_codes(self, minutes: int = 30) -> List[Dict]:
        """
        Obtiene códigos detectados en los últimos X minutos

        Args:
            minutes: Minutos hacia atrás para buscar

        Returns:
            Lista de códigos recientes
        """
        from datetime import timedelta

        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_codes = []

        for code in self.detected_codes:
            try:
                code_time = datetime.strptime(
                    code['timestamp'], LOGGING_CONFIG['date_format'])
                if code_time >= cutoff_time:
                    recent_codes.append(code)
            except ValueError:
                continue

        return recent_codes
