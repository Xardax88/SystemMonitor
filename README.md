# System Monitor Widget Py

Un widget flotante para Windows que muestra el uso de CPU, GPU, VRAM y RAM en tiempo real, siempre visible y con fondo translúcido/acrílico.

## Características

- Muestra estadísticas de CPU, GPU, VRAM y RAM.
- Siempre visible sobre otras ventanas (intenta estar sobre la barra de tareas).
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

## Licencia
MIT License
    