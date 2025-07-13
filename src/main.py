#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================================

System Monitor Widget
---------------------
Un widget flotante para Windows que muestra en tiempo real el uso de CPU, GPU, VRAM y RAM.
Incluye fondo acrílico/translúcido, siempre visible y control desde la bandeja del sistema.

Autor: Xardax * Paragoni Maximiliano
Requisitos:
    - Python 3.8+
    - PyQt6
    - psutil
    - GPUtil
    - pywin32

Licencia: MIT

============================================================================================
"""

import sys, os
import time
import threading

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QPushButton,
    QFrame,
)
from PyQt6.QtGui import QIcon, QFont, QGuiApplication, QColor
from PyQt6.QtCore import Qt, QTimer, QSize

import psutil
import gpustat


# -----------------------------------------------------------------------
# Función para obtener la ruta de los recursos empaquetados con PyInstaller
# -----------------------------------------------------------------------
def resource_path(relative_path):
    try:
        # Ruta creada por PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Guarda el icono de la bandeja del sistema
tray_icon = resource_path("assets/icon.png")


# -----------------------------------------------------------------------
# Clase para el monitor del sistema
# -----------------------------------------------------------------------
class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

        self.is_locked = False  # Controlar si está bloqueada
        self.dragging = False
        self.offset = None

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.ensure_on_top)
        self.check_timer.start(1000)

        # Inicia los hilos para actualizar las estadísticas
        self.cpu_thread = threading.Thread(
            target=self.update_cpu_stats_background, daemon=True
        )
        self.gpu_thread = threading.Thread(
            target=self.update_gpu_stats_background, daemon=True
        )
        self.cpu_thread.start()
        self.gpu_thread.start()

    # Funciones para manejar el arrastre de la ventana
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.is_locked:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging and not self.is_locked:
            self.move(self.mapToGlobal(event.pos() - self.offset))

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False

    def toggle_lock(self):
        self.is_locked = not self.is_locked
        return self.is_locked

    # Función para inicializar la interfaz de usuario
    def initUI(self):
        self.cpu_label = QLabel("CPU: 0%")
        self.gpu_label = QLabel("GPU: 0%")
        self.vram_label = QLabel("VRAM: 0%")
        self.ram_label = QLabel("RAM: 0%")

        label_style = "color: white; font-weight: bold; font-size: 12px;"
        for label in [self.cpu_label, self.gpu_label, self.vram_label, self.ram_label]:
            label.setStyleSheet(label_style)

        hbox = QHBoxLayout()
        hbox.addWidget(self.cpu_label)
        hbox.addWidget(self.gpu_label)
        hbox.addWidget(self.vram_label)
        hbox.addWidget(self.ram_label)
        hbox.setContentsMargins(10, 5, 10, 5)

        self.setLayout(hbox)
        self.setWindowFlags(
            Qt.WindowType.Popup
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.setStyleSheet(
            """
                QWidget {
                    background-color: rgba(0, 0, 0, 100);
                    padding: 8px;
                    padding-left: 10px;
                    padding-right: 10px;
                    border-radius: 10px;
                }
            """
        )

        self.setGeometry(15, 1037, 400, 30)
        self.setWindowTitle("System Monitor")
        self.setWindowIcon(QIcon(tray_icon))
        self.show()

    # Función para manejar el evento de mostrar la ventana
    def showEvent(self, event):
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    # Función para manejar el evento de ocultar la ventana
    def focusInEvent(self, event):
        # Manejar el evento de foco para asegurar que la ventana permanezca activa
        self.setWindowState(self.windowState() | Qt.WindowActive)
        super().focusInEvent(event)

    # Función para obtener las estadísticas de la GPU (ejecutada en el hilo)
    def get_gpu_stats(self):
        try:
            gpu_stats = gpustat.GPUStatCollection.new_query()
            if gpu_stats.gpus:
                gpu = gpu_stats.gpus[0]
                gpu_usage = gpu.utilization
                vram_used = gpu.memory_used
                vram_total = gpu.memory_total
                vram_usage = (vram_used / vram_total) * 100 if vram_total > 0 else 0
                return (gpu_usage, vram_usage)
            else:
                return (0, 0)
        except Exception as e:
            print(f"Error al obtener estadísticas de la GPU: {e}")
            return (0, 0)

    # Función para actualizar las estadísticas de la CPU (ejecutada en el hilo)
    def update_cpu_stats_background(self):
        while True:
            cpu_percent = psutil.cpu_percent()
            ram_percent = psutil.virtual_memory().percent

            # Llama a la función para actualizar las labels desde el hilo principal
            self.update_cpu_labels(cpu_percent, ram_percent)
            time.sleep(1)

    # Función para actualizar las estadísticas de la GPU (ejecutada en el hilo)
    def update_gpu_stats_background(self):
        while True:
            gpu_percent, vram_percent = self.get_gpu_stats()

            # Llama a la función para actualizar las labels desde el hilo principal
            self.update_gpu_labels(gpu_percent, vram_percent)
            time.sleep(1)

    # Función para actualizar las etiquetas de uso
    def update_cpu_labels(self, cpu_percent, ram_percent):
        self.cpu_label.setText("CPU: {0:.1f}%".format(cpu_percent))
        self.ram_label.setText("RAM: {0:.1f}%".format(ram_percent))

    def update_gpu_labels(self, gpu_percent, vram_percent):
        self.gpu_label.setText("GPU: {0:.1f}%".format(gpu_percent))
        self.vram_label.setText("VRAM: {0:.1f}%".format(vram_percent))

    # Función para manejar el evento de perder el foco
    def focusOutEvent(self, event):
        self.setWindowState(self.windowState() | Qt.WindowActive)
        super().focusOutEvent(event)
        self.raise_()

    # Función para asegurar que la ventana esté siempre en la parte superior
    def ensure_on_top(self):
        self.raise_()
        self.activateWindow()


# -----------------------------------------------------------------------
# Clase para la ventana "Acerca de"
# -----------------------------------------------------------------------


class AboutWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Acerca de")
        self.setWindowIcon(QIcon("assets/icon.png"))
        self.setFixedSize(350, 300)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet(
            """
                QFrame#Container {
                    background-color: #1e1e1e;
                    border-radius: 12px;
                    border: 1px solid rgba(100, 100, 100, 0.1);
                }
                QWidget {
                    background-color: #1e1e1e;
                    color: white;
                    font-family: 'Segoe UI', 'Arial';
                }
                QLabel {
                    margin-left: 40px;
                    margin-right: 30px;
                }
            """
        )
        self.initUI()

    def initUI(self):

        # Capa externa para sombra y borde redondeado
        container = QFrame(self)
        container.setObjectName("Container")
        container.setGeometry(0, 0, 350, 300)

        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(1, 20, 1, 1)

        # Info text
        info_layout = QVBoxLayout()

        terminal_label = QLabel("PyMonitor")
        terminal_label.setFont(QFont("Segoe UI", 16, weight=QFont.Weight.Bold))
        version_label = QLabel("Version: 0.9.Beta, build on Jul 13, 2024")
        source_label = QLabel(
            "GitHub: <a href='https://github.com/Xardax88/SystemMonitor'>Xardax88/SystemMonitor</a>"
        )
        source_label.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextBrowserInteraction
        )
        source_label.setOpenExternalLinks(True)
        documentation_label = QLabel("Documentación")
        release_notes_label = QLabel("Notas de la versión")
        privacy_label = QLabel("Política de privacidad")
        author_label = QLabel("by Xardax(Paragoni Maximiliano)")
        license_label = QLabel("Licence MIT 2025")

        info_layout.addWidget(terminal_label)
        info_layout.addSpacing(5)
        info_layout.addWidget(version_label)
        info_layout.addSpacing(15)
        info_layout.addWidget(source_label)
        info_layout.addSpacing(15)
        # info_layout.addWidget(documentation_label)
        # info_layout.addWidget(release_notes_label)
        # info_layout.addWidget(privacy_label)
        info_layout.addWidget(author_label)
        info_layout.addWidget(license_label)

        self.main_layout.addLayout(info_layout)
        self.main_layout.addStretch()

        # Barra inferior
        bottom_bar = QFrame()
        bottom_bar.setObjectName("BottomBar")
        bottom_bar.setFixedHeight(90)
        bottom_bar.setStyleSheet(
            """
                background-color: #141414;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            """
        )

        bottom_layout = QHBoxLayout(bottom_bar)
        bottom_layout.setContentsMargins(25, 20, 25, 10)
        bottom_layout.setSpacing(10)

        feedback_button = QPushButton("Enviar comentarios")
        feedback_button.setObjectName("FeedbackButton")
        feedback_button.setFixedSize(140, 40)
        feedback_button.setStyleSheet(
            """
            QPushButton#FeedbackButton {
                background-color: #101010;
                color: 303030;
                border-radius: 6px;
            }
        """
        )

        accept_button = QPushButton("Aceptar")
        accept_button.setObjectName("AcceptButton")
        accept_button.setFixedSize(140, 40)
        accept_button.setStyleSheet(
            """
            QPushButton#AcceptButton {
                background-color: #2d2d2d;
                color: white;
                border-radius: 6px;
            }
            QPushButton#AcceptButton:hover {
                background-color: #3a3a3a;
            }
        """
        )
        accept_button.clicked.connect(self.close)

        bottom_layout.addWidget(feedback_button)
        bottom_layout.addStretch()
        bottom_layout.addWidget(accept_button)

        self.main_layout.addWidget(bottom_bar)


