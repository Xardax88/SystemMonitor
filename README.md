# System Monitor Widget Py 🐍

![Último Commit](https://img.shields.io/github/last-commit/Xardax88/SystemMonitor)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/license/mit/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-8.0.0-blue.svg)](https://pypi.org/project/PyQt6/)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

Un widget flotante para Windows que muestra el uso de CPU, GPU, VRAM y RAM en tiempo real, siempre visible y con fondo translúcido/acrílico.

---

## Características

![Screenshot](docs/screenshot.png)

- Muestra estadísticas de CPU, GPU, VRAM y RAM.
- Siempre visible.
- Fondo translúcido/acrílico (Fluent Design, solo Windows 10/11).
- Se puede mover y bloquear en pantalla.
- Control desde el icono de la bandeja del sistema.

## Requisitos

- Python 3.8+
- Windows 10/11
- PyQt6
- psutil
- GPUtil
- pywin32

## Instalación

1. Clona este repositorio.
2. Instala las dependencias:

```bash
   pip install PyQt6 psutil GPUtil pywin32
```
   
## Uso

Ejecuta el script principal:
    
```bash
  python main.py
```

El widget aparecerá en la esquina inferior izquierda. Usa el icono de la bandeja para mostrar/ocultar, bloquear posición o salir.

## Notas

- El widget intenta estar siempre visible sobre la barra de tareas.
- El fondo translúcido/acrílico solo funciona en Windows 10/11.

---

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.
    