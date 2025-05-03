import os
import platform as std_platform
import sys
import subprocess
import orjson
import time
import webbrowser
import pygame
import requests
import zipfile
import shutil
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QObject, QSize, QTranslator, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QMessageBox, QLineEdit,
    QFileDialog, QInputDialog, QDialog, QTableWidgetItem, QTableWidget, QGroupBox, QFormLayout, QProgressDialog,
    QSplashScreen, QCheckBox, QRadioButton, QButtonGroup, QOpenGLWidget
)
import minecraft_launcher_lib
from PIL import Image
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
import orjson
from PIL import Image, ImageTk
import minecraft_launcher_lib.fabric
import minecraft_launcher_lib.microsoft_account
import minecraft_launcher_lib.exceptions
from OpenGL import GL
from OpenGL.GLU import *
import numpy as np

minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory().replace("minecraft", "deflauncher")
mods_directory = os.path.join(minecraft_directory, "mods")
os.makedirs(mods_directory, exist_ok=True)
pictures_dir = os.path.join(minecraft_directory, 'assets', 'icons')
pygame.mixer.init()
internet = bool

timeout = 1

try:
    requests.head("https://i.imgur.com/PLANLN7.jpeg", timeout=timeout)
    internet = True
    print('The internet connection is active')
except requests.ConnectionError:
    internet = False
    print("The internet connection is down")

system = std_platform.system()

if system == "Windows":
    print("You are running on Windows.")
    explorer_path = os.path.join(pictures_dir, "explorer.png")
elif system == "Linux":
    print("You are running on Linux.")
    explorer_path = os.path.join(pictures_dir, "file_manager.png")
elif system == "Darwin":
    print("You are running on macOS.")
    explorer_path = os.path.join(pictures_dir, "finder.png")
else:
    webbrowser.open("https://www.microsoft.com/software-download/windows11")
    webbrowser.open("https://www.linux.org/pages/download/")
    print("You are running on an unknown OS.")

