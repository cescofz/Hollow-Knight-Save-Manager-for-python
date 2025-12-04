from PyQt5.QtWidgets import *
import re
import sys
import os
import winreg
import configparser
from start import *


class find(QDialog, Ui_Dialog):
    def __init__(self):
        super(find, self).__init__()
        self.setupUi(self)
        self.config = configparser.ConfigParser()
        self.config['Location'] = {}
        self.config["SaveLocaltion"] = {}
        self.find_game()
        self.get_savefilelist()
        with open("config.ini", "w", encoding="utf-8") as f:
            self.config.write(f)

        self.comboBox.currentTextChanged.connect(self.set_current_save)
        self.lab_game_path.setWordWrap(True)
        self.buttonBox.accepted.connect(self.on_accepted)
        self.show()

    def on_accepted(self):
        if self.find_game != None and self.get_savefilelist != None:
            from main import HKS
            self.close()
            main_window = HKS()
            main_window.show()
        else:
            QMessageBox.critical(self, "Error:", "找不到存档文件或游戏未安装!")
            return 0

    def get_savefilelist(self):
        save_list = []
        try:
            save_path = os.environ["LOCALAPPDATA"] + "\\..\\LocalLow\\Team Cherry\\Hollow Knight"
            self.lab_savefolder.setText(save_path)
            self.lab_savefolder.setWordWrap(True)
            file_list = os.listdir(save_path)
            pattern = re.compile(r'^user\d+\.dat$')
            matches = [file for file in file_list if pattern.match(file)]
            for file in matches:
                save_list.append(file)
                self.comboBox.addItem(file)
            self.config["SaveLocaltion"]["savepath"] = save_list[0]
            return save_list
        except:
            self.lab_savefolder.setText("存档未找到！")
            return None

    def set_current_save(self):
        self.config["SaveLocaltion"]["savepath"] = self.comboBox.currentText()
        with open("config.ini", "w", encoding="utf-8") as f:
            self.config.write(f)

    def find_game(self):
        reg_paths = [
            # 64位系统注册表路径（32位程序）
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 367520",
            # 32位系统/64位程序注册表路径
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\Steam App 367520"
        ]
        game_path = None
        try:
            for reg_path in reg_paths:
                try:
                    key = winreg.OpenKey(
                        winreg.HKEY_LOCAL_MACHINE,
                        reg_path,
                        0,
                        winreg.KEY_READ | winreg.KEY_WOW64_64KEY  # 兼容64位系统
                    )
                    value, reg_type = winreg.QueryValueEx(key, "InstallLocation")
                    if os.path.isdir(value):
                        game_path = value.strip()
                        winreg.CloseKey(key)
                        break
                    winreg.CloseKey(key)
                except FileNotFoundError:
                    continue
                except PermissionError:
                    self.lab_gameinstall_state.setText("权限不足，请用管理员身份运行重试！")
                    raise PermissionError("Permission denied")
                except Exception as e:
                    self.lab_gameinstall_state.setText("错误")
                    raise RuntimeError("Failed")
            if not game_path:
                self.lab_gameinstall_state.setText("未找到")
                raise FileNotFoundError("Not Found Game!")
            self.lab_game_path.setText(game_path)
            self.lab_gameinstall_state.setText("已找到")
            self.config['Location']['GamePath'] = game_path
            with open("config.ini", 'w', encoding='utf-8') as f:
                self.config.write(f)
            return game_path
        except Exception as e:
            print(f"查找游戏失败：{str(e)}")
            return None


if __name__ == "__main__":
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    find = find()
    app.exec_()
