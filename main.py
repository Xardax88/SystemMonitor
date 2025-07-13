#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================================

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

==============================================================================
"""

import sys
import psutil
import GPUtil
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

import win32con
import win32gui


# -----------------------------------------------------------------------
# Clase para el monitor del sistema
# -----------------------------------------------------------------------
class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_stats)
        self.timer.start(1000)  # Actualiza cada segundo
        self.is_locked = False  # Controlar si está bloqueada
        self.dragging = False
        self.offset = None

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.ensure_on_top)
        self.check_timer.start(500)  # Verifica cada 0.5 segundo

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

        self.setGeometry(10, 1035, 400, 30)
        self.setWindowTitle("System Monitor")
        self.setWindowIcon(QIcon("icon.png"))
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

    # Función para actualizar las estadísticas del sistema
    def update_stats(self):
        cpu_percent = psutil.cpu_percent()
        ram_percent = psutil.virtual_memory().percent

        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                gpu = gpus[0]
                gpu_percent = gpu.load * 100
                vram_percent = gpu.memoryUsed / gpu.memoryTotal * 100
            else:
                gpu_percent = 0
                vram_percent = 0
        except Exception as e:
            print(f"Error al obtener información de la GPU: {e}")
            gpu_percent = 0
            vram_percent = 0

        self.cpu_label.setText("CPU: {0:.1f}%".format(cpu_percent))
        self.gpu_label.setText("GPU: {0:.1f}%".format(gpu_percent))
        self.vram_label.setText("VRAM: {0:.1f}%".format(vram_percent))
        self.ram_label.setText("RAM: {0:.1f}%".format(ram_percent))

    # Función para manejar el evento de perder el foco
    def focusOutEvent(self, event):
        self.setWindowState(self.windowState() | Qt.WindowActive)
        super().focusOutEvent(event)
        self.raise_()

    # Función para asegurar que la ventana esté siempre en la parte superior
    def ensure_on_top(self):
        hwnd = int(self.winId())
        fg_hwnd = win32gui.GetForegroundWindow()
        if hwnd != fg_hwnd:
            self.raise_()
            self.activateWindow()


# -----------------------------------------------------------------------
# Clase para el icono de la bandeja del sistema
# -----------------------------------------------------------------------
class TrayIcon(QSystemTrayIcon):
    def __init__(self, icon, parent=None):
        super().__init__()
        QSystemTrayIcon.__init__(self, icon, parent)
        self.menu = QMenu(parent)
        self.monitor = SystemMonitor()

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
        about_box.setWindowIcon(QIcon("icon.png"))
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

    icon = QIcon("icon.png")
    tray_icon = TrayIcon(icon)

    sys.exit(app.exec())
