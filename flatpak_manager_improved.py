#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flatpak Manager - Gestor profesional de aplicaciones Flatpak
"""

import sys
import subprocess
import platform
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QVBoxLayout, 
                           QWidget, QTextEdit, QLabel, QMessageBox, QHBoxLayout,
                           QTabWidget, QProgressBar, QFileDialog, QSystemTrayIcon,
                           QMenu, QStyle, QStatusBar, QSizePolicy, QGroupBox,
                           QFormLayout, QCheckBox, QComboBox, QInputDialog)
from PyQt6.QtCore import QSettings
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QIcon, QAction, QFont, QTextCursor, QGuiApplication

# Constantes
APP_NAME = "Flatpak Manager"
VERSION = "2.0.0"
AUTHOR = "Soporte Técnico"
YEAR = datetime.now().year

class CommandThread(QThread):
    """Hilo para ejecutar comandos en segundo plano"""
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, command):
        super().__init__()
        self.command = command
        self._is_running = True
    
    def run(self):
        try:
            self._is_running = True
            process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            while self._is_running and process.poll() is None:
                line = process.stdout.readline()
                if line:
                    self.output_signal.emit(line.strip())
            
            # Leer cualquier salida restante
            if not self._is_running:
                process.terminate()
                process.wait()
                return
                
            # Leer la salida restante
            for line in process.stdout:
                if line.strip():
                    self.output_signal.emit(line.strip())
            
            process.wait()
            self.finished_signal.emit(process.returncode == 0, "")
            
        except Exception as e:
            self.finished_signal.emit(False, str(e))
        finally:
            self._is_running = False
    
    def stop(self):
        """Detiene la ejecución del comando"""
        self._is_running = False
        self.quit()
        self.wait(2000)  # Esperar hasta 2 segundos a que termine

class AboutDialog(QMessageBox):
    """Diálogo Acerca de"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Acerca de {APP_NAME}")
        self.setIcon(QMessageBox.Icon.Information)
        
