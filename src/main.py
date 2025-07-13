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

import sys
import time
import threading

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QHBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QMessageBox,
)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QTimer

import psutil
import GPUtil


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
        self.setWindowIcon(QIcon("../assets/icon.png"))
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
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                return (gpu.load * 100, gpu.memoryUtil * 100)
            else:
                return (0, 0)
        except Exception:
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
# Clase para el icono de la bandeja del sistema
# -----------------------------------------------------------------------
class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon, monitor, parent=None):
        super().__init__()
        QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QMenu(parent)
        self.monitor = monitor

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
        about_box = QMessageBox()
        about_box.setWindowTitle("Acerca de System Monitor Widget")
        about_box.setWindowIcon(QIcon("../assets/icon.png"))
        about_box.setTextFormat(Qt.TextFormat.RichText)
        about_box.setText(
            "<b>System Monitor Widget</b><br>"
            "Autor: <a href='https://github.com/Xardax88'>Xardax</a><br>"
            "Muestra uso de <b>CPU</b>, <b>GPU</b>, <b>VRAM</b> y <b>RAM</b> en tiempo real.<br>"
            "Licencia: MIT<br>"
            "GitHub: <a href='https://github.com/Xardax88/SystemMonitor'>https://github.com/Xardax88/SystemMonitor</a>"
        )
        about_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        about_box.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        about_box.exec()

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

    icon = QIcon("../assets/icon.png")
    monitor = SystemMonitor()
    tray_icon = TrayIcon(icon, monitor)

    sys.exit(app.exec())
