# main.py
"""
Punto de entrada principal para el detector de códigos de barras
"""

import sys
import argparse
from detector.barcodeDetector import BarcodeDetector


def parse_arguments():
    """
    Parsea argumentos de línea de comandos
    """
    parser = argparse.ArgumentParser(
        description='Detector de Códigos de Barras para Medicamentos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                    # Usar cámara por defecto
  python main.py --camera 1         # Usar cámara específica
  python main.py --test-camera      # Probar capacidades de cámara
  python main.py --export codes.json # Exportar después de detección
        """
    )

    parser.add_argument(
        '--camera', '-c',
        type=int,
        default=None,
        help='Índice de la cámara a usar (default: desde config)'
    )

    parser.add_argument(
        '--test-camera', '-t',
        action='store_true',
        help='Probar capacidades de la cámara y salir'
    )

    parser.add_argument(
        '--export', '-e',
        type=str,
        help='Archivo donde exportar códigos detectados al finalizar'
    )

    parser.add_argument(
        '--format', '-f',
        choices=['json', 'csv'],
        default='json',
        help='Formato de exportación (default: json)'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Modo verbose con información adicional'
    )

    return parser.parse_args()


def test_camera_capabilities(camera_index=None):
    """
    Prueba las capacidades de la cámara
    """
    print("🔍 Probando capacidades de cámara...")

    try:
        from utils.cameraConfig import CameraManager

        camera_manager = CameraManager(camera_index)
        cap = camera_manager.initialize_camera()

        # Información básica
        info = camera_manager.get_camera_info()
        print("\n📷 INFORMACIÓN DE CÁMARA:")
        for key, value in info.items():
            print(f"   {key}: {value}")

        # Probar capacidades
        capabilities = camera_manager.test_camera_capabilities()
        print("\n🎛️  CAPACIDADES:")
        for feature, details in capabilities.items():
            status = "✅" if details['supported'] else "❌"
            writable = "📝" if details.get('writable', False) else "🔒"
            print(f"   {status} {writable} {feature}: {details}")

        camera_manager.release()
        print("\n✅ Prueba de cámara completada")

    except Exception as e:
        print(f"❌ Error probando cámara: {e}")


def main():
    """
    Función principal
    """
    args = parse_arguments()

    # Si solo quiere probar la cámara
    if args.test_camera:
        test_camera_capabilities(args.camera)
        return

    print("🚀 Iniciando Detector de Códigos de Barras")
    print("=" * 50)

    if args.verbose:
        print(f"📊 Configuración:")
        print(f"   Cámara: {args.camera or 'por defecto'}")
        if args.export:
            print(f"   Exportar a: {args.export} ({args.format})")

    try:
        # Crear e inicializar detector
        detector = BarcodeDetector(camera_index=args.camera)

        # Ejecutar detector
        detector.run()

        # Exportar si se solicitó
        if args.export:
            print(f"\n💾 Exportando códigos a {args.export}...")
            if detector.export_codes(args.export, args.format):
                print(f"✅ Códigos exportados exitosamente")
            else:
                print(f"❌ Error exportando códigos")

    except KeyboardInterrupt:
        print("\n⚠️ Interrupción del usuario")

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()

    finally:
        print("\n🏁 Detector finalizado")


if __name__ == "__main__":
    main()
