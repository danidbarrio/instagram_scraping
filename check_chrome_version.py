import subprocess
import time
import winreg
import pyautogui

def get_chrome_version_and_uninstall_path():
    try:
        registry_path = r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Google Chrome"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
            version = winreg.QueryValueEx(key, "DisplayVersion")[0]
            uninstall_string = winreg.QueryValueEx(key, "UninstallString")[0]
            return version, uninstall_string
    except Exception as e:
        print(f"Error accessing the registry for Google Chrome: {e}")
        return None, None

def uninstall_chrome(uninstall_string):
    try:
        subprocess.run(uninstall_string, check=True)
        time.wait(1)
        pyautogui.press('enter')
        print("Google Chrome successfully uninstalled.")
    except Exception as e:
        print(f"Error uninstalling Google Chrome: {e}")

def install_chrome(installer_path):
    try:
        subprocess.run(installer_path, check=True)
        print("Google Chrome successfully installed.")
    except Exception as e:
        print(f"Error installing Google Chrome: {e}")

if __name__ == "__main__":
    version, uninstall_string = get_chrome_version_and_uninstall_path()
    
    if version:
        major_version = int(version.split('.')[0])
    else:
        major_version = 0
    
    if major_version > 114:
        if uninstall_string:
            uninstall_chrome(uninstall_string)
        #install_chrome(installer_path)
    else:
        print("No action required. Google Chrome version is 114 or below.")


