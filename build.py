import os
import subprocess
import sys

def build():
    # Install dependencies just in case
    subprocess.run([sys.executable, "-m", "pip", "install", "nicegui", "playwright", "pyinstaller"])
    
    # Run PyInstaller
    # --onefile: single executable
    # --windowed: no console window
    # --add-data: include nicegui static files
    import nicegui
    nicegui_path = os.path.dirname(nicegui.__file__)
    
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "ArXivDownloader",
        f"--add-data={nicegui_path}{os.pathsep}nicegui",
        "app.py"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd)

if __name__ == "__main__":
    build()