# -----------------------------------------------------------------------
# Clase para el icono de la bandeja del sistema
# -----------------------------------------------------------------------
class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon, monitor, parent=None):
        super().__init__()
        QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QMenu(parent)
        self.monitor = monitor
        self.about_window = None

        toggle_window_action = self.menu.addAction("Mostrar/Ocultar")
        toggle_window_action.triggered.connect(self.toggle_window)

        self.lock_action = self.menu.addAction("Bloquear posición")
        self.lock_action.triggered.connect(self.toggle_lock)

        about_action = self.menu.addAction("Acerca de")
        about_action.triggered.connect(self.show_about)

        exit_action = self.menu.addAction("Salir")
        exit_action.triggered.connect(self.exit_app)

        self.setContextMenu(self.menu)
        self.activated.connect(self.on_tray_icon_activated)
        self.show()

    # Función para alternar la visibilidad de la ventana del monitor
    def toggle_window(self):
        if self.monitor.isVisible():
            self.monitor.hide()
        else:
            self.monitor.show()
            self.monitor.raise_()
            self.monitor.activateWindow()

    # Función para alternar el bloqueo de la posición del monitor
    def toggle_lock(self):
        is_locked = self.monitor.toggle_lock()
        self.lock_action.setText(
            "Desbloquear posición" if is_locked else "Bloquear posición"
        )

    # Función para manejar el evento de activación del icono de la bandeja
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.toggle_window()

    # Función para mostrar información sobre la aplicación
    def show_about(self):
        # if self.about_window is None:
        self.about_window = AboutWindow()
        self.about_window.show()
        self.about_window.activateWindow()

    # Función para salir de la aplicación
    def exit_app(self):
        self.monitor.hide()
        QApplication.quit()


# -----------------------------------------------------------------------
# Función principal
# -----------------------------------------------------------------------
if __name__ == "__main__":

    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Prevent closing when the window is closed

    icon = QIcon(tray_icon)
    monitor = SystemMonitor()
    tray_icon = TrayIcon(icon, monitor)

    sys.exit(app.exec())