if internet == True:
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory().replace("minecraft", "deflauncher")
    splash_path = os.path.join(pictures_dir, "077bdfbf-0950-4e0d-bed2-5732339a1e6e.png")
    modrinth_path = os.path.join(pictures_dir, "Modrinth_idja4akuiu_0.png")
    modrinth_icon_path = os.path.join(pictures_dir, "22410180.png")
    sound_path = os.path.join(pictures_dir, "funny_82hiegE.mp3")
    explorer_path = os.path.join(pictures_dir, "explorer.png")
    fabric_path = os.path.join(pictures_dir, "fabric.png")
    forge_path = os.path.join(pictures_dir, "forge.png")
    save_icon_path = os.path.join(pictures_dir, "user.png")
    minecraft_icon_path = os.path.join(pictures_dir, "ezgif-6-0495bd1a5c.png")
    file_manager_path = os.path.join(pictures_dir, "file_manager.png")
    finder_path = os.path.join(pictures_dir, "finder.png")
    search_path = os.path.join(pictures_dir, "search-interface-symbol.png")
    back_path = os.path.join(pictures_dir, "back.png")
    next_path = os.path.join(pictures_dir, "next.png")
    rename_path = os.path.join(pictures_dir, "rename.png")
    add_button_path = os.path.join(pictures_dir, "add-button.png")
    remove_path = os.path.join(pictures_dir, "remove.png")
    MODRINTH_API_URL = "https://api.modrinth.com/v2"

    class SplashScreen(QSplashScreen):
        def __init__(self, splash_path):
            super().__init__()
            pixmap = QPixmap(splash_path)
            if not pixmap.isNull():
                self.setPixmap(pixmap)
                scaled_pixmap = pixmap.scaled(300, 200, Qt.KeepAspectRatio)
                self.setPixmap(scaled_pixmap)
                self.resize(scaled_pixmap.size())
                self.label = QLabel(self)
                self.label.setAlignment(Qt.AlignBottom | Qt.AlignHCenter)
                self.label.setFont(QFont("Arial", 10))
                self.label.resize(280, 50)

        def update_label(self, text):
            self.label.setText(text)

    class SkinWorker(QObject):
        progress = pyqtSignal(int)
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

        def __init__(self, profile_name, file_path, minecraft_directory, skin_type="slim"):
            super().__init__()
            self.profile_name = profile_name
            self.file_path = file_path
            self.minecraft_directory = minecraft_directory
            self.skin_type = skin_type

        def change_skin(self):
            try:
                with Image.open(self.file_path) as img:
                    img = img.resize((64, 64), Image.ANTIALIAS)
                    skin_path = os.path.join(self.minecraft_directory, self.profile_name, "skin.png")
                    img.save(skin_path)

                if self.skin_type == "slim":
                    self._adjust_slim_skin(img, skin_path)
                else:
                    self._adjust_wide_skin(img, skin_path)

                self.finished.emit("Skin changed successfully!")
            except Exception as e:
                self.error.emit(f"Error changing skin: {e}")

        def _adjust_slim_skin(self, img, skin_path):
            with Image.open(skin_path) as img:
                img = img.convert("RGBA")
                slim_arm_areas = [
                    (40, 20, 56, 32),
                    (8, 20, 24, 32)
                ]
                for area in slim_arm_areas:
                    left, top, right, bottom = area
                    img.paste((159, 75, 64, 255), area)
                img.save(skin_path)

        def _adjust_wide_skin(self, img, skin_path):
            with Image.open(skin_path) as img:
                img = img.convert("RGBA")
                wide_arm_areas = [
                    (32, 20, 48, 32),
                    (16, 20, 32, 32)
                ]
                for area in wide_arm_areas:
                    left, top, right, bottom = area
                    img.paste((159, 75, 64, 255), area)
                img.save(skin_path)

        def edit_skin(self, profile_name, skin_type="slim"):
            try:
                # Get the version directory
                version_dir = os.path.join(self.minecraft_dir, "versions", self.version)
                if not os.path.exists(version_dir):
                    self.error.emit("Minecraft version not found")
                    return

                # Get the jar file
                jar_file = os.path.join(version_dir, f"{self.version}.jar")
                if not os.path.exists(jar_file):
                    self.error.emit("Minecraft jar file not found")
                    return

                # Create a temporary directory for extraction
                temp_dir = os.path.join(self.minecraft_dir, "temp_skin_edit")
                os.makedirs(temp_dir, exist_ok=True)

                # Extract the jar file
                with zipfile.ZipFile(jar_file, 'r') as jar:
                    jar.extractall(temp_dir)

                # List of skins to replace
                skins_to_replace = ["alex", "ari", "efe", "kai", "makena", "noor", "steve", "sunny", "zury"]
                replaced_count = 0

                # Ask user to select a skin file
                skin_file, _ = QFileDialog.getOpenFileName(
                    self.main_window,
                    "Select Skin File",
                    "",
                    "PNG Files (*.png)"
                )
                
                if not skin_file:
                    self.error.emit("No skin file selected")
                    return

                # Show preview and get skin type
                preview_dialog = SkinPreviewDialog(self.main_window)
                preview_dialog.set_preview(skin_file)
                
                if preview_dialog.exec_() != QDialog.Accepted:
                    self.error.emit("Skin selection cancelled")
                    return
                    
                selected_type = preview_dialog.get_skin_type()

                # Path to the skins directory
                skins_dir = os.path.join(temp_dir, "assets", "minecraft", "textures", "entity", "player", selected_type)
                if not os.path.exists(skins_dir):
                    self.error.emit(f"Skins directory not found for type: {selected_type}")
                    return

                # Replace each skin
                for skin_name in skins_to_replace:
                    target_path = os.path.join(skins_dir, f"{skin_name}.png")
                    if os.path.exists(target_path):
                        shutil.copy2(skin_file, target_path)
                        replaced_count += 1

                if replaced_count == 0:
                    self.error.emit("No matching skin files found to replace")
                    return

                # Repack the jar file
                with zipfile.ZipFile(jar_file, 'w') as jar:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            jar.write(file_path, arcname)

                self.finished.emit(f"Successfully replaced {replaced_count} skins in {selected_type} directory")

            except Exception as e:
                self.error.emit(f"Failed to edit skins: {e}")
            finally:
                # Clean up
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

    class JavaInstaller(QThread):
        progress = pyqtSignal(int)
        finished = pyqtSignal(bool)
        error = pyqtSignal(str)

        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent
            self.java_url = None
            self.install_location = None
            self.add_to_path = False
            self.create_shortcut = False

        def set_installation_options(self, java_url, install_location, add_to_path, create_shortcut):
            self.java_url = java_url
            self.install_location = install_location
            self.add_to_path = add_to_path
            self.create_shortcut = create_shortcut

        def run(self):
            try:
                # Create installation directory
                os.makedirs(self.install_location, exist_ok=True)
                
                # Download Java installer
                installer_path = os.path.join(self.install_location, "java_installer.exe")
                
                response = requests.get(self.java_url, stream=True)
                total_size = int(response.headers.get('content-length', 0))
                block_size = 1024
                downloaded = 0
                
                with open(installer_path, 'wb') as f:
                    for data in response.iter_content(block_size):
                        downloaded += len(data)
                        f.write(data)
                        progress = int((downloaded / total_size) * 50)  # First 50% for download
                        self.progress.emit(progress)
                
                # Run Java installer with custom location
                install_args = [
                    installer_path,
                    '/s',
                    f'INSTALLDIR="{self.install_location}"',
                    'AUTO_UPDATE=0'
                ]
                
                if self.add_to_path:
                    install_args.append('ADDLOCAL=FeatureMain,FeatureEnvironment')
                else:
                    install_args.append('ADDLOCAL=FeatureMain')
                
                subprocess.run(install_args, check=True)
                self.progress.emit(75)
                
                # Create desktop shortcut if requested
                if self.create_shortcut:
                    java_exe = os.path.join(self.install_location, "bin", "java.exe")
                    if os.path.exists(java_exe):
                        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
                        shortcut_path = os.path.join(desktop, "Java.lnk")
                        
                        # Create shortcut using Windows API
                        import pythoncom
                        from win32com.client import Dispatch
                        
                        shell = Dispatch('WScript.Shell')
                        shortcut = shell.CreateShortCut(shortcut_path)
                        shortcut.Targetpath = java_exe
                        shortcut.WorkingDirectory = os.path.dirname(java_exe)
                        shortcut.save()
                
                self.progress.emit(100)
                self.finished.emit(True)
                
            except Exception as e:
                self.error.emit(str(e))
            finally:
                # Clean up installer
                if os.path.exists(installer_path):
                    os.remove(installer_path)

    class InstallWorker(QThread):
        progress = pyqtSignal(int)
        finished = pyqtSignal(str)
        error = pyqtSignal(str)

        def __init__(self, modloader, version, minecraft_dir, parent=None):
            super().__init__(parent)
            self.main_window = parent
            self.modloader = modloader
            self.version = version
            self.minecraft_dir = minecraft_dir

        def run(self):
            try:
                if self.modloader == "Fabric":
                    self.install_fabric()
                elif self.modloader == "Forge":
                    self.install_forge()
                else:
                    self.install_vanilla()
            except Exception as e:
                self.error.emit(str(e))

        def install_fabric(self):
            try:
                latest_fabric_loader = minecraft_launcher_lib.fabric.get_latest_loader_version()
                total_steps = 3
                self.progress.emit(0)
                
                # Step 1: Download Fabric loader
                self.progress.emit(33)
                minecraft_launcher_lib.fabric.install_fabric(self.version, self.minecraft_dir)
                
                # Step 2: Install Fabric
                self.progress.emit(66)
                minecraft_launcher_lib.fabric.install_fabric(self.version, self.minecraft_dir)
                
                self.progress.emit(100)
                self.finished.emit(f"Fabric (loader {latest_fabric_loader}) for Minecraft {self.version} installed successfully.")
            except Exception as e:
                self.error.emit(str(e))

        def install_forge(self):
            try:
                forge_version = minecraft_launcher_lib.forge.find_forge_version(self.version)
                total_steps = 3
                self.progress.emit(0)
                
                # Step 1: Download Forge installer
                self.progress.emit(33)
                minecraft_launcher_lib.forge.install_forge_version(forge_version, self.minecraft_dir)
                
                # Step 2: Install Forge
                self.progress.emit(66)
                minecraft_launcher_lib.forge.install_forge_version(forge_version, self.minecraft_dir)
                
                self.progress.emit(100)
                self.finished.emit(f"Forge for Minecraft {self.version} installed successfully.")
            except Exception as e:
                self.error.emit(str(e))

        def install_vanilla(self):
            try:
                total_steps = 3
                self.progress.emit(0)
                
                # Step 1: Download Minecraft version
                self.progress.emit(33)
                minecraft_launcher_lib.install.install_minecraft_version(self.version, self.minecraft_dir)
                
                # Step 2: Install dependencies
                self.progress.emit(66)
                minecraft_launcher_lib.install.install_minecraft_version(self.version, self.minecraft_dir)
                
                self.progress.emit(100)
                self.finished.emit(f"Minecraft {self.version} installed successfully.")
            except Exception as e:
                self.error.emit(str(e))

        def edit_skin(self, profile_name, skin_type="slim"):
            try:
                # Get the version directory
                version_dir = os.path.join(self.minecraft_dir, "versions", self.version)
                if not os.path.exists(version_dir):
                    self.error.emit("Minecraft version not found")
                    return

                # Get the jar file
                jar_file = os.path.join(version_dir, f"{self.version}.jar")
                if not os.path.exists(jar_file):
                    self.error.emit("Minecraft jar file not found")
                    return

                # Create a temporary directory for extraction
                temp_dir = os.path.join(self.minecraft_dir, "temp_skin_edit")
                os.makedirs(temp_dir, exist_ok=True)

                # Extract the jar file
                with zipfile.ZipFile(jar_file, 'r') as jar:
                    jar.extractall(temp_dir)

                # List of skins to replace
                skins_to_replace = ["alex", "ari", "efe", "kai", "makena", "noor", "steve", "sunny", "zury"]
                replaced_count = 0

                # Ask user to select a skin file
                skin_file, _ = QFileDialog.getOpenFileName(
                    self.main_window,
                    "Select Skin File",
                    "",
                    "PNG Files (*.png)"
                )
                
                if not skin_file:
                    self.error.emit("No skin file selected")
                    return

                # Show preview and get skin type
                preview_dialog = SkinPreviewDialog(self.main_window)
                preview_dialog.set_preview(skin_file)
                
                if preview_dialog.exec_() != QDialog.Accepted:
                    self.error.emit("Skin selection cancelled")
                    return
                    
                selected_type = preview_dialog.get_skin_type()

                # Path to the skins directory
                skins_dir = os.path.join(temp_dir, "assets", "minecraft", "textures", "entity", "player", selected_type)
                if not os.path.exists(skins_dir):
                    self.error.emit(f"Skins directory not found for type: {selected_type}")
                    return

                # Replace each skin
                for skin_name in skins_to_replace:
                    target_path = os.path.join(skins_dir, f"{skin_name}.png")
                    if os.path.exists(target_path):
                        shutil.copy2(skin_file, target_path)
                        replaced_count += 1

                if replaced_count == 0:
                    self.error.emit("No matching skin files found to replace")
                    return

                # Repack the jar file
                with zipfile.ZipFile(jar_file, 'w') as jar:
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            jar.write(file_path, arcname)

                self.finished.emit(f"Successfully replaced {replaced_count} skins in {selected_type} directory")

            except Exception as e:
                self.error.emit(f"Failed to edit skins: {e}")
            finally:
                # Clean up
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

    class ModrinthManager(QDialog):
        def __init__(self, main_window, instance_path):
            super().__init__()
            self.setWindowTitle("Modrinth Manager")
            self.setWindowIcon(QIcon(modrinth_icon_path))
            self.main_window = main_window
            self.setGeometry(400, 400, 800, 600)
            self.instance_path = instance_path
            self.mods_folder = mods_directory

            self.mod_urls = {}

            self.current_page = 1
            self.total_pages = 1
            self.current_query = ""

            main_layout = QVBoxLayout()
            search_layout = QHBoxLayout()

            self.search_input = QLineEdit(self)
            self.search_input.setPlaceholderText("Search mods on Modrinth...")
            search_layout.addWidget(self.search_input)

            self.search_button = QPushButton("Search", self)
            self.search_button.setIcon(QIcon(search_path))
            self.search_button.setIconSize(QSize(16, 16))
            self.search_button.clicked.connect(self.search_mods)
            search_layout.addWidget(self.search_button)

            self.pagination_layout = QHBoxLayout()
            main_layout.addLayout(search_layout)
            main_layout.addLayout(self.pagination_layout)

            self.results_table = QTableWidget(self)
            self.results_table.setColumnCount(3)
            self.results_table.setHorizontalHeaderLabels(["", "Mod Name", "Description"])
            self.results_table.cellDoubleClicked.connect(self.handle_cell_double_click)
            main_layout.addWidget(self.results_table)

            self.setLayout(main_layout)

            self.load_popular_mods()

        def search_mods(self):
            query = self.search_input.text()
            self.current_query = query
            self.current_page = 1

            if not query:
                self.load_popular_mods()
                return

            try:
                response = requests.get(
                    f"{MODRINTH_API_URL}/search",
                    params={
                        "query": query,
                        "limit": 16,
                        "project_type": "mod",
                        "offset": (self.current_page - 1) * 16
                    }
                )
                response.raise_for_status()
                results = response.json()["hits"]
                total_hits = response.json().get("total_hits", 0)
                self.total_pages = (total_hits // 16) + 1

                self.display_results(results)
                self.update_pagination_buttons(self.total_pages)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to search mods: {e}")

        def load_popular_mods(self):
            try:
                response = requests.get(
                    f"{MODRINTH_API_URL}/search",
                    params={
                        "query": "",
                        "limit": 16,
                        "project_type": "mod",
                        "sort_by": "downloads",
                        "offset": (self.current_page - 1) * 16
                    }
                )
                response.raise_for_status()
                results = response.json()["hits"]
                total_hits = response.json().get("total_hits", 0)
                self.total_pages = (total_hits // 16) + 1

                self.display_results(results)
                self.update_pagination_buttons(self.total_pages)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load popular mods: {e}")

        def go_to_page(self, page):
            print(f"Going to page {page}")
            self.current_page = page
            if self.current_query:
                self.search_mods()
            else:
                self.load_popular_mods()

        def prev_page(self):
            print("Previous button clicked")
            if self.current_page > 1:
                self.current_page -= 1
                if self.current_query:
                    self.search_mods()
                else:
                    self.load_popular_mods()

        def next_page(self):
            print("Next button clicked")
            if self.current_page < self.total_pages:
                self.current_page += 1
                if self.current_query:
                    self.search_mods()
                else:
                    self.load_popular_mods()

        def display_results(self, results):
            self.results_table.setRowCount(len(results))
            self.mod_urls.clear()

            for row, mod in enumerate(results):
                row_widget = QWidget()
                row_layout = QHBoxLayout()
                row_layout.setContentsMargins(1, 1, 1, 1)
                row_layout.setSpacing(20)

                icon_url = mod.get("icon_url")
                if icon_url:
                    response = requests.get(icon_url, stream=True)
                    response.raise_for_status()
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)

                    icon_label = QLabel()
                    icon_label.setPixmap(
                        pixmap.scaled(32, 32, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                    row_layout.addWidget(icon_label)

                name_label = QLabel(mod["title"])
                name_label.setStyleSheet("margin-left: 10px;")

                description = mod.get("description", "No description available")
                description_label = QLabel(description)
                description_label.setWordWrap(True)

                self.results_table.setCellWidget(row, 0, row_widget)
                self.results_table.setCellWidget(row, 1, name_label)
                self.results_table.setCellWidget(row, 2, description_label)

                row_widget.setLayout(row_layout)

                project_id_item = QTableWidgetItem()
                project_id_item.setData(256, mod["project_id"])
                self.results_table.setItem(row, 0, project_id_item)

                mod_slug = mod.get("slug", "")
                mod_url = f"https://modrinth.com/mod/{mod_slug}"
                self.mod_urls[row] = mod_url

            self.results_table.setColumnWidth(0, 50)
            self.results_table.setColumnWidth(1, 300)
            self.results_table.setColumnWidth(2, 400)

        def update_pagination_buttons(self, total_pages):
            for i in reversed(range(self.pagination_layout.count())):
                widget = self.pagination_layout.itemAt(i).widget()
                if widget:
                    widget.deleteLater()

            prev_button = QPushButton("Previous", self)
            prev_button.setIcon(QIcon(back_path))
            prev_button.setIconSize(QSize(16, 16))
            prev_button.clicked.connect(self.prev_page)
            prev_button.setEnabled(self.current_page > 1)
            self.pagination_layout.addWidget(prev_button)

            max_buttons = 5
            half_max = max_buttons // 2
            start_page = max(1, self.current_page - half_max)
            end_page = min(total_pages, start_page + max_buttons - 1)

            if start_page > 1:
                ellipsis = QLabel("...")
                self.pagination_layout.addWidget(ellipsis)

            for page in range(start_page, end_page + 1):
                page_button = QPushButton(str(page), self)
                page_button.setEnabled(page != self.current_page)
                page_button.clicked.connect(lambda _, p=page: self.go_to_page(p))
                self.pagination_layout.addWidget(page_button)

            if end_page < total_pages:
                ellipsis = QLabel("...")
                self.pagination_layout.addWidget(ellipsis)

            next_button = QPushButton(self)
            next_button.setIcon(QIcon(next_path))
            next_button.setIconSize(QSize(16, 16))
            next_button.setText("Next")
            next_button.clicked.connect(self.next_page)
            next_button.setEnabled(self.current_page < total_pages)
            self.pagination_layout.addWidget(next_button)

        def handle_cell_double_click(self, row, column):
            if column == 2:
                self.open_mod_in_browser(row)
            else:
                self.show_versions(row, column)

        def open_mod_in_browser(self, row):
            if row in self.mod_urls:
                mod_url = self.mod_urls[row]
                webbrowser.open(mod_url)
            else:
                QMessageBox.warning(self, "Error", "No URL found for this mod.")

        def show_versions(self, row, column):
            mod_id = self.results_table.item(row, 0).data(256)
            minecraft_version = self.main_window.version_combo.currentText()
            modloader = self.main_window.modloader_combo.currentText().lower()

            try:
                response = requests.get(f"{MODRINTH_API_URL}/project/{mod_id}/version")
                response.raise_for_status()
                versions = response.json()

                compatible_versions = [
                    v for v in versions if minecraft_version in v["game_versions"] and modloader in v["loaders"]
                ]

                if not compatible_versions:
                    QMessageBox.warning(self, "No Compatible Versions",
                                        "No versions match the selected Minecraft version and mod loader.")
                    return

                version_names = [v["name"] for v in compatible_versions]

                version, ok = QInputDialog.getItem(self, "Select Version", "Available Versions:", version_names,
                                                   editable=False)

                if ok and version:
                    selected_version = next(v for v in compatible_versions if v["name"] == version)
                    self.download_mod(selected_version)

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to fetch versions: {e}")

        def download_mod(self, version):
            try:
                for file in version["files"]:
                    if file["primary"]:
                        mod_url = file["url"]
                        mod_name = file["filename"]
                        mod_path = os.path.join(self.mods_folder, mod_name)

                        response = requests.get(mod_url, stream=True)
                        response.raise_for_status()

                        with open(mod_path, 'wb') as f:
                            total_size = int(response.headers.get("Content-Length", 0))
                            downloaded_size = 0

                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                                downloaded_size += len(chunk)

                        QMessageBox.information(self, "Download Complete",
                                                f"{mod_name} has been successfully downloaded to:\n{self.mods_folder}")
                        return

                QMessageBox.warning(self, "Error", "No primary file found for this version.")
            except requests.exceptions.RequestException as e:
                QMessageBox.critical(self, "Download Error", f"Failed to download mod: {e}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"An unexpected error occurred: {e}")

    class OptionsManager(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent

        def init(self):
            self.setWindowTitle("Options")
            layout = QFormLayout(self)

            # Theme option
            theme_label = QLabel("UI Theme:")
            self.theme_input = QLineEdit()
            self.theme_input.setText(self.parent.options.get("theme", "Default"))
            self.theme_input.setPlaceholderText("Enter theme name")
            layout.addRow(theme_label, self.theme_input)

            # Language option
            lang_label = QLabel("Language:")
            self.lang_combo = QComboBox()
            self.lang_combo.addItems(["English", "Russian", "Spanish", "French"])
            self.lang_combo.setCurrentText(self.parent.options.get("language", "English"))
            layout.addRow(lang_label, self.lang_combo)

            # Java path option
            java_layout = QHBoxLayout()
            self.java_path_input = QLineEdit()
            self.java_path_input.setText(self.parent.options.get("java_path", ""))
            self.java_path_input.setPlaceholderText("Path to Java executable")
            java_layout.addWidget(self.java_path_input)
            
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(self.browse_java_path)
            java_layout.addWidget(browse_button)
            
            layout.addRow(QLabel("Java Path:"), java_layout)

            # Auto-install Java option
            self.auto_install_java_checkbox = QCheckBox("Automatically install Java if not found")
            self.auto_install_java_checkbox.setChecked(self.parent.options.get("auto_install_java", True))
            layout.addRow(self.auto_install_java_checkbox)

            # Hide launcher option
            self.hide_launcher_checkbox = QCheckBox("Hide launcher when game is running")
            self.hide_launcher_checkbox.setChecked(self.parent.options.get("hide_launcher", False))
            layout.addRow(self.hide_launcher_checkbox)

            # Save button
            save_button = QPushButton("Save Options")
            save_button.clicked.connect(self.save_options)
            layout.addRow(save_button)

            # Hamster image (for fun)
            self.hamster_label = QLabel(self)
            self.chompick_path = os.path.join(pictures_dir, 'NormalnyChomik-ezgif.com-webp-to-png-converter.png')
            try:
                self.hamster_label.setPixmap(QPixmap(self.chompick_path))
            except Exception as e:
                print(f"Error loading image: {e}")
                self.hamster_label.setText("Image not found")
            self.hamster_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.hamster_label.mousePressEvent = self.hamster_clicked
            layout.addRow(self.hamster_label)

            self.setLayout(layout)

        def browse_java_path(self):
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Java Executable",
                "",
                "Executable Files (*.exe);;All Files (*)"
            )
            if file_path:
                self.java_path_input.setText(file_path)

        def save_options(self):
            theme_name = self.theme_input.text()
            language = self.lang_combo.currentText()
            hide_launcher = self.hide_launcher_checkbox.isChecked()
            java_path = self.java_path_input.text()
            auto_install_java = self.auto_install_java_checkbox.isChecked()

            valid_themes = ["Default", "Dark", "Light"]
            if theme_name not in valid_themes:
                QMessageBox.warning(self, "Invalid Theme", f"Theme '{theme_name}' is not valid.")
                return

            # Update the parent's options
            self.parent.options = {
                "theme": theme_name,
                "language": language,
                "hide_launcher": hide_launcher,
                "java_path": java_path,
                "auto_install_java": auto_install_java
            }

            # Save options using orjson
            try:
                with open(self.parent.options_file, "wb") as file:
                    file.write(orjson.dumps(self.parent.options, option=orjson.OPT_INDENT_2))
                QMessageBox.information(self, "Options Saved", "Settings have been saved.")
                self.play_funny_sound()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save options: {e}")

        def hamster_clicked(self, event):
            if event.button() == Qt.LeftButton:
                self.play_funny_sound()

        def play_funny_sound(self):
            try:
                pygame.mixer.init()
                if hasattr(self, 'sound') and self.sound.get_busy():
                    self.sound.stop()
                self.sound = pygame.mixer.Sound(sound_path)
                self.sound.play()
            except Exception as e:
                print(f"Error playing sound: {e}")

        def show_options_dialog(self):
            self.init()
            self.exec_()

    class MinecraftLauncher(QWidget):
        def __init__(self):
            super().__init__()
            self.translator = QTranslator()

            self.setWindowTitle("DefLauncher 0.8 BETA TEST")
            self.setGeometry(300, 300, 700, 700)
            self.setWindowIcon(QIcon(splash_path))

            ProfileManagement = "Profile Management"

            self.profiles_file = os.path.join(minecraft_directory, "profiles.json")
            self.options_file = os.path.join(minecraft_directory, "options.json")
            self.options = self.load_options()
            self.profiles = self.load_profiles()
            self.apply_options()

            self.options_manager = OptionsManager(self)

            main_layout = QVBoxLayout()

            profile_group = QGroupBox(self.tr(ProfileManagement))
            profile_layout = QFormLayout()

            self.profile_combo = QComboBox(self)
            self.profile_combo.addItems(self.profiles.keys())
            self.profile_combo.currentTextChanged.connect(self.update_profile_ui)
            profile_layout.addRow(QLabel(self.tr("Profile:")), self.profile_combo)

            button_layout = QHBoxLayout()
            self.rename_profile_button = QPushButton(self.tr("Rename"))
            self.rename_profile_button.setIcon(QIcon(rename_path))
            self.rename_profile_button.setIconSize(QSize(16, 16))
            self.rename_profile_button.clicked.connect(self.rename_profile)
            button_layout.addWidget(self.rename_profile_button)
            self.new_profile_button = QPushButton(self.tr("New"))
            self.new_profile_button.setIcon(QIcon(add_button_path))
            self.new_profile_button.setIconSize(QSize(16, 16))
            self.new_profile_button.clicked.connect(self.create_new_profile)
            button_layout.addWidget(self.new_profile_button)
            self.delete_profile_button = QPushButton(self.tr("Delete"))
            self.delete_profile_button.setIcon(QIcon(remove_path))
            self.delete_profile_button.setIconSize(QSize(16, 16))
            self.delete_profile_button.clicked.connect(self.delete_profile)
            button_layout.addWidget(self.delete_profile_button)

            profile_layout.addRow(button_layout)
            profile_group.setLayout(profile_layout)
            main_layout.addWidget(profile_group)

            user_group = QGroupBox(self.tr("User Details"))
            user_layout = QFormLayout()

            self.username_input = QLineEdit(self)
            user_layout.addRow(QLabel(self.tr("Username:")), self.username_input)

            self.skin_button = QPushButton("Change Skin")
            self.skin_button.clicked.connect(self.change_skin)
            user_layout.addRow(self.skin_button)
            user_group.setLayout(user_layout)
            main_layout.addWidget(user_group)

            config_group = QGroupBox("Minecraft Configuration")
            config_layout = QFormLayout()

            self.version_combo = QComboBox(self)
            self.version_combo.addItems([version["id"] for version in minecraft_launcher_lib.utils.get_version_list()])
            config_layout.addRow(QLabel("Minecraft Version:"), self.version_combo)

            self.modloader_combo = QComboBox(self)
            self.modloader_combo.addItems(["Vanilla", "Fabric", "Forge"])
            config_layout.addRow(QLabel("Mod Loader:"), self.modloader_combo)

            config_group.setLayout(config_layout)
            main_layout.addWidget(config_group)

            actions_group = QGroupBox("Actions")
            actions_layout = QVBoxLayout()

            self.launch_button = QPushButton("Play",
                                             self)
            self.launch_button.setIconSize(QSize(32, 32))
            self.launch_button.clicked.connect(self.launch_minecraft)
            self.launch_button.setStyleSheet("""
                        QPushButton {
                            font-size: 16px;
                            padding: 10px;
                            border: none;
                            background-color: #4CAF50;
                            color: white;
                            border-radius: 8px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
            actions_layout.addWidget(self.launch_button)

            self.save_profile_button = QPushButton("Save Profile")
            self.save_profile_button.setIcon(QIcon(save_icon_path))
            self.save_profile_button.setIconSize(QSize(16, 16))
            self.save_profile_button.clicked.connect(self.save_profile)
            actions_layout.addWidget(self.save_profile_button)

            self.open_launcher_dir_button = QPushButton("Open Launcher Directory")
            self.open_launcher_dir_button.setIcon(QIcon(explorer_path))
            self.open_launcher_dir_button.setIconSize(QSize(16, 16))
            self.open_launcher_dir_button.clicked.connect(self.open_launcher_directory)
            actions_layout.addWidget(self.open_launcher_dir_button)

            self.install_button = QPushButton()
            self.install_button.clicked.connect(self.install_modloader)
            actions_layout.addWidget(self.install_button)
            self.modloader_combo.currentIndexChanged.connect(self.update_install_button_icon)
            self.update_install_button_icon()

            self.open_mod_folder_button = QPushButton("Open Mods Folder")
            self.open_mod_folder_button.setIcon(QIcon(explorer_path))
            self.open_mod_folder_button.setIconSize(QSize(16, 16))
            self.open_mod_folder_button.clicked.connect(self.open_mods_folder)
            actions_layout.addWidget(self.open_mod_folder_button)

            self.modrinth_button = QPushButton("Modrinth Mod Manager")
            self.modrinth_button.setIcon(QIcon(modrinth_icon_path))
            self.modrinth_button.setIconSize(QSize(16, 16))
            self.modrinth_button.clicked.connect(self.open_modrinth_manager)
            actions_layout.addWidget(self.modrinth_button)

            self.options_button = QPushButton("Options")
            options = os.path.join(pictures_dir, "settings.png")
            options_icon = QIcon(options)
            self.options_button.setIcon(options_icon)
            self.options_button.setIconSize(QSize(16, 16))
            self.options_button.clicked.connect(self.options_manager.show_options_dialog)
            actions_layout.addWidget(self.options_button)

            actions_group.setLayout(actions_layout)
            main_layout.addWidget(actions_group)

            self.setLayout(main_layout)
            self.update_profile_ui()

        def update_install_button_icon(self):
            selected_modloader = self.modloader_combo.currentText()
            if selected_modloader == "Fabric":
                self.install_button.setText("Install Fabric")
                self.install_button.setIcon(QIcon(fabric_path))
            elif selected_modloader == "Forge":
                self.install_button.setText("Install Forge")
                self.install_button.setIcon(QIcon(forge_path))
            else:
                self.install_button.setText("Install Minecraft")
                self.install_button.setIcon(QIcon(minecraft_icon_path))
            self.install_button.setIconSize(QSize(16, 16))

        def delete_profile(self):
            profile_name = self.profile_combo.currentText()
            if not profile_name:
                QMessageBox.warning(self, "No Profile Selected", "Please select a profile to delete.")
                return
            elif profile_name == "Default":
                QMessageBox.critical(self, "Cannot Delete Profile", "You cannot delete the default profile.")
                return

            reply = QMessageBox.question(self, 'Delete Profile', f'Are you sure you want to delete "{profile_name}"?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                del self.profiles[profile_name]
                self.save_profiles()
                self.profile_combo.clear()
                self.profile_combo.addItems(self.profiles.keys())
                if self.profile_combo.count() > 0:
                    self.profile_combo.setCurrentIndex(0)
                else:
                    self.username_input = "Player"
                    self.version_combo.setCurrentText("latest")
                    self.modloader_combo.setCurrentText("Vanilla")

        def open_modrinth_manager(self):
            profile_name = self.profile_combo.currentText()
            profile_path = os.path.join(minecraft_directory, profile_name)
            self.modrinth_manager = ModrinthManager(self, profile_path)
            self.modrinth_manager.exec_()

        def update_profile_ui(self):
            profile_name = self.profile_combo.currentText()
            profile = self.profiles.get(profile_name, {})
            self.username_input.setText(profile.get("username", "Player"))
            self.version_combo.setCurrentText(profile.get("version", "latest"))
            self.modloader_combo.setCurrentText(profile.get("modloader", "Vanilla"))

        def save_profile(self):
            profile_name = self.profile_combo.currentText()
            self.profiles[profile_name] = {
                "username": self.username_input.text(),
                "version": self.version_combo.currentText(),
                "modloader": self.modloader_combo.currentText(),
            }
            self.save_profiles()
            QMessageBox.information(self, "Profile Saved", f"Profile '{profile_name}' has been saved.")

        def rename_profile(self):
            profile_name = self.profile_combo.currentText()
            new_name, ok = QInputDialog.getText(self, "Rename Profile", "Enter new profile name:")
            if ok and new_name:
                self.profiles[new_name] = self.profiles.pop(profile_name)
                self.save_profiles()
                self.profile_combo.clear()
                self.profile_combo.addItems(self.profiles.keys())
                self.profile_combo.setCurrentText(new_name)

        def create_new_profile(self):
            new_name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
            if ok and new_name:
                self.profiles[new_name] = {"username": "Player", "version": "latest", "modloader": "Vanilla"}
                self.save_profiles()
                self.profile_combo.addItem(new_name)
                self.profile_combo.setCurrentText(new_name)

        def change_skin(self):
            profile_name = self.profile_combo.currentText()
            self.worker = InstallWorker(self.modloader_combo.currentText(), self.version_combo.currentText(), minecraft_directory)
            self.worker.edit_skin(profile_name)

        def update_installation_progress(self, value):
            print(f"Installation Progress: {value}%")

        def install_modloader(self):
            selected_modloader = self.modloader_combo.currentText()
            selected_version = self.version_combo.currentText()

            self.worker = InstallWorker(selected_modloader, selected_version, minecraft_directory)
            if selected_modloader == "Vanilla":
                progress_dialog = QProgressDialog(f"Installing Minecraft {selected_version}", "Cancel", 0, 100, self)
                progress_dialog.setWindowTitle("Installation Progress")
                progress_dialog.setWindowModality(Qt.WindowModal)
            else:
                progress_dialog = QProgressDialog("Installing Mod Loader for Minecraft...", "Cancel", 0, 200, self)
                progress_dialog.setWindowTitle("Installation Progress")
            progress_dialog.setWindowModality(Qt.WindowModal)

            self.worker.progress.connect(progress_dialog.setValue)
            self.worker.finished.connect(lambda message: self.on_install_finished(message, progress_dialog))
            self.worker.error.connect(lambda error: self.on_install_error(error, progress_dialog))

            self.worker.start()

            progress_dialog.canceled.connect(self.worker.terminate)

        def on_install_finished(self, message, progress_dialog):
            progress_dialog.close()
            QMessageBox.information(self, "Installation Complete", message)

        def on_install_error(self, error, progress_dialog):
            progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Failed to install mod loader: {error}")

        def open_mods_folder(self):
            try:
                os.startfile(mods_directory) if os.name == "nt" else subprocess.call(["open", mods_directory])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open mods folder: {e}")

        def open_launcher_directory(self):
            try:
                os.startfile(minecraft_directory) if os.name == "nt" else subprocess.call(["open", minecraft_directory])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open launcher directory: {e}")

        def load_profiles(self):
            if os.path.exists(self.profiles_file):
                try:
                    with open(self.profiles_file, "rb") as file:
                        return orjson.loads(file.read())
                except Exception as e:
                    print(f"Failed to load profiles: {e}. Using default profile.")
                    return {"Default": {"username": "Player", "version": "latest", "modloader": "Vanilla"}}
            return {"Default": {"username": "Player", "version": "latest", "modloader": "Vanilla"}}

        def save_profiles(self):
            try:
                os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
                with open(self.profiles_file, "wb") as file:
                    file.write(orjson.dumps(self.profiles, option=orjson.OPT_INDENT_2))
                print("Profiles saved successfully.")
            except Exception as e:
                print(f"Failed to save profiles: {e}")

        def launch_minecraft(self):
            try:
                # Check for Java installation
                if not self.check_java_installation():
                    if not self.install_java():
                        return

                profile_name = self.profile_combo.currentText()
                selected_version = self.version_combo.currentText()
                selected_modloader = self.modloader_combo.currentText()

                # Get all installed Minecraft versions
                all_versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)
                valid_versions = [v['id'] for v in all_versions]

                # Determine the version to launch based on modloader
                version_to_launch = selected_version  # Default to vanilla
                forge_version = None

                # Handle Forge-specific logic
                if selected_modloader == "Forge":
                    forge_versions = minecraft_launcher_lib.forge.find_forge_version(selected_version)
                    if not forge_versions:
                        QMessageBox.critical(self, "Error", f"No Forge version found for {selected_version}")
                        return
                    forge_version = forge_versions[0]  # Take the first available Forge version
                    version_to_launch = f"{selected_version}-forge-{forge_version}"

                # Handle Fabric-specific logic
                elif selected_modloader == "Fabric":
                    try:
                        fabric_versions = minecraft_launcher_lib.fabric.get_all_minecraft_versions()
                        if selected_version not in [v['version'] for v in fabric_versions]:
                            QMessageBox.critical(self, "Error", f"Fabric doesn't support {selected_version}")
                            return
                        loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()
                        version_to_launch = f"fabric-loader-{loader_version}-{selected_version}"
                        
                        # Ensure Fabric is installed
                        if not minecraft_launcher_lib.fabric.is_fabric_installed(version_to_launch, minecraft_directory):
                            QMessageBox.critical(self, "Error", "Fabric is not installed. Please install it first.")
                            return
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to initialize Fabric: {e}")
                        return

                # Validate that the determined version is installed
                if version_to_launch not in valid_versions:
                    QMessageBox.critical(self, "Error", f"Version {version_to_launch} is not installed. Please install it first.")
                    return

                # Set up mods directory for Fabric and ensure it exists
                mods_folder = os.path.join(minecraft_directory, profile_name, "mods")
                if selected_modloader == "Fabric":
                    os.makedirs(mods_folder, exist_ok=True)

                # Prepare launch options without JVM arguments
                options = {
                    "username": self.username_input.text(),
                    "uuid": "dummy-uuid",
                    "token": "dummy-token",
                    "javaPath": self.options.get("java_path", "")
                }

                # Generate and execute the Minecraft command
                minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
                    version_to_launch, minecraft_directory, options
                )
                
                # Hide launcher if option is enabled
                if self.options.get("hide_launcher", False):
                    self.hide()
                
                # Launch Minecraft with proper error handling
                process = subprocess.Popen(
                    minecraft_command,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait for the process to complete
                stdout, stderr = process.communicate()
                
                # Show launcher again after game closes
                if self.options.get("hide_launcher", False):
                    self.show()
                    
                # Check if there were any errors
                if process.returncode != 0:
                    error_message = f"Failed to launch Minecraft (Exit code: {process.returncode})"
                    if stderr:
                        error_message += f"\n\nError output:\n{stderr}"
                    QMessageBox.critical(self, "Error", error_message)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to launch Minecraft: {e}")
                if self.options.get("hide_launcher", False):
                    self.show()

        def load_options(self):
            default_options = {
                "theme": "Default",
                "language": "English",
                "hide_launcher": False
            }

            if os.path.exists(self.options_file):
                try:
                    with open(self.options_file, "rb") as file:
                        return orjson.loads(file.read())
                except Exception as e:
                    print(f"Failed to load options: {e}. Using default options.")
                    return default_options
            else:
                print("Options file not found. Using default options.")
                return default_options

        def save_options(self):
            try:
                with open(self.options_file, "wb") as file:
                    file.write(orjson.dumps(self.options, option=orjson.OPT_INDENT_2))
                print("Options saved successfully.")
            except Exception as e:
                print(f"Failed to save options: {e}")

        def apply_options(self):
            theme = self.options.get("theme", "Default")
            print(f"Applying theme: {theme}")

            language = self.options.get("language", "English")
            print(f"Applying language: {language}")

            hide_launcher = self.options.get("hide_launcher", False)
            print(f"Hide launcher when game is running: {hide_launcher}")

        @staticmethod
        def download_file(url, save_dir):
            file_name = os.path.join(save_dir, url.split('/')[-1])

            if os.path.exists(file_name):
                print(f"File already exists: {file_name}")
                return

            try:
                response = requests.get(url)
                response.raise_for_status()

                os.makedirs(save_dir, exist_ok=True)

                with open(file_name, 'wb') as file:
                    file.write(response.content)
                print(f"Downloaded: {file_name}")

            except Exception as e:
                print(f"Failed to download {url}: {e}")

        @staticmethod
        def download_files():
            urls = [
                'https://raw.githubusercontent.com/Russiankids/Chompick/main/NormalnyChomik-ezgif.com-webp-to-png-converter.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/widgets.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/077bdfbf-0950-4e0d-bed2-5732339a1e6e.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/Modrinth_idja4akuiu_0.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/22410180.png',
                'https://raw.githubusercontent.com/Russiankids/Chompick/main/funny_82hiegE.mp3',
                'https://raw.githubusercontent.com/Russiankids/Chompick/main/settings.png',
                'https://raw.githubusercontent.com/Russiankids/Chompick/main/remove.png',
                'https://raw.githubusercontent.com/Russiankids/Chompick/main/add-button.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/explorer.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/fabric.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/forge.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/user.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/ezgif-6-0495bd1a5c.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/file_manager.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/finder.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/search-interface-symbol.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/rename.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/next.png',
                'https://raw.githubusercontent.com/Russiankids/DefLauncher/main/assets/back.png'

            ]
            pictures_dir = os.path.join(minecraft_directory, 'assets', 'icons')

            for url in urls:
                MinecraftLauncher.download_file(url, pictures_dir)

        def check_skin(self):
            nickname = self.username_input.text().strip()
            if not nickname:
                self.face_icon_button.setIcon(QIcon())
                return

            face_url = f"https://crafatar.com/avatars/{nickname}?size=32&overlay"
            try:
                response = requests.get(face_url)
                if response.status_code == 200:
                    pixmap = QPixmap()
                    pixmap.loadFromData(response.content)

                    face_icon = QIcon(pixmap)

                    self.face_icon_button.setIcon(face_icon)
                else:
                    self.face_icon_button.setIcon(QIcon())
            except requests.RequestException as e:
                self.face_icon_button.setIcon(QIcon())
                print(f"Error fetching skin: {e}")

        def check_java_installation(self):
            java_path = self.options.get("java_path", "")
            if java_path and os.path.exists(java_path):
                return True
            
            # Try to find Java in common locations
            common_paths = [
                os.path.join(os.environ.get("ProgramFiles", ""), "Java", "jdk-17", "bin", "java.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Java", "jdk-17", "bin", "java.exe"),
                os.path.join(os.environ.get("ProgramFiles", ""), "Java", "jre-17", "bin", "java.exe"),
                os.path.join(os.environ.get("ProgramFiles(x86)", ""), "Java", "jre-17", "bin", "java.exe"),
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    self.options["java_path"] = path
                    self.save_options()
                    return True
            
            return False

        def install_java(self):
            # Show Java installation options dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Java Installation Options")
            layout = QVBoxLayout()

            # Java version selection
            version_group = QGroupBox("Java Version")
            version_layout = QVBoxLayout()
            java_versions = {
                "Java 8": "https://download.oracle.com/java/8/latest/jdk-8_windows-x64_bin.exe",
                "Java 11": "https://download.oracle.com/java/11/latest/jdk-11_windows-x64_bin.exe",
                "Java 17": "https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe",
                "Java 21": "https://download.oracle.com/java/21/latest/jdk-21_windows-x64_bin.exe"
            }
            
            version_buttons = QButtonGroup()
            for version, url in java_versions.items():
                radio = QRadioButton(version)
                version_buttons.addButton(radio)
                version_layout.addWidget(radio)
            
            # Select Java 17 by default
            version_buttons.buttons()[2].setChecked(True)
            version_group.setLayout(version_layout)
            layout.addWidget(version_group)

            # Installation location
            location_group = QGroupBox("Installation Location")
            location_layout = QHBoxLayout()
            location_input = QLineEdit()
            location_input.setText(os.path.join(os.environ.get("ProgramFiles", ""), "Java"))
            location_layout.addWidget(location_input)
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(lambda: self.browse_java_location(location_input))
            location_layout.addWidget(browse_button)
            location_group.setLayout(location_layout)
            layout.addWidget(location_group)

            # Additional options
            options_group = QGroupBox("Additional Options")
            options_layout = QVBoxLayout()
            add_to_path = QCheckBox("Add Java to system PATH")
            add_to_path.setChecked(True)
            options_layout.addWidget(add_to_path)
            create_desktop_shortcut = QCheckBox("Create desktop shortcut")
            create_desktop_shortcut.setChecked(True)
            options_layout.addWidget(create_desktop_shortcut)
            options_group.setLayout(options_layout)
            layout.addWidget(options_group)

            # Buttons
            button_layout = QHBoxLayout()
            install_button = QPushButton("Install")
            cancel_button = QPushButton("Cancel")
            button_layout.addWidget(install_button)
            button_layout.addWidget(cancel_button)
            layout.addLayout(button_layout)

            dialog.setLayout(layout)

            # Connect signals
            install_button.clicked.connect(dialog.accept)
            cancel_button.clicked.connect(dialog.reject)

            if dialog.exec_() == QDialog.Accepted:
                # Get selected options
                selected_version = version_buttons.checkedButton().text()
                java_url = java_versions[selected_version]
                install_location = location_input.text()
                add_to_path_enabled = add_to_path.isChecked()
                create_shortcut = create_desktop_shortcut.isChecked()

                # Show installation progress
                progress_dialog = QProgressDialog("Installing Java...", "Cancel", 0, 100, self)
                progress_dialog.setWindowTitle("Java Installation")
                progress_dialog.setWindowModality(Qt.WindowModal)

                # Create installer instance
                installer = JavaInstaller(self)
                installer.set_installation_options(
                    java_url,
                    install_location,
                    add_to_path_enabled,
                    create_shortcut
                )
                
                installer.progress.connect(progress_dialog.setValue)
                installer.finished.connect(lambda success: self.on_java_install_finished(success, progress_dialog))
                installer.error.connect(lambda error: self.on_java_install_error(error, progress_dialog))
                
                installer.start()
                progress_dialog.exec_()
                
                return True
            return False

        def browse_java_location(self, location_input):
            directory = QFileDialog.getExistingDirectory(
                self,
                "Select Java Installation Directory",
                location_input.text(),
                QFileDialog.ShowDirsOnly
            )
            if directory:
                location_input.setText(directory)

        def on_java_install_finished(self, success, progress_dialog):
            progress_dialog.close()
            if success:
                QMessageBox.information(self, "Success", "Java has been installed successfully.")
            else:
                QMessageBox.warning(self, "Error", "Failed to install Java. Please install it manually.")

        def on_java_install_error(self, error, progress_dialog):
            progress_dialog.close()
            QMessageBox.critical(self, "Error", f"Failed to install Java: {error}")

    class SkinPreviewDialog(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.setWindowTitle("Skin Preview")
            self.setGeometry(100, 100, 400, 500)
            
            layout = QVBoxLayout()
            
            # Preview image
            self.preview_label = QLabel()
            self.preview_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(self.preview_label)
            
            # Skin type selection
            type_group = QGroupBox("Skin Type")
            type_layout = QVBoxLayout()
            self.type_combo = QComboBox()
            self.type_combo.addItems(["wide", "slim"])
            type_layout.addWidget(self.type_combo)
            type_group.setLayout(type_layout)
            layout.addWidget(type_group)
            
            # Buttons
            button_layout = QHBoxLayout()
            self.accept_button = QPushButton("Use This Skin")
            self.cancel_button = QPushButton("Cancel")
            button_layout.addWidget(self.accept_button)
            button_layout.addWidget(self.cancel_button)
            layout.addLayout(button_layout)
            
            self.setLayout(layout)
            
            # Connect signals
            self.accept_button.clicked.connect(self.accept)
            self.cancel_button.clicked.connect(self.reject)

        def set_preview(self, skin_path):
            pixmap = QPixmap(skin_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                self.preview_label.setPixmap(scaled_pixmap)

        def get_skin_type(self):
            return self.type_combo.currentText()

    class Skin3DPreviewWidget(QOpenGLWidget):
        def __init__(self, skin_path, parent=None):
            super().__init__(parent)
            self.skin_path = skin_path
            self.texture_id = None
            self.angle = 0
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.rotate)
            self.timer.start(30)  # ~33 FPS

        def initializeGL(self):
            glEnable(GL_DEPTH_TEST)
            glEnable(GL_TEXTURE_2D)
            self.texture_id = self.load_skin_texture(self.skin_path)

        def resizeGL(self, w, h):
            glViewport(0, 0, w, h)
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, w / h if h else 1, 0.1, 100.0)
            glMatrixMode(GL_MODELVIEW)

        def paintGL(self):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            glTranslatef(0, 0, -5)
            glRotatef(self.angle, 0, 1, 0)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            self.draw_player_model()

        def rotate(self):
            self.angle = (self.angle + 2) % 360
            self.update()

        def load_skin_texture(self, path):
            from PIL import Image
            img = Image.open(path).convert('RGBA').transpose(Image.FLIP_TOP_BOTTOM)
            img_data = np.array(img)
            texture_id = glGenTextures(1)
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, img.width, img.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
            return texture_id

        def draw_player_model(self):
            # Draw a simple player: head (cube), body (rect), arms/legs (rects)
            # For brevity, only the head is textured here. You can expand this for full body.
            glPushMatrix()
            # Head
            glTranslatef(0, 0.75, 0)
            self.draw_cube(1.0)
            glPopMatrix()
            # Body
            glPushMatrix()
            glScalef(0.75, 1.0, 0.4)
            glTranslatef(0, -0.25, 0)
            self.draw_cube(1.0)
            glPopMatrix()
            # Arms
            for x in [-0.65, 0.65]:
                glPushMatrix()
                glTranslatef(x, 0.25, 0)
                glScalef(0.25, 0.75, 0.25)
                self.draw_cube(1.0)
                glPopMatrix()
            # Legs
            for x in [-0.25, 0.25]:
                glPushMatrix()
                glTranslatef(x, -1.0, 0)
                glScalef(0.25, 0.75, 0.25)
                self.draw_cube(1.0)
                glPopMatrix()

        def draw_cube(self, size):
            # Draw a textured cube (for the head)
            hs = size / 2
            glBegin(GL_QUADS)
            # Front
            glTexCoord2f(0.125, 0.25); glVertex3f(-hs, -hs, hs)
            glTexCoord2f(0.25, 0.25); glVertex3f(hs, -hs, hs)
            glTexCoord2f(0.25, 0.375); glVertex3f(hs, hs, hs)
            glTexCoord2f(0.125, 0.375); glVertex3f(-hs, hs, hs)
            # ... (repeat for other faces, mapping skin texture coordinates)
            glEnd()

    if __name__ == "__main__":
        MinecraftLauncher.download_files()
        app = QApplication(sys.argv)
        splash = SplashScreen(splash_path)
        splash.show()
        time.sleep(3)
        main_window = MinecraftLauncher()
        splash.finish(main_window)
        main_window.show()
        sys.exit(app.exec_())
else:
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory().replace("minecraft", "deflauncher")
    splash_path = os.path.join(pictures_dir, "077bdfbf-0950-4e0d-bed2-5732339a1e6e.png")
    modrinth_path = os.path.join(pictures_dir, "Modrinth_idja4akuiu_0.png")
    modrinth_icon_path = os.path.join(pictures_dir, "22410180.png")
    sound_path = os.path.join(pictures_dir, "funny_82hiegE.mp3")
    explorer_path = os.path.join(pictures_dir, "explorer.png")
    fabric_path = os.path.join(pictures_dir, "fabric.png")
    forge_path = os.path.join(pictures_dir, "forge.png")
    save_icon_path = os.path.join(pictures_dir, "user.png")
    minecraft_icon_path = os.path.join(pictures_dir, "ezgif-6-0495bd1a5c.png")
    file_manager_path = os.path.join(pictures_dir, "file_manager.png")
    finder_path = os.path.join(pictures_dir, "finder.png")
    search_path = os.path.join(pictures_dir, "search-interface-symbol.png")
    back_path = os.path.join(pictures_dir, "back.png")
    next_path = os.path.join(pictures_dir, "next.png")
    rename_path = os.path.join(pictures_dir, "rename.png")
    add_button_path = os.path.join(pictures_dir, "add-button.png")
    remove_path = os.path.join(pictures_dir, "remove.png")

    class OptionsManager(QDialog):
        def __init__(self, parent=None):
            super().__init__(parent)
            self.parent = parent

        def init(self):
            self.setWindowTitle("Options")
            layout = QFormLayout(self)

            # Theme option
            theme_label = QLabel("UI Theme:")
            self.theme_input = QLineEdit()
            self.theme_input.setText(self.parent.options.get("theme", "Default"))
            self.theme_input.setPlaceholderText("Enter theme name")
            layout.addRow(theme_label, self.theme_input)

            # Language option
            lang_label = QLabel("Language:")
            self.lang_combo = QComboBox()
            self.lang_combo.addItems(["English", "Russian", "Spanish", "French"])
            self.lang_combo.setCurrentText(self.parent.options.get("language", "English"))
            layout.addRow(lang_label, self.lang_combo)

            # Java path option
            java_layout = QHBoxLayout()
            self.java_path_input = QLineEdit()
            self.java_path_input.setText(self.parent.options.get("java_path", ""))
            self.java_path_input.setPlaceholderText("Path to Java executable")
            java_layout.addWidget(self.java_path_input)
            
            browse_button = QPushButton("Browse")
            browse_button.clicked.connect(self.browse_java_path)
            java_layout.addWidget(browse_button)
            
            layout.addRow(QLabel("Java Path:"), java_layout)

            # Auto-install Java option
            self.auto_install_java_checkbox = QCheckBox("Automatically install Java if not found")
            self.auto_install_java_checkbox.setChecked(self.parent.options.get("auto_install_java", True))
            layout.addRow(self.auto_install_java_checkbox)

            # Hide launcher option
            self.hide_launcher_checkbox = QCheckBox("Hide launcher when game is running")
            self.hide_launcher_checkbox.setChecked(self.parent.options.get("hide_launcher", False))
            layout.addRow(self.hide_launcher_checkbox)

            # Save button
            save_button = QPushButton("Save Options")
            save_button.clicked.connect(self.save_options)
            layout.addRow(save_button)

            # Hamster image (for fun)
            self.hamster_label = QLabel(self)
            self.chompick_path = os.path.join(pictures_dir, 'NormalnyChomik-ezgif.com-webp-to-png-converter.png')
            try:
                self.hamster_label.setPixmap(QPixmap(self.chompick_path))
            except Exception as e:
                print(f"Error loading image: {e}")
                self.hamster_label.setText("Image not found")
            self.hamster_label.setAlignment(Qt.AlignRight | Qt.AlignBottom)
            self.hamster_label.mousePressEvent = self.hamster_clicked
            layout.addRow(self.hamster_label)

            self.setLayout(layout)

        def browse_java_path(self):
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Java Executable",
                "",
                "Executable Files (*.exe);;All Files (*)"
            )
            if file_path:
                self.java_path_input.setText(file_path)

        def save_options(self):
            theme_name = self.theme_input.text()
            language = self.lang_combo.currentText()
            hide_launcher = self.hide_launcher_checkbox.isChecked()
            java_path = self.java_path_input.text()
            auto_install_java = self.auto_install_java_checkbox.isChecked()

            valid_themes = ["Default", "Dark", "Light"]
            if theme_name not in valid_themes:
                QMessageBox.warning(self, "Invalid Theme", f"Theme '{theme_name}' is not valid.")
                return

            # Update the parent's options
            self.parent.options = {
                "theme": theme_name,
                "language": language,
                "hide_launcher": hide_launcher,
                "java_path": java_path,
                "auto_install_java": auto_install_java
            }

            # Save options using orjson
            try:
                with open(self.parent.options_file, "wb") as file:
                    file.write(orjson.dumps(self.parent.options, option=orjson.OPT_INDENT_2))
                QMessageBox.information(self, "Options Saved", "Settings have been saved.")
                self.play_funny_sound()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save options: {e}")

        def hamster_clicked(self, event):
            if event.button() == Qt.LeftButton:
                self.play_funny_sound()

        def play_funny_sound(self):
            try:
                pygame.mixer.init()
                if hasattr(self, 'sound') and self.sound.get_busy():
                    self.sound.stop()
                self.sound = pygame.mixer.Sound(sound_path)
                self.sound.play()
            except Exception as e:
                print(f"Error playing sound: {e}")

        def show_options_dialog(self):
            self.init()
            self.exec_()

    class MinecraftLauncher(QWidget):
        def __init__(self):
            super().__init__()
            self.translator = QTranslator()

            self.setWindowTitle("DefLauncher 0.8 OFFLINE")
            self.setGeometry(300, 300, 700, 700)
            self.setWindowIcon(QIcon(splash_path))

            ProfileManagement = "Profile Management"

            self.profiles_file = os.path.join(minecraft_directory, "profiles.json")
            self.options_file = os.path.join(minecraft_directory, "options.json")
            self.options = self.load_options()
            self.profiles = self.load_profiles()
            self.apply_options()

            self.options_manager = OptionsManager(self)

            main_layout = QVBoxLayout()

            profile_group = QGroupBox(self.tr(ProfileManagement))
            profile_layout = QFormLayout()

            self.profile_combo = QComboBox(self)
            self.profile_combo.addItems(self.profiles.keys())
            self.profile_combo.currentTextChanged.connect(self.update_profile_ui)
            profile_layout.addRow(QLabel(self.tr("Profile:")), self.profile_combo)

            button_layout = QHBoxLayout()
            self.rename_profile_button = QPushButton(self.tr("Rename"))
            self.rename_profile_button.setIcon(QIcon(rename_path))
            self.rename_profile_button.setIconSize(QSize(16, 16))
            self.rename_profile_button.clicked.connect(self.rename_profile)
            button_layout.addWidget(self.rename_profile_button)
            self.new_profile_button = QPushButton(self.tr("New"))
            self.new_profile_button.setIcon(QIcon(add_button_path))
            self.new_profile_button.setIconSize(QSize(16, 16))
            self.new_profile_button.clicked.connect(self.create_new_profile)
            button_layout.addWidget(self.new_profile_button)
            self.delete_profile_button = QPushButton(self.tr("Delete"))
            self.delete_profile_button.setIcon(QIcon(remove_path))
            self.delete_profile_button.setIconSize(QSize(16, 16))
            self.delete_profile_button.clicked.connect(self.delete_profile)
            button_layout.addWidget(self.delete_profile_button)

            profile_layout.addRow(button_layout)
            profile_group.setLayout(profile_layout)
            main_layout.addWidget(profile_group)

            user_group = QGroupBox(self.tr("User Details"))
            user_layout = QFormLayout()

            self.username_input = QLineEdit(self)
            user_layout.addRow(QLabel(self.tr("Username:")), self.username_input)

            user_group.setLayout(user_layout)
            main_layout.addWidget(user_group)

            config_group = QGroupBox("Minecraft Configuration")
            config_layout = QFormLayout()

            self.version_combo = QComboBox(self)
            self.version_combo.addItems([version["id"] for version in minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)])
            config_layout.addRow(QLabel("Minecraft Version:"), self.version_combo)

            config_group.setLayout(config_layout)
            main_layout.addWidget(config_group)

            actions_group = QGroupBox("Actions")
            actions_layout = QVBoxLayout()

            self.launch_button = QPushButton("Play",
                                             self)
            self.launch_button.setIconSize(QSize(32, 32))
            self.launch_button.clicked.connect(self.launch_minecraft)
            self.launch_button.setStyleSheet("""
                        QPushButton {
                            font-size: 16px;
                            padding: 10px;
                            border: none;
                            background-color: #4CAF50;
                            color: white;
                            border-radius: 8px;
                        }
                        QPushButton:hover {
                            background-color: #45a049;
                        }
                    """)
            actions_layout.addWidget(self.launch_button)

            self.save_profile_button = QPushButton("Save Profile")
            self.save_profile_button.setIcon(QIcon(save_icon_path))
            self.save_profile_button.setIconSize(QSize(16, 16))
            self.save_profile_button.clicked.connect(self.save_profile)
            actions_layout.addWidget(self.save_profile_button)

            self.open_launcher_dir_button = QPushButton("Open Launcher Directory")
            self.open_launcher_dir_button.setIcon(QIcon(explorer_path))
            self.open_launcher_dir_button.setIconSize(QSize(16, 16))
            self.open_launcher_dir_button.clicked.connect(self.open_launcher_directory)
            actions_layout.addWidget(self.open_launcher_dir_button)

            self.open_mod_folder_button = QPushButton("Open Mods Folder")
            self.open_mod_folder_button.setIcon(QIcon(explorer_path))
            self.open_mod_folder_button.setIconSize(QSize(16, 16))
            self.open_mod_folder_button.clicked.connect(self.open_mods_folder)
            actions_layout.addWidget(self.open_mod_folder_button)

            self.options_button = QPushButton("Options")
            options = os.path.join(pictures_dir, "settings.png")
            options_icon = QIcon(options)
            self.options_button.setIcon(options_icon)
            self.options_button.setIconSize(QSize(16, 16))
            self.options_button.clicked.connect(self.options_manager.show_options_dialog)
            actions_layout.addWidget(self.options_button)

            actions_group.setLayout(actions_layout)
            main_layout.addWidget(actions_group)

            self.setLayout(main_layout)
            self.update_profile_ui()

        def delete_profile(self):
            profile_name = self.profile_combo.currentText()
            if not profile_name:
                QMessageBox.warning(self, "No Profile Selected", "Please select a profile to delete.")
                return
            elif profile_name == "Default":
                QMessageBox.critical(self, "Cannot Delete Profile", "You cannot delete the default profile.")
                return

            reply = QMessageBox.question(self, 'Delete Profile', f'Are you sure you want to delete "{profile_name}"?',
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

            if reply == QMessageBox.Yes:
                del self.profiles[profile_name]
                self.save_profiles()
                self.profile_combo.clear()
                self.profile_combo.addItems(self.profiles.keys())
                if self.profile_combo.count() > 0:
                    self.profile_combo.setCurrentIndex(0)
                else:
                    self.username_input = "Player"
                    self.version_combo.setCurrentText(minecraft_launcher_lib.utils.get_installed_versions[0])


        def update_profile_ui(self):
            profile_name = self.profile_combo.currentText()
            profile = self.profiles.get(profile_name, {})
            self.username_input.setText(profile.get("username", "Player"))
            self.version_combo.setCurrentText(profile.get("version", "latest"))

        def save_profile(self):
            profile_name = self.profile_combo.currentText()
            self.profiles[profile_name] = {
                "username": self.username_input.text(),
                "version": self.version_combo.currentText(),
            }
            self.save_profiles()
            QMessageBox.information(self, "Profile Saved", f"Profile '{profile_name}' has been saved.")

        def rename_profile(self):
            profile_name = self.profile_combo.currentText()
            new_name, ok = QInputDialog.getText(self, "Rename Profile", "Enter new profile name:")
            if ok and new_name:
                self.profiles[new_name] = self.profiles.pop(profile_name)
                self.save_profiles()
                self.profile_combo.clear()
                self.profile_combo.addItems(self.profiles.keys())
                self.profile_combo.setCurrentText(new_name)

        def create_new_profile(self):
            new_name, ok = QInputDialog.getText(self, "New Profile", "Enter profile name:")
            if ok and new_name:
                self.profiles[new_name] = {"username": "Player", "version": "latest", "modloader": "Vanilla"}
                self.save_profiles()
                self.profile_combo.addItem(new_name)
                self.profile_combo.setCurrentText(new_name)

        def open_mods_folder(self):
            try:
                os.startfile(mods_directory) if os.name == "nt" else subprocess.call(["open", mods_directory])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open mods folder: {e}")

        def open_launcher_directory(self):
            try:
                os.startfile(minecraft_directory) if os.name == "nt" else subprocess.call(["open", minecraft_directory])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open launcher directory: {e}")

        def load_profiles(self):
            if os.path.exists(self.profiles_file):
                with open(self.profiles_file, "rb") as file:
                    return orjson.loads(file.read())
            return {"Default": {"username": "Player", "version": "latest", "modloader": "Vanilla"}}

        def save_profiles(self):
            try:
                os.makedirs(os.path.dirname(self.profiles_file), exist_ok=True)
                with open(self.profiles_file, "wb") as file:
                    file.write(orjson.dumps(self.profiles, option=orjson.OPT_INDENT_2))
                print("Profiles saved successfully.")
            except Exception as e:
                print(f"Failed to save profiles: {e}")

        def launch_minecraft(self):
            try:
                # Check for Java installation
                if not self.check_java_installation():
                    if not self.install_java():
                        return

                profile_name = self.profile_combo.currentText()
                selected_version = self.version_combo.currentText()
                selected_modloader = self.modloader_combo.currentText()

                # Get all installed Minecraft versions
                all_versions = minecraft_launcher_lib.utils.get_installed_versions(minecraft_directory)
                valid_versions = [v['id'] for v in all_versions]

                # Determine the version to launch based on modloader
                version_to_launch = selected_version  # Default to vanilla
                forge_version = None

                # Handle Forge-specific logic
                if selected_modloader == "Forge":
                    forge_versions = minecraft_launcher_lib.forge.find_forge_version(selected_version)
                    if not forge_versions:
                        QMessageBox.critical(self, "Error", f"No Forge version found for {selected_version}")
                        return
                    forge_version = forge_versions[0]  # Take the first available Forge version
                    version_to_launch = f"{selected_version}-forge-{forge_version}"

                # Handle Fabric-specific logic
                elif selected_modloader == "Fabric":
                    try:
                        fabric_versions = minecraft_launcher_lib.fabric.get_all_minecraft_versions()
                        if selected_version not in [v['version'] for v in fabric_versions]:
                            QMessageBox.critical(self, "Error", f"Fabric doesn't support {selected_version}")
                            return
                        loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()
                        version_to_launch = f"fabric-loader-{loader_version}-{selected_version}"
                        
                        # Ensure Fabric is installed
                        if not minecraft_launcher_lib.fabric.is_fabric_installed(version_to_launch, minecraft_directory):
                            QMessageBox.critical(self, "Error", "Fabric is not installed. Please install it first.")
                            return
                    except Exception as e:
                        QMessageBox.critical(self, "Error", f"Failed to initialize Fabric: {e}")
                        return

                # Validate that the determined version is installed
                if version_to_launch not in valid_versions:
                    QMessageBox.critical(self, "Error", f"Version {version_to_launch} is not installed. Please install it first.")
                    return

                # Set up mods directory for Fabric and ensure it exists
                mods_folder = os.path.join(minecraft_directory, profile_name, "mods")
                if selected_modloader == "Fabric":
                    os.makedirs(mods_folder, exist_ok=True)

                # Prepare launch options without JVM arguments
                options = {
                    "username": self.username_input.text(),
                    "uuid": "dummy-uuid",
                    "token": "dummy-token",
                    "javaPath": self.options.get("java_path", "")
                }

                # Generate and execute the Minecraft command
                minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(
                    version_to_launch, minecraft_directory, options
                )
                
                # Hide launcher if option is enabled
                if self.options.get("hide_launcher", False):
                    self.hide()
                
                # Launch Minecraft with proper error handling
                process = subprocess.Popen(
                    minecraft_command,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # Wait for the process to complete
                stdout, stderr = process.communicate()
                
                # Show launcher again after game closes
                if self.options.get("hide_launcher", False):
                    self.show()
                    
                # Check if there were any errors
                if process.returncode != 0:
                    error_message = f"Failed to launch Minecraft (Exit code: {process.returncode})"
                    if stderr:
                        error_message += f"\n\nError output:\n{stderr}"
                    QMessageBox.critical(self, "Error", error_message)
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to launch Minecraft: {e}")
                if self.options.get("hide_launcher", False):
                    self.show()

        def load_options(self):
            default_options = {
                "theme": "Default",
                "language": "English",
                "hide_launcher": False
            }

            if os.path.exists(self.options_file):
                try:
                    with open(self.options_file, "rb") as file:
                        return orjson.loads(file.read())
                except Exception as e:
                    print(f"Failed to load options: {e}. Using default options.")
                    return default_options
            else:
                print("Options file not found. Using default options.")
                return default_options

        def save_options(self):
            try:
                with open(self.options_file, "wb") as file:
                    file.write(orjson.dumps(self.options, option=orjson.OPT_INDENT_2))
                print("Options saved successfully.")
            except Exception as e:
                print(f"Failed to save options: {e}")

        def apply_options(self):
            theme = self.options.get("theme", "Default")
            print(f"Applying theme: {theme}")

            language = self.options.get("language", "English")
            print(f"Applying language: {language}")

            hide_launcher = self.options.get("hide_launcher", False)
            print(f"Hide launcher when game is running: {hide_launcher}")

    if __name__ == "__main__":
        app = QApplication(sys.argv)
        time.sleep(3)
        main_window = MinecraftLauncher()
        main_window.show()
        sys.exit(app.exec_())
