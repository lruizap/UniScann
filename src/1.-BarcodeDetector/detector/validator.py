# detector/validator.py
"""
Módulo para validación de códigos de barras
"""


class BarcodeValidator:
    """
    Clase para validar diferentes tipos de códigos de barras
    """

    @staticmethod
    def is_valid_ean13(code):
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

    @staticmethod
    def is_valid_upca(code):
        """
        Verifica si un código es un UPC-A válido

        Args:
            code (str): Código a validar

        Returns:
            bool: True si es válido, False en caso contrario
        """
        if len(code) != 12:
            return False

        if not code.isdigit():
            return False

        # Algoritmo de validación UPC-A
        odd_sum = sum(int(code[i]) for i in range(0, 11, 2))
        even_sum = sum(int(code[i]) for i in range(1, 11, 2))
        checksum = (10 - ((odd_sum * 3 + even_sum) % 10)) % 10

        return checksum == int(code[11])

    @staticmethod
    def validate_code(code, code_type):
        """
        Valida un código según su tipo

        Args:
            code (str): Código a validar
            code_type (str): Tipo de código ('EAN13', 'UPCA', etc.)

        Returns:
            bool: True si es válido, False en caso contrario
        """
        validators = {
            'EAN13': BarcodeValidator.is_valid_ean13,
            'UPCA': BarcodeValidator.is_valid_upca,
            'CODE128': lambda x: True,  # CODE128 no tiene validación estándar simple
        }

        validator = validators.get(code_type)
        if validator:
            return validator(code)

        # Si no hay validador específico, asumir válido
        return True

    @staticmethod
    def is_pharmaceutical_code(code, code_type):
        """
        Determina si un código es típicamente usado en productos farmacéuticos

        Args:
            code (str): Código de barras
            code_type (str): Tipo de código

        Returns:
            bool: True si es típico de farmacia
        """
        pharmaceutical_types = ['EAN13', 'UPCA', 'CODE128']

        if code_type not in pharmaceutical_types:
            return False

        # Los códigos EAN-13 de medicamentos en España suelen comenzar con ciertos prefijos
        if code_type == 'EAN13' and len(code) == 13:
            # Prefijos comunes para productos farmacéuticos
            pharma_prefixes = ['84', '76', '77', '80', '81', '82', '83']
            return any(code.startswith(prefix) for prefix in pharma_prefixes)

        return True  # Otros tipos los consideramos válidos por defecto
