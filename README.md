# System Monitor Widget Py 🐍

[![Última Versión](https://img.shields.io/github/v/release/Xardax88/SystemMonitor?include_prereleases&label=version&color=blue)](https://github.com/Xardax88/SystemMonitor/releases)
![Último Commit](https://img.shields.io/github/last-commit/Xardax88/SystemMonitor)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/license/mit/)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.9.1-blue.svg)](https://pypi.org/project/PyQt6/)
[![Code Style: Black](https://img.shields.io/badge/Code%20Style-Black-000000.svg)](https://github.com/psf/black)

Un widget flotante para Windows programado en Python, que muestra el uso de CPU, GPU, VRAM y RAM en tiempo real, siempre visible y con fondo translúcido/acrílico.

> [!IMPORTANT]  
> Actualmente la aplicación solo funciona con placas de video NVIDIA, ya que utiliza la librería GPUtil para obtener información de la GPU.
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
- PyQt6
- psutil
- GPUtil

## Instalación

1.  **Clonar el repositorio (opcional):**

    Si desea modificar el código fuente, clone el repositorio de GitHub:

    ```bash
    git clone https://github.com/Xardax88/SystemMonitor.git
    cd SystemMonitor
    ```

2.  **Crear un entorno virtual (recomendado):**

    Es altamente recomendado crear un entorno virtual para aislar las dependencias del proyecto del resto de su sistema Python.

    *   Abra una terminal o símbolo del sistema.
    *   Navegue al directorio del proyecto (si clonó el repositorio).
    *   Cree un entorno virtual usando `venv`:

        ```bash
        python -m venv .venv
        ```

        *   En algunos sistemas, puede que necesite usar `python3` en lugar de `python`.


3.  **Activar el entorno virtual:**

    Debe activar el entorno virtual para que Python utilice las dependencias instaladas dentro de él.

    *   **Windows:**

        ```bash
        .venv\Scripts\activate
        ```


4.  **Instalar las dependencias:**

    Utilice `pip` para instalar las dependencias necesarias del archivo `requirements.txt`:

    ```bash
    pip install -r requirements.txt
    ```

5.  **Ejecutar el System Monitor Widget:**

    Una vez que las dependencias estén instaladas, puede ejecutar el script principal:

    ```bash
    python main.py
    ```
   
## Uso

Ejecuta el script principal:

*   **Windows:**
    ```bash
      .venv\Scripts\activate
      python main.py
    ```

El widget aparecerá en la esquina inferior izquierda. Usa el icono de la bandeja para mostrar/ocultar, bloquear posición o salir.

## Notas

- El widget intenta estar siempre visible sobre la barra de tareas.
- El fondo translúcido/acrílico solo funciona en Windows 10/11.
- **Limitaciones**: Actualmente solo funciona con tarjetas NVIDIA.

---

## Licencia
Este proyecto está licenciado bajo la Licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## Autor

Paragoni Maximiliano (Xardax88)
    