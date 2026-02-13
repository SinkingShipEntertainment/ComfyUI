import logging
import os
import signal
import socket
import subprocess
import sys
import webbrowser

# from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QObject, QTimer, QSharedMemory
from PySide6.QtGui import QIcon, QAction
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu

# Traditional print() statements were silently erroring if the original
# terminal gets closed. This is because that prints to sys.stdout, whose file
# descriptor disappears when the terminal gets closed. The logging module
# with a modified emit method lets us intercept and ignore such cases.
class SafeStreamHandler(logging.StreamHandler):
    def emit(self, record):
        try:
            super().emit(record)
        except (BrokenPipeError, OSError):
            pass  # Ignore if terminal closed

logger = logging.getLogger("comfy_tray")
logger.setLevel(logging.INFO)
handler = SafeStreamHandler(sys.stdout)
handler.setLevel(logging.INFO)
logger.addHandler(handler)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICON_PATH = os.path.join(BASE_DIR, "tray_icon.ico")
COMFY_PATH = os.path.join(BASE_DIR, "main.py")
LOCAL_MODELS = os.path.expanduser("~/comfyui/models")
GLOBAL_MODELS = "/mnt/vfx/projects/SSELibrary/work/comfyui/models"


class ComfyTray:

    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.shared_memory = QSharedMemory("comfyui_tray_lock")
        if self.shared_memory.attach():
            logger.info("Already running.")
            sys.exit(0)

        if not self.shared_memory.create(1):
            logger.info("Already running.")
            sys.exit(0)

        self.worker = None
        self.tray = QSystemTrayIcon(self.app)
        self.tray.setIcon(QIcon(ICON_PATH))
        self.tray.setVisible(True)

        self.open_tab_action = QAction("New ComfyUI Tab")
        self.browse_local_models_action = QAction("Browse Local Models")
        self.browse_global_models_action = QAction("Browse Global Models")
        self.restart_action = QAction("Restart ComfyUI")
        self.quit_action = QAction("Quit")

        self.open_tab_action.triggered.connect(self.open_browser)
        self.browse_local_models_action.triggered.connect(lambda: self.open_folder(LOCAL_MODELS))
        self.browse_global_models_action.triggered.connect(lambda: self.open_folder(GLOBAL_MODELS))
        self.restart_action.triggered.connect(self.restart_comfy)
        self.quit_action.triggered.connect(self.quit_app)

        self.menu = QMenu()
        self.menu.addAction(self.open_tab_action)
        self.menu.addAction(self.browse_local_models_action)
        self.menu.addAction(self.browse_global_models_action)
        self.menu.addAction(self.restart_action)
        self.menu.addSeparator()
        self.menu.addAction(self.quit_action)
        self.tray.setContextMenu(self.menu)

        self.start_comfy(auto_launch=True)

        # Monitor if comfy crashes
        self.monitor_timer = QTimer()
        self.monitor_timer.timeout.connect(self.check_worker)
        self.monitor_timer.start(5000)

    def is_port_open(self, host="127.0.0.1", port=8188):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.5)
            return sock.connect_ex((host, port)) == 0

    def check_worker(self):
        if self.worker and self.worker.poll() is not None:
            self.tray.setToolTip("ComfyUI: Disconnected")

    def check_if_ready(self):
        if self.is_port_open():
            self.tray.setToolTip("ComfyUI: Connected")
            self.launch_timer.stop()

    def start_comfy(self, auto_launch=False):

        logger.info("Starting ComfyUI...")
        self.tray.setToolTip("ComfyUI: Starting...")

        cmd_list = ["python3", COMFY_PATH, "--base-directory", "~/comfyui"]
        if auto_launch:
            cmd_list.append("--auto-launch")

        self.worker = subprocess.Popen(
            cmd_list,
            stdout=sys.stdout,
            stderr=sys.stderr
        )

        # Start polling for readiness
        self.launch_timer = QTimer()
        self.launch_timer.timeout.connect(self.check_if_ready)
        self.launch_timer.start(1000)  # check every second

    def open_browser(self):
        url = "http://127.0.0.1:8188"
        webbrowser.open(url)

    def open_folder(self, folder_path):

        if not os.path.exists(folder_path):
            logger.info("Folder does not exist: %s" % folder_path)
            return

        try:
            subprocess.run(["xdg-open", folder_path], check=False)
        except Exception as e:
            logger.info("Failed to open folder: %s" % e)

    def stop_comfy(self):
        if self.worker and self.worker.poll() is None:
            logger.info("Stopping ComfyUI...")

            self.worker.send_signal(signal.SIGINT)  # mimic Ctrl+C
            try:
                self.worker.wait(timeout=10)
            except subprocess.TimeoutExpired:
                logger.info("Force killing ComfyUI...")
                self.worker.kill()

    def restart_comfy(self):
        self.stop_comfy()
        self.start_comfy()

    def quit_app(self):
        self.stop_comfy()
        self.tray.hide()
        self.app.quit()

    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    tray = ComfyTray()
    tray.run()
