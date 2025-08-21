# config.py
"""
Configuraciones centralizadas para el detector de códigos de barras
"""

# Configuración de Cámara
CAMERA_CONFIG = {
    'index': 0,
    'width': 1280,
    'height': 720,
    'fps': 30,
    'autofocus': True,
    'focus': 0
}

# Configuración de Detección
DETECTION_CONFIG = {
    'cooldown_seconds': 2.0,
    'supported_symbols': ['EAN13', 'UPCA', 'CODE128'],
    'scales': [1.0, 1.2, 0.8, 1.4],
    'processing_modes': [
        "Original",
        "Escala de grises",
        "Contraste mejorado",
        "Binarización",
        "Morfológico"
    ]
}

# Configuración de Procesamiento de Imagen
IMAGE_PROCESSING = {
    'clahe_clip_limit': 3.0,
    'clahe_tile_grid_size': (8, 8),
    'adaptive_threshold_max_value': 255,
    'adaptive_threshold_block_size': 11,
    'adaptive_threshold_c': 2,
    'morphology_kernel_size': (2, 2),
    'bilateral_filter_d': 9,
    'bilateral_filter_sigma_color': 75,
    'bilateral_filter_sigma_space': 75
}

# Configuración de Interfaz
UI_CONFIG = {
    'window_name': 'Barcode Scanner',
    'font': 'cv2.FONT_HERSHEY_SIMPLEX',
    'font_scale': 0.6,
    'font_color': (255, 255, 255),
    'font_thickness': 2,
    'rectangle_color': (0, 255, 0),
    'rectangle_thickness': 2,
    'type_color': (255, 0, 0)
}

# Configuración de Logging
LOGGING_CONFIG = {
    'enable_console_output': True,
    'enable_file_output': False,
    'log_file': 'barcode_detector.log',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

# Mensajes del Sistema
MESSAGES = {
    'startup': {
        'title': "🎥 Iniciando detector de códigos de barras...",
        'instructions': [
            "📋 Instrucciones:",
            "   - Presiona 'q' para salir",
            "   - Presiona 'c' para limpiar historial",
            "   - Presiona 's' para cambiar modo de procesamiento",
            "   - Mantén el código de barras estable frente a la cámara"
        ],
        'separator': "=" * 50
    },
    'detection': {
        'valid_code': "✅ CÓDIGO VÁLIDO DETECTADO:",
        'invalid_code': "❌ Código inválido detectado:",
        'general_code': "📦 CÓDIGO DETECTADO:",
        'not_ean13': "⚠️ No es EAN-13, pero se ha detectado un código."
    },
    'system': {
        'camera_error': "❌ Error: No se puede leer de la cámara",
        'user_interrupt': "⚠️ Detenido por el usuario",
        'history_cleared': "🧹 Historial limpiado",
        'mode_changed': "🔄 Modo cambiado a:",
        'goodbye': "👋 ¡Hasta luego!"
    }
}
