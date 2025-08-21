
# 📦 Barcode Detector

Un sistema modular para la **detección y validación de códigos de barras en tiempo real** utilizando la cámara del dispositivo. Está optimizado para trabajar con formatos comunes en productos y medicamentos (EAN-13, UPC-A, CODE128), asegurando fiabilidad y facilidad de uso.

## 🚀 Características principales

* 🎥 **Captura en tiempo real** desde la cámara del sistema.
* 🔍 **Procesamiento de imágenes** con técnicas de mejora de contraste, binarización y operaciones morfológicas para aumentar la precisión.
* ✅ **Validación de códigos EAN-13** mediante cálculo del dígito de control.
* 📋 **Historial de detecciones** con marcas de tiempo.
* 🖥️ **Interfaz visual interactiva**, mostrando detecciones directamente en pantalla.
* ⚙️ **Configuración flexible** centralizada en un único archivo.
* 📂 **Arquitectura modular**, fácil de mantener y extender.
* 🧹 Funciones adicionales en ejecución:

  * `q`: salir del programa
  * `c`: limpiar historial de códigos
  * `s`: cambiar modo de procesamiento de imagen

---

## 📂 Estructura del proyecto

```bash
barcode_detector/
│
├── 📄 main.py                    # Punto de entrada con interfaz CLI
├── 📄 config.py                  # Configuración centralizada
├── 📄 requirements.txt           # Dependencias del proyecto
│
├── 📁 detector/
│   ├── __init__.py               # Inicializador del paquete
│   ├── barcode_detector.py       # Clase principal (detección y control)
│   ├── image_processor.py        # Técnicas de preprocesamiento de imágenes
│   └── validator.py              # Validación de códigos EAN-13/UPC-A
│
├── 📁 utils/
│   ├── __init__.py               # Inicializador del paquete
│   ├── camera_config.py          # Gestión y ajustes de cámara
│   └── display.py                # Visualización y mensajes al usuario
│
└── 📁 storage/
    ├── __init__.py               # Inicializador del paquete
    └── code_storage.py           # Almacenamiento y exportación de códigos
```

---

## ⚙️ Instalación

1. Clona este repositorio:

   ```bash
   git clone https://github.com/lruizap/src/1.-BarcodeDetector.git
   cd barcode_detector
   ```

2. Crea un entorno virtual (opcional pero recomendado):

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

---

## ▶️ Uso

Ejecuta el sistema desde el archivo principal:

```bash
python main.py
```

Una ventana se abrirá mostrando la cámara en tiempo real con la detección de códigos.

---

## 📊 Salida

El sistema mostrará:

* Los códigos detectados en pantalla con su tipo.
* El historial en consola con marcas de tiempo.
* Resumen final al salir, incluyendo códigos válidos e inválidos.

Además, se pueden exportar y reutilizar los códigos detectados desde el módulo de almacenamiento.

---

## 🛠️ Tecnologías utilizadas

* **OpenCV** → Procesamiento de imágenes y captura de cámara.
* **Pyzbar** → Detección de códigos de barras.
* **NumPy** → Operaciones matriciales y de filtrado.
* **Python estándar** → Manejo de fechas, estructuras y utilidades.

---

## 📌 Próximas mejoras

* Exportación de resultados en formatos como CSV/JSON.
* Integración con bases de datos para registrar inventarios.
* Soporte para QR y otros tipos de códigos.
* Interfaz gráfica independiente de la consola.