class AboutDialog(QMessageBox):
    """Diálogo Acerca de"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Acerca de {APP_NAME}")
        self.setIcon(QMessageBox.Icon.Information)

        about_text = (
            f"<h2>{APP_NAME} v{VERSION}</h2>"
            "<p>Un gestor profesional de aplicaciones Flatpak</p>"
            "<p>Creado por VicCodeV y VicCodeM</p>"
            "<p>Licencia: GPL v3</p>"
            "<p>Desarrollado con PyQt6</p>"
        )

        self.setText(about_text)
        self.setStandardButtons(QMessageBox.StandardButton.Ok)
        self.setTextFormat(Qt.TextFormat.RichText)  # Permite formato HTML
        
        # Ajustar tamaño mínimo
        self.setMinimumSize(400, 300)

class FlatpakManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} v{VERSION}")
        self.setMinimumSize(900, 700)
        self.setWindowIcon(self.style().standardIcon(
            getattr(QStyle.StandardPixmap, 'SP_ComputerIcon')))
        
        # Variables
        self.command_thread = None
        self.settings = QSettings("FlatpakManager", "Config")
        
        self.setup_ui()
        self.setup_menu()
        self.setup_tray_icon()
        
        # Mostrar información del sistema
        self.show_system_info()
        
        # Cargar configuración
        self.load_config()
        
    def create_button(self, text, callback, icon=None, tooltip=None):
        """Crea un botón con el texto, icono y tooltip especificados"""
        button = QPushButton(text)
        if icon:
            button.setIcon(icon)
        if tooltip:
            button.setToolTip(tooltip)
        button.clicked.connect(callback)
        return button
        
    def setup_ui(self):
        """Configura la interfaz de usuario"""
        # Widget principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Pestañas
        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)
        
        # Pestaña principal (Acciones)
        self.main_tab = QWidget()
        self.setup_main_tab()
        self.tabs.addTab(self.main_tab, "Acciones")
        
        # Pestaña de configuración
        self.config_tab = QWidget()
        self.setup_config_tab()
        self.tabs.addTab(self.config_tab, "Configuración")
        
        # Barra de estado mejorada
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        
        # Crear un contenedor para la barra de progreso y el mensaje
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(10)
        
        # Etiqueta para el estado actual
        self.status_label = QLabel("Listo")
        self.status_label.setMinimumWidth(200)
        
        # Barra de progreso mejorada
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumHeight(4)  # Hacerla más delgada
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(4)  # Altura fija muy pequeña
        
        # Agregar widgets al layout
        progress_layout.addWidget(self.status_label, 1)
        progress_layout.addWidget(self.progress_bar, 10)  # La barra ocupa más espacio
        
        # Agregar el contenedor a la barra de estado
        self.statusBar.addPermanentWidget(progress_container, 1)
        self.statusBar.setSizeGripEnabled(False)  # Deshabilitar el grip de redimensionamiento
        self.statusBar.showMessage("Listo")
    
    def setup_main_tab(self):
        """Configura la pestaña principal con todas las acciones"""
        main_layout = QVBoxLayout()
        
        # Sección de información del sistema
        self.system_info = QTextEdit()
        self.system_info.setReadOnly(True)
        self.system_info.setFont(QFont("Monospace", 10))
        self.system_info.setMaximumHeight(150)
        main_layout.addWidget(QLabel("<h3>Información del sistema</h3>"))
        main_layout.addWidget(self.system_info)
        
        # Sección de acciones
        actions_group = QGroupBox("Acciones")
        actions_layout = QVBoxLayout()
        
        # Estilo para los botones
        btn_style = """
            QPushButton {
                padding: 10px 15px;
                font-weight: normal;
                font-size: 13px;
                border: 1px solid palette(mid);
                border-radius: 4px;
                margin: 6px 0;
                text-align: left;
                min-height: 40px;
                background: palette(button);
                color: palette(button-text);
                text-align: left;
                padding-left: 15px;
            }
            QPushButton:hover {
                background: palette(midlight);
                border: 1px solid palette(highlight);
            }
            QPushButton:pressed {
                background: palette(dark);
                color: palette(light);
            }
            QPushButton:disabled {
                color: palette(mid);
                background: palette(window);
                border: 1px solid palette(mid);
            }
        """
        
        # Botones de acción
        self.btn_list = self.create_button(" Listar Aplicaciones", 
                                         callback=self.list_flatpaks, 
                                         tooltip="Lista todas las aplicaciones Flatpak instaladas")
        
        self.btn_updates = self.create_button(" Buscar Actualizaciones", 
                                            callback=self.check_updates, 
                                            tooltip="Busca actualizaciones disponibles para aplicaciones Flatpak")
        
        self.btn_install = self.create_button(" Instalar Aplicación", 
                                           callback=self.install_flatpak, 
                                           tooltip="Instalar una nueva aplicación Flatpak")
        
        self.btn_uninstall = self.create_button(" Desinstalar Aplicación", 
                                             callback=self.uninstall_flatpak, 
                                             tooltip="Desinstalar una aplicación Flatpak")
        
        self.btn_export = self.create_button(" Exportar Lista", 
                                           callback=self.export_list, 
                                           tooltip="Guarda una lista de todas las aplicaciones instaladas")
        
        self.btn_clean_cache = self.create_button(" Limpiar Caché", 
                                               callback=self.clean_cache, 
                                               tooltip="Elimina paquetes no utilizados de la caché de Flatpak")
        
        # Agregar botones al layout de acciones
        actions_layout.addWidget(self.btn_list)
        actions_layout.addWidget(self.btn_updates)
        actions_layout.addWidget(self.btn_install)
        actions_layout.addWidget(self.btn_uninstall)
        actions_layout.addWidget(self.btn_export)
        actions_layout.addWidget(self.btn_clean_cache)
        actions_layout.addStretch()
        
        actions_group.setLayout(actions_layout)
        
        # Área de salida
        output_group = QGroupBox("Salida de comandos")
        output_layout = QVBoxLayout()
        
        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Monospace", 9))
        
        output_layout.addWidget(self.output_area)
        output_group.setLayout(output_layout)
        
        # Configurar el layout principal
        main_layout.addWidget(actions_group)
        main_layout.addWidget(output_group, 1)  # El 1 hace que el grupo de salida ocupe el espacio restante
        
        self.main_tab.setLayout(main_layout)
    
    def setup_config_tab(self):
        """Configura la pestaña de configuración"""
        self.config_tab = QWidget()
        layout = QVBoxLayout(self.config_tab)
        
        # Grupo de configuración general
        general_group = QGroupBox("Configuración General")
        general_layout = QFormLayout()
        
        # Tema
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Sistema", "Claro", "Oscuro"])
        general_layout.addRow("Tema:", self.theme_combo)
        
        # Actualizaciones automáticas
        self.auto_update_check = QCheckBox("Buscar actualizaciones al iniciar")
        general_layout.addRow(self.auto_update_check)
        
        # Tamaño de fuente
        self.font_size = QComboBox()
        self.font_size.addItems(["Pequeño", "Mediano", "Grande", "Muy grande"])
        general_layout.addRow("Tamaño de fuente:", self.font_size)
        
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)
        
        # Grupo de notificaciones
        notif_group = QGroupBox("Notificaciones")
        notif_layout = QVBoxLayout()
        
        self.notif_updates = QCheckBox("Notificar actualizaciones disponibles")
        self.notif_errors = QCheckBox("Notificar errores")
        self.notif_complete = QCheckBox("Notificar cuando las operaciones completen")
        self.notif_sound = QCheckBox("Reproducir sonido en notificaciones")
        
        notif_layout.addWidget(self.notif_updates)
        notif_layout.addWidget(self.notif_errors)
        notif_layout.addWidget(self.notif_complete)
        notif_layout.addWidget(self.notif_sound)
        notif_group.setLayout(notif_layout)
        layout.addWidget(notif_group)
        
        # Grupo de limpieza automática
        clean_group = QGroupBox("Limpieza Automática")
        clean_layout = QVBoxLayout()
        
        self.auto_clean_check = QCheckBox("Limpiar caché automáticamente")
        self.auto_clean_days = QComboBox()
        self.auto_clean_days.addItems(["Diariamente", "Semanalmente", "Mensualmente"])
        
        clean_layout.addWidget(self.auto_clean_check)
        clean_layout.addWidget(QLabel("Frecuencia:"))
        clean_layout.addWidget(self.auto_clean_days)
        clean_group.setLayout(clean_layout)
        
        # Grupo de rendimiento
        perf_group = QGroupBox("Rendimiento")
        perf_layout = QVBoxLayout()
        
        self.parallel_downloads = QCheckBox("Descargas en paralelo")
        self.max_downloads = QComboBox()
        self.max_downloads.addItems(["2", "4", "6", "8", "10"])
        self.max_downloads.setCurrentText("4")
        
        perf_layout.addWidget(self.parallel_downloads)
        perf_layout.addWidget(QLabel("Máximo de descargas simultáneas:"))
        perf_layout.addWidget(self.max_downloads)
        perf_group.setLayout(perf_layout)
        
        # Grupo de repositorios
        repo_group = QGroupBox("Repositorios")
        repo_layout = QVBoxLayout()
        
        self.repo_list = QTextEdit()
        self.repo_list.setReadOnly(True)
        self.repo_list.setMaximumHeight(100)
        
        # Botones de repositorios
        repo_btn_layout = QHBoxLayout()
        self.refresh_repos_btn = QPushButton("Actualizar")
        self.add_repo_btn = QPushButton("Añadir")
        self.remove_repo_btn = QPushButton("Eliminar")
        repo_btn_layout.addWidget(self.refresh_repos_btn)
        repo_btn_layout.addWidget(self.add_repo_btn)
        repo_btn_layout.addWidget(self.remove_repo_btn)
        
        repo_layout.addWidget(QLabel("Repositorios configurados:"))
        repo_layout.addWidget(self.repo_list)
        repo_layout.addLayout(repo_btn_layout)
        
        # Actualizar lista de repositorios
        self.update_repo_list()
        repo_group.setLayout(repo_layout)
        
        # Agregar grupos al layout principal
        layout.addWidget(clean_group)
        layout.addWidget(perf_group)
        layout.addWidget(repo_group)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        
        self.save_config_btn = QPushButton("Guardar Configuración")
        self.reset_config_btn = QPushButton("Restablecer Valores")
        
        btn_layout.addWidget(self.save_config_btn)
        btn_layout.addWidget(self.reset_config_btn)
        
        layout.addLayout(btn_layout)
        
        # Cargar configuración guardada
        self.load_config()
        
        # Conectar señales
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        self.font_size.currentTextChanged.connect(self.update_font_size)
        self.parallel_downloads.stateChanged.connect(self.toggle_parallel_downloads)
        self.save_config_btn.clicked.connect(self.save_config)
        self.reset_config_btn.clicked.connect(self.reset_settings)
        
        # Conectar botones de repositorios
        self.refresh_repos_btn.clicked.connect(self.update_repo_list)
        self.add_repo_btn.clicked.connect(self.add_repository)
        self.remove_repo_btn.clicked.connect(self.remove_repository)
        
        # Actualizar estado inicial
        self.toggle_parallel_downloads(self.parallel_downloads.checkState())
        self.update_repo_list()
        
        # Agregar pestaña de configuración
        self.tabs.addTab(self.config_tab, "Configuración")
    
    def setup_menu(self):
        """Configura el menú principal"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        # Acciones del menú Archivo
        export_action = QAction("&Exportar lista...", self)
        export_action.triggered.connect(self.export_list)
        file_menu.addAction(export_action)
        
        # Agregar separador
        file_menu.addSeparator()
        
        # Acción Salir
        exit_action = QAction("&Salir", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Menú Configuración
        config_menu = menubar.addMenu("&Configuración")
        
        # Acciones del menú Configuración
        settings_action = QAction("&Preferencias...", self)
        settings_action.triggered.connect(lambda: self.tabs.setCurrentWidget(self.config_tab))
        config_menu.addAction(settings_action)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("&Herramientas")
        
        list_action = QAction("&Listar Flatpaks", self)
        list_action.triggered.connect(self.list_flatpaks)
        tools_menu.addAction(list_action)
        
        update_action = QAction("Buscar &Actualizaciones", self)
        update_action.triggered.connect(self.check_updates)
        tools_menu.addAction(update_action)
        
        clean_action = QAction("&Limpiar Caché", self)
        clean_action.triggered.connect(self.clean_cache)
        tools_menu.addAction(clean_action)
        
        repair_action = QAction("&Reparar Flatpaks", self)
        repair_action.triggered.connect(self.repair_flatpaks)
        tools_menu.addAction(repair_action)
        
        # Menú Ayuda (al final)
        help_menu = menubar.addMenu("A&yuda")
        
        # Acción de documentación
        docs_action = QAction("&Documentación", self)
        docs_action.triggered.connect(self.show_documentation)
        help_menu.addAction(docs_action)
        
        # Agregar separador
        help_menu.addSeparator()
        
        # Acción Acerca de
        about_action = QAction("&Acerca de...", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_tray_icon(self):
        """Configura el ícono en la bandeja del sistema"""
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(
            getattr(QStyle.StandardPixmap, 'SP_ComputerIcon')))
        
        tray_menu = QMenu()
        
        show_action = QAction("Mostrar", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        exit_action = QAction("Salir", self)
        exit_action.triggered.connect(self.close)
        tray_menu.addAction(exit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()
        
        # Mostrar notificación al iniciar
        # Verificar si el sistema soporta notificaciones del sistema
        if self.tray_icon.isSystemTrayAvailable():
            # En PyQt6, el parámetro del ícono es opcional y se puede omitir
            # para usar el ícono por defecto del sistema
            try:
                self.tray_icon.showMessage(
                    f"{APP_NAME} v{VERSION}",
                    "El administrador de Flatpaks se está ejecutando en segundo plano",
                    msecs=3000
                )
            except Exception as e:
                print(f"No se pudo mostrar la notificación: {e}")
        else:
            print("El sistema no soporta notificaciones en la bandeja")
    
    def show_system_info(self):
        """Muestra información del sistema"""
        info = []
        info.append(f"Sistema: {platform.system()} {platform.release()}")
        info.append(f"Versión: {platform.version()}")
        info.append(f"Máquina: {platform.machine()}")
        info.append(f"Procesador: {platform.processor()}")
        info.append("")
        
        # Obtener información de Flatpak
        try:
            flatpak_version = subprocess.check_output(
                ["flatpak", "--version"], 
                stderr=subprocess.STDOUT,
                text=True
            ).strip()
            info.append(f"Versión de Flatpak: {flatpak_version}")
            
            # Contar aplicaciones instaladas
            flatpak_list = subprocess.check_output(
                ["flatpak", "list", "--app"],
                stderr=subprocess.STDOUT,
                text=True
            )
            app_count = len(flatpak_list.splitlines()) - 1  # Restar el encabezado
            info.append(f"Aplicaciones instaladas: {app_count}")
            
        except subprocess.CalledProcessError as e:
            info.append("Error al obtener información de Flatpak")
        
        self.system_info.setPlainText("\n".join(info))
    
    def run_command(self, command, show_output=True, status_message=""):
        """
        Ejecuta un comando en segundo plano
        
        Args:
            command (str): Comando a ejecutar
            show_output (bool): Si se debe mostrar la salida del comando
            status_message (str): Mensaje a mostrar en la barra de estado
        """
        # Configurar el estado inicial
        self.set_buttons_enabled(False)
        if hasattr(self, 'status_label') and status_message:
            self.status_label.setText(status_message)
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setRange(0, 0)  # Modo indeterminado
        
        # Mostrar el comando en la salida si es necesario
        if show_output and hasattr(self, 'append_output'):
            self.append_output(f"$ {command}")
        
        # Verificar si hay un hilo en ejecución
        if hasattr(self, 'command_thread') and self.command_thread and self.command_thread.isRunning():
            self.command_thread.stop()
        
        # Configurar y ejecutar el hilo
        self.command_thread = CommandThread(command)
        if show_output and hasattr(self, 'append_output'):
            self.command_thread.output_signal.connect(self.append_output)
        self.command_thread.finished_signal.connect(self.command_finished)
        self.command_thread.start()
    
    def command_finished(self, success, message):
        """Se ejecuta cuando termina un comando"""
        self.set_buttons_enabled(True)
        
        # Actualizar la barra de progreso
        self.progress_bar.setRange(0, 1)
        self.progress_bar.setValue(1)
        
        # Mostrar mensaje de estado
        if success:
            self.status_label.setText("Listo")
            self.statusBar.showMessage("Comando completado exitosamente", 3000)
        else:
            self.status_label.setText("Error")
            self.statusBar.showMessage("Error al ejecutar el comando", 5000)
    
    def set_buttons_enabled(self, enabled):
        """Habilita o deshabilita los botones"""
        # Solo intentar habilitar/deshabilitar los botones que existen
        buttons = ['btn_list', 'btn_updates', 'btn_install', 
                  'btn_uninstall', 'btn_export']
        
        for btn_name in buttons:
            if hasattr(self, btn_name):
                btn = getattr(self, btn_name)
                if btn is not None:  # Asegurarse de que el botón existe
                    btn.setEnabled(enabled)
    
    def append_output(self, text):
        """Agrega texto al área de salida"""
        self.output_area.moveCursor(QTextCursor.MoveOperation.End)
        self.output_area.insertPlainText(text + "\n")
        self.output_area.moveCursor(QTextCursor.MoveOperation.End)
    
    def list_flatpaks(self):
        """Lista las aplicaciones Flatpak instaladas"""
        self.output_area.clear()
        self.append_output("Obteniendo lista de aplicaciones instaladas...\n" + "="*50 + "\n")
        
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app", "--columns=application,version,branch,origin"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                self.append_output("Aplicaciones Flatpak instaladas:")
                self.append_output("=" * 50)
                self.append_output(result.stdout)
                self.statusBar.showMessage("Lista de aplicaciones generada", 3000)
            else:
                self.append_output("Error al listar aplicaciones:")
                self.append_output(result.stderr)
                self.statusBar.showMessage("Error al listar aplicaciones", 5000)
        except Exception as e:
            self.append_output(f"Error inesperado: {str(e)}")
            self.statusBar.showMessage("Error inesperado", 5000)
    
    def check_updates(self):
        """Busca actualizaciones disponibles"""
        self.output_area.clear()
        self.append_output("Buscando actualizaciones disponibles...\n" + "="*50 + "\n")
        
        try:
            # Primero actualizamos la información de los repositorios
            update_result = subprocess.run(
                ["flatpak", "update", "--appstream"],
                capture_output=True,
                text=True
            )
            
            if update_result.returncode != 0:
                self.append_output("Advertencia: No se pudo actualizar la información de los repositorios")
                self.append_output(update_result.stderr)
            
            # Luego buscamos actualizaciones disponibles
            result = subprocess.run(
                ["flatpak", "remote-ls", "--updates", "--columns=application,version,branch,origin"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0 and result.stdout.strip():
                self.append_output("Actualizaciones disponibles:")
                self.append_output("=" * 50)
                self.append_output("Aplicación                Versión Actual    Rama      Origen")
                self.append_output("-" * 50)
                self.append_output(result.stdout)
                self.statusBar.showMessage("Búsqueda de actualizaciones completada", 3000)
            else:
                self.append_output("No hay actualizaciones disponibles.")
                self.statusBar.showMessage("No hay actualizaciones disponibles", 3000)
                
        except Exception as e:
            self.append_output(f"Error al buscar actualizaciones: {str(e)}")
            self.statusBar.showMessage("Error al buscar actualizaciones", 5000)
    
    def install_flatpak(self):
        """Instala una nueva aplicación Flatpak"""
        app_id, ok = QInputDialog.getText(self, "Instalar aplicación", 
                                       "Ingresa el ID de la aplicación (ej: org.gimp.GIMP):")
        if ok and app_id:
            self.output_area.clear()
            self.append_output(f"Instalando {app_id}...\n" + "="*50 + "\n")
            
            try:
                result = subprocess.run(
                    ["flatpak", "install", "-y", app_id],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    self.append_output(f"\n{app_id} instalado exitosamente!")
                    self.statusBar.showMessage(f"{app_id} instalado exitosamente", 3000)
                else:
                    self.append_output(f"Error al instalar {app_id}:")
                    self.append_output(result.stderr)
                    self.statusBar.showMessage(f"Error al instalar {app_id}", 5000)
            except Exception as e:
                self.append_output(f"Error inesperado: {str(e)}")
                self.statusBar.showMessage("Error inesperado", 5000)
    
    def uninstall_flatpak(self):
        """Desinstala una aplicación Flatpak"""
        try:
            # Obtener lista de aplicaciones instaladas
            result = subprocess.run(
                ["flatpak", "list", "--app", "--columns=application"],
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                self.append_output("Error al obtener la lista de aplicaciones:")
                self.append_output(result.stderr)
                return
                
            apps = [app.strip() for app in result.stdout.split('\n') if app.strip()]
            
            if not apps:
                QMessageBox.information(self, "Información", "No hay aplicaciones instaladas.")
                return
                
            # Mostrar diálogo para seleccionar aplicación
            app, ok = QInputDialog.getItem(
                self, 
                "Desinstalar aplicación", 
                "Selecciona la aplicación a desinstalar:",
                apps, 
                0, 
                False
            )
            
            if ok and app:
                self.output_area.clear()
                self.append_output(f"Desinstalando {app}...\n" + "="*50 + "\n")
                
                result = subprocess.run(
                    ["flatpak", "uninstall", "-y", app],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.append_output(f"\n{app} desinstalado exitosamente!")
                    self.statusBar.showMessage(f"{app} desinstalado exitosamente", 3000)
                else:
                    self.append_output(f"Error al desinstalar {app}:")
                    self.append_output(result.stderr)
                    self.statusBar.showMessage(f"Error al desinstalar {app}", 5000)
                    
        except Exception as e:
            self.append_output(f"Error inesperado: {str(e)}")
            self.statusBar.showMessage("Error inesperado", 5000)
    
    def export_list(self):
        """Exporta la lista de aplicaciones instaladas a un archivo"""
        try:
            # Obtener lista de aplicaciones instaladas
            result = subprocess.check_output(["flatpak", "list", "--app", "--columns=application,version"], 
                                           text=True)
            
            # Mostrar diálogo para guardar archivo
            file_path, _ = QFileDialog.getSaveFileName(self, "Guardar lista de aplicaciones", 
                                                    "flatpak_apps.txt", "Archivos de texto (*.txt)")
            
            if file_path:
                with open(file_path, 'w') as f:
                    f.write("Aplicaciones Flatpak instaladas:\n")
                    f.write("=" * 30 + "\n\n")
                    f.write(result)
                
                QMessageBox.information(self, "Éxito", 
                                      f"Lista de aplicaciones guardada en:\n{file_path}")
                
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"Error al obtener la lista de aplicaciones: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar el archivo: {e}")
    
    def clean_cache(self):
        """Limpia la caché de Flatpak"""
        reply = QMessageBox.question(
            self, 
            "Limpiar caché",
            "¿Estás seguro de que deseas limpiar la caché de Flatpak?\n\n"
            "Esto liberará espacio eliminando datos en caché no utilizados.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.output_area.clear()
            self.run_command(
                ["flatpak", "uninstall", "--unused", "-y"],
                status_message="Limpiando caché de Flatpak..."
            )
    
    def repair_flatpaks(self):
        """Intenta reparar instalaciones de Flatpak dañadas"""
        reply = QMessageBox.question(
            self, 
            "Reparar Flatpaks",
            "¿Estás seguro de que deseas intentar reparar las instalaciones de Flatpak?\n\n"
            "Esto puede tomar algún tiempo dependiendo del número de aplicaciones instaladas.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.output_area.clear()
            self.run_command(
                ["flatpak", "repair"],
                status_message="Reparando instalaciones de Flatpak..."
            )
    
    def cleanup(self):
        """Limpia los recursos antes de salir"""
        if hasattr(self, 'command_thread') and self.command_thread:
            if self.command_thread.isRunning():
                self.command_thread.stop()
                self.command_thread.wait(2000)  # Esperar hasta 2 segundos
            self.command_thread = None
            
    def clean_cache(self):
        """Limpia la caché de Flatpak"""
        try:
            self.output_area.clear()
            self.append_output("Limpiando caché de Flatpak...\n" + "="*50 + "\n")
            
            # Ejecutar limpieza de caché
            result = subprocess.run(
                ["flatpak", "uninstall", "--unused", "-y"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.append_output("\n¡Caché limpiada exitosamente!")
                self.append_output("\nPaquetes eliminados:")
                self.append_output("=" * 50)
                self.append_output(result.stdout)
                self.statusBar.showMessage("Caché limpiada exitosamente", 3000)
            else:
                self.append_output("Error al limpiar la caché:")
                self.append_output(result.stderr)
                self.statusBar.showMessage("Error al limpiar la caché", 5000)
                
        except Exception as e:
            self.append_output(f"Error inesperado: {str(e)}")
            self.statusBar.showMessage("Error inesperado al limpiar caché", 5000)
    
    def show_about(self):
        """Muestra el diálogo Acerca de"""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def load_config(self):
        """Carga la configuración guardada"""
        # Cargar tema
        theme = self.settings.value("theme", "Sistema")
        index = self.theme_combo.findText(theme)
        if index >= 0:
            self.theme_combo.setCurrentIndex(index)
        
        # Cargar configuración de notificaciones
        self.notif_updates.setChecked(self.settings.value("notif/updates", True, type=bool))
        self.notif_errors.setChecked(self.settings.value("notif/errors", True, type=bool))
        self.notif_complete.setChecked(self.settings.value("notif/complete", True, type=bool))
        self.notif_sound.setChecked(self.settings.value("notif/sound", False, type=bool))
        
        # Cargar configuración de actualizaciones
        self.auto_update_check.setChecked(self.settings.value("updates/auto_check", True, type=bool))
        
        # Cargar configuración de limpieza
        self.auto_clean_check.setChecked(self.settings.value("cleanup/enabled", False, type=bool))
        clean_freq = self.settings.value("cleanup/frequency", "Semanalmente")
        index = self.auto_clean_days.findText(clean_freq)
        if index >= 0:
            self.auto_clean_days.setCurrentIndex(index)
        
        # Cargar configuración de rendimiento
        self.parallel_downloads.setChecked(self.settings.value("performance/parallel_downloads", True, type=bool))
        max_downloads = self.settings.value("performance/max_downloads", "4")
        index = self.max_downloads.findText(max_downloads)
        if index >= 0:
            self.max_downloads.setCurrentIndex(index)
        
        # Aplicar configuración de fuente
        font_size = self.settings.value("ui/font_size", "Mediano")
        index = self.font_size.findText(font_size)
        if index >= 0:
            self.font_size.setCurrentIndex(index)
        self.update_font_size()
    
    def save_config(self):
        """Guarda la configuración actual"""
        # Guardar tema
        self.settings.setValue("theme", self.theme_combo.currentText())
        
        # Guardar configuración de notificaciones
        self.settings.setValue("notif/updates", self.notif_updates.isChecked())
        self.settings.setValue("notif/errors", self.notif_errors.isChecked())
        self.settings.setValue("notif/complete", self.notif_complete.isChecked())
        self.settings.setValue("notif/sound", self.notif_sound.isChecked())
        
        # Guardar configuración de actualizaciones
        self.settings.setValue("updates/auto_check", self.auto_update_check.isChecked())
        
        # Guardar configuración de limpieza
        self.settings.setValue("cleanup/enabled", self.auto_clean_check.isChecked())
        self.settings.setValue("cleanup/frequency", self.auto_clean_days.currentText())
        
        # Guardar configuración de rendimiento
        self.settings.setValue("performance/parallel_downloads", self.parallel_downloads.isChecked())
        self.settings.setValue("performance/max_downloads", self.max_downloads.currentText())
        
        # Guardar configuración de interfaz
        self.settings.setValue("ui/font_size", self.font_size.currentText())
        
        QMessageBox.information(self, "Configuración", "La configuración ha sido guardada correctamente.")
    
    def reset_settings(self):
        """Restablece la configuración a los valores por defecto"""
        reply = QMessageBox.question(
            self, 
            "Restablecer configuración",
            "¿Estás seguro de que deseas restablecer toda la configuración a los valores por defecto?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings.clear()
            self.load_config()
            QMessageBox.information(self, "Configuración", "La configuración ha sido restablecida a los valores por defecto.")
    
    def apply_theme(self, theme_name):
        """Aplica el tema seleccionado"""
        # Implementación básica - se puede mejorar con hojas de estilo
        if theme_name == "Claro":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #f0f0f0;
                }
                QTextEdit, QListWidget, QTreeWidget {
                    background-color: white;
                    border: 1px solid #d0d0d0;
                }
            """)
        elif theme_name == "Oscuro":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QTextEdit, QListWidget, QTreeWidget {
                    background-color: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #4a4a4a;
                }
                QLabel, QCheckBox, QRadioButton {
                    color: #e0e0e0;
                }
            """)
        else:  # Sistema
            self.setStyleSheet("")  # Restablecer al tema del sistema
    
    def update_font_size(self):
        """Actualiza el tamaño de fuente de la interfaz"""
        sizes = {
            "Pequeño": 9,
            "Mediano": 11,
            "Grande": 13,
            "Muy grande": 15
        }
        
        size = sizes.get(self.font_size.currentText(), 11)
        font = self.font()
        font.setPointSize(size)
        self.setFont(font)
    
    def toggle_parallel_downloads(self, state):
        """Habilita/deshabilita las descargas en paralelo"""
        self.max_downloads.setEnabled(state == Qt.CheckState.Checked.value)
    
    def update_repo_list(self):
        """Actualiza la lista de repositorios"""
        try:
            result = subprocess.check_output(["flatpak", "remotes", "--columns=name,url,options"], 
                                           text=True)
            self.repo_list.setPlainText(result.strip())
        except subprocess.CalledProcessError as e:
            self.repo_list.setPlainText("Error al obtener la lista de repositorios")
    
    def add_repository(self):
        """Añade un nuevo repositorio"""
        name, ok = QInputDialog.getText(self, "Añadir repositorio", "Nombre del repositorio:")
        if not ok or not name:
            return
            
        url, ok = QInputDialog.getText(self, "Añadir repositorio", "URL del repositorio:")
        if not ok or not url:
            return
            
        try:
            subprocess.run(["flatpak", "remote-add", "--if-not-exists", name, url], check=True)
            self.update_repo_list()
            QMessageBox.information(self, "Éxito", f"Repositorio '{name}' añadido correctamente.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"No se pudo añadir el repositorio: {e}")
    
    def remove_repository(self):
        """Elimina un repositorio"""
        repos = self.repo_list.toPlainText().split('\n')
        if not repos or not repos[0]:
            QMessageBox.warning(self, "Advertencia", "No hay repositorios para eliminar.")
            return
            
        repo_names = [repo.split('\t')[0] for repo in repos if '\t' in repo]
        if not repo_names:
            QMessageBox.warning(self, "Advertencia", "No se encontraron repositorios válidos.")
            return
            
        name, ok = QInputDialog.getItem(self, "Eliminar repositorio", 
                                       "Selecciona el repositorio a eliminar:", 
                                       repo_names, 0, False)
        if not ok or not name:
            return
            
        try:
            subprocess.run(["flatpak", "remote-delete", name], check=True)
            self.update_repo_list()
            QMessageBox.information(self, "Éxito", f"Repositorio '{name}' eliminado correctamente.")
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Error", f"No se pudo eliminar el repositorio: {e}")
    
    def show_documentation(self):
        """Muestra la documentación"""
        QMessageBox.information(
            self,
            "Documentación",
            "La documentación está disponible en: https://github.com/VicCodeM/flatpak-manager"
        )
    
    def closeEvent(self, event):
        """Se ejecuta al cerrar la aplicación"""
        if hasattr(self, 'tray_icon') and self.tray_icon.isVisible():
            reply = QMessageBox.question(
                self,
                'Confirmar salida',
                '¿Deseas minimizar a la bandeja en lugar de salir?',
                QMessageBox.StandardButton.Yes | 
                QMessageBox.StandardButton.No | 
                QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.hide()
                event.ignore()
            elif reply == QMessageBox.StandardButton.No:
                self.cleanup()
                event.accept()
            else:
                event.ignore()
        else:
            self.cleanup()
            event.accept()
            
    def export_list(self):
        """Exporta la lista de Flatpaks a un archivo"""
        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar lista de Flatpaks",
            f"flatpak-list-{datetime.now().strftime('%Y%m%d')}.txt",
            "Archivos de texto (*.txt);;Todos los archivos (*)"
        )
        
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write("=== Lista de Flatpaks instalados ===\n\n")
                    f.write(subprocess.check_output(
                        ["flatpak", "list", "--app", "--columns=application,name,version,branch"],
                        text=True
                    ))
                
                QMessageBox.information(
                    self,
                    "Exportación exitosa",
                    f"La lista de Flatpaks se ha exportado a:\n{file_name}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error al exportar",
                    f"No se pudo exportar la lista:\n{str(e)}"
                )

def main():
    app = QApplication(sys.argv)
    
    # Establecer estilo y tema
    app.setStyle('Fusion')
    
    # Crear y mostrar la ventana principal
    window = FlatpakManager()
    window.show()
    
    # Conectar la señal aboutToQuit para limpiar recursos
    def handle_about_to_quit():
        if hasattr(window, 'cleanup'):
            window.cleanup()
    
    app.aboutToQuit.connect(handle_about_to_quit)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
