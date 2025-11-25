'''
PyQt5开发的Hollow Knight存档编辑器
加密和解密方法来自[@KayDeeTee](https://github.com/KayDeeTee)'s [Hollow Knight Save Manager](https://github.com/KayDeeTee/Hollow-Knight-SaveManager).
'''
import sys
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from PyQt5.QtWidgets import QApplication,QMainWindow,QFileDialog,QMessageBox
from PyQt5.Qt import QTimer
from PyQt5 import QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer,QMediaContent
from UI import Ui_MainWindow
import os
import shutil
import json
import subprocess

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
class HKS(QMainWindow,Ui_MainWindow):
    C_SHARP_HEADER = bytes([0, 1, 0, 0, 0, 255, 255, 255, 255, 1, 0, 0, 0, 0, 0, 0, 0, 6, 1, 0, 0, 0])
    AES_KEY = b'UKu52ePUBwetZ9wNX88o54dnfKRu0T1l'
    ECB_CIPHER = AES.new(AES_KEY, AES.MODE_ECB)
    def __init__(self):
        super(HKS, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("Hollow Knight(空洞骑士)存档修改器           by Sky.柚子")
        self.setWindowIcon(QIcon(resource_path("res/image/icon.ico")))
        self.show()
        self.main()
    def string_to_bytes(self,s: str) -> bytes:
        """将字符串转换为字节序列"""
        return s.encode('utf-8')
    def bytes_to_string(self,b: bytes) -> str:
        """将字节序列转换为字符串"""
        return b.decode('utf-8')
    def aes_decrypt(self,data: bytes) -> bytes:
        """AES解密并移除PKCS7填充"""
        decrypted = self.ECB_CIPHER.decrypt(data)
        return unpad(decrypted, AES.block_size)
    def aes_encrypt(self,data: bytes) -> bytes:
        """添加PKCS7填充并进行AES加密"""
        padded = pad(data, AES.block_size)
        return self.ECB_CIPHER.encrypt(padded)
    def generate_length_prefixed_string(self,length: int) -> bytes:
        """生成长度前缀字符串（遵循MSDN规范）"""
        length = min(0x7FFFFFFF, length)
        bytes_list = []
        for _ in range(4):
            if length >> 7 != 0:
                bytes_list.append((length & 0x7F) | 0x80)
                length >>= 7
            else:
                bytes_list.append(length & 0x7F)
                length >>= 7
                break
        if length != 0:
            bytes_list.append(length)
        return bytes(bytes_list)
    def add_header(self,data: bytes) -> bytes:
        """为数据添加文件头"""
        length_data = self.generate_length_prefixed_string(len(data))
        total_length = len(self.C_SHARP_HEADER) + len(length_data) + len(data) + 1
        result = bytearray(total_length)
        result[:len(self.C_SHARP_HEADER)] = self.C_SHARP_HEADER
        result[len(self.C_SHARP_HEADER):len(self.C_SHARP_HEADER) + len(length_data)] = length_data
        result[len(self.C_SHARP_HEADER) + len(length_data):-1] = data
        result[-1] = 11  # 固定结尾字节
        return bytes(result)
    def remove_header(self,data: bytes) -> bytes:
        data = data[len(self.C_SHARP_HEADER):-1]
        length_count = 0
        for i in range(5):
            length_count += 1
            if (data[i] & 0x80) == 0:
                break
        return data[length_count:]
    def decode_save_file(self,data: bytes) -> str:
        """解密存档文件并返回JSON字符串"""
        data = self.remove_header(data)
        data = base64.b64decode(data)
        data = self.aes_decrypt(data)
        return self.bytes_to_string(data)
    def encode_to_pc_save(self,json_str: str) -> bytes:
        """将JSON字符串编码为PC版存档文件"""
        data = self.string_to_bytes(json_str)
        data = self.aes_encrypt(data)
        data = base64.b64encode(data)
        return self.add_header(data)
    def hash_string(self,s: str) -> int:
        """计算字符串的哈希值（对应原Hash函数）"""
        result = 0
        for c in s:
            result = ((result << 5) - result) + ord(c)
        return result
    def play_background_music(self):
        self.player = QMediaPlayer()
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(resource_path("res/audio/back.mp3"))))
        self.player.setVolume(50)
        self.player.stateChanged.connect(self.on_player_state_changed)
        self.player.play()
    def on_player_state_changed(self, state):
        if state == QMediaPlayer.StoppedState:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(resource_path("res/audio/back.mp3"))))
            self.player.play()
    def read_json(self):
        with open("user_data.json","r") as f:
            data = json.loads(f.read())
            f.close()
        return data
    def read_save(self):
        save_dir = os.environ["LOCALAPPDATA"]+"\\..\\LocalLow\\Team Cherry\\Hollow Knight\\user1.dat"
        if os.path.exists(save_dir):
            self.lab_savepath.setText(save_dir)
            print(save_dir)
            shutil.copyfile(save_dir, "./bkp_user1.dat")
            self.textEdit_log.append(f"读取存档:已生成备份存档文件到当前目录{os.getcwd()}\\bkp_user1.dat")
            with open(save_dir, "rb") as f:
                pc_save_data = f.read()
            self.textEdit_log.append("读取存档:开始解码")
            json_data = self.decode_save_file(pc_save_data)
            with open("user_data.json", "w") as f:
                f.write(json_data)
                f.close()
            self.textEdit_log.append(f"读取存档:解码数据成功，已写入玩家数据到{os.getcwd()}\\user_data.json")
            self.btn_flash.show()
            with open("user_data.json","r") as f:
                json_data = json.loads(f.read())
                f.close()
            self.flash_data(json_data)
    def flash_data(self,json_data):
        self.lab_geo.setText(str(json_data["playerData"]["geo"]))
        self.lab_health.setText(str(json_data["playerData"]["health"]))
        self.lab_maxhelath.setText(str(json_data["playerData"]["maxHealth"]))
        self.lab_mp.setText(str(json_data["playerData"]["MPCharge"]))
        self.lab_maxmp.setText(str(json_data["playerData"]["maxMP"]))
        self.lab_nailDamage.setText(str(json_data["playerData"]["nailDamage"]))
        self.lab_nailupdate.setText(str(json_data["playerData"]["nailSmithUpgrades"]))
        self.textEdit_log.append("读取存档:从userdata.json读取成功！刷新完成")
    def change_json_file(self,k,v):
        with open("user_data.json", "r") as f:
            json_data = json.loads(f.read())
        json_data["playerData"][k] = v
        with open("user_data.json","w") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            f.close()
    def changeGeo(self):
        v = int(self.lineEdit_Geo.text())
        self.textEdit_log.append(f"存档修改:已修改Geo={v}到userdata.json!")
        self.change_json_file("geo",v)
    def changeHelath(self):
        v = v = int(self.lineEdit_Health.text())
        self.textEdit_log.append(f"存档修改:已修改health={v}到userdata.json!")
        self.change_json_file("health",v)
    def changeMaxHealth(self):
        v = v = int(self.lineEdit_MaxHelath.text())
        self.textEdit_log.append(f"存档修改:已修改maxHealth={v}到userdata.json!")
        self.change_json_file("maxHealth",v)
    def changeMP(self):
        v = v = int(self.lineEdit_mp.text())
        self.textEdit_log.append(f"存档修改:已修改MP(灵魂)={v}到userdata.json!")
        self.change_json_file("MPCharge",v)
    def changeMaxMP(self):
        v = v = int(self.lineEdit_MaxMp.text())
        self.textEdit_log.append(f"存档修改:已修改MaxMP(最大灵魂上限)={v}到userdata.json!")
        self.change_json_file("maxMP",v)
    def changenailDamage(self):
        v = v = int(self.lineEdit_nailDamage.text())
        self.textEdit_log.append(f"存档修改:已修改nailDamage(骨钉攻击力)={v}到userdata.json!")
        self.change_json_file("nailDamage",v)
    def changenailDamageupdate(self):
        v = v = int(self.lineEdit_nailDamage_update.text())
        self.textEdit_log.append(f"存档修改:已修改nailSmithUpgrades(骨钉升级次数)={v}到userdata.json!")
        self.change_json_file("nailSmithUpgrades",v)
    def saveas_file(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getSaveFileName(self, "另存为", "user1.dat", "存档文件 (*.dat);", options=options)
        if fileName:
            if not os.path.exists("user_data.json"):
                self.textEdit_log.append("都没有userdata.json我咋给你另存为？")
                return
            try:
                with open("user_data.json", "r", encoding="utf-8") as f:
                    json_str = f.read()
                save_data = self.encode_to_pc_save(json_str)
                with open(fileName, "wb") as f:
                    f.write(save_data)
                self.textEdit_log.append(f"存档另存为:存档已成功另存为到：{fileName}")
            except Exception as e:
                self.textEdit_log.append(f"存档另存为:另存为失败：{str(e)}")
    def opendatajson(self):
        state = subprocess.run("notepad user_data.json")
        return
    def encoder_save(self):
        save_dir = os.environ["LOCALAPPDATA"] + "\\..\\LocalLow\\Team Cherry\\Hollow Knight\\user1.dat"
        if os.path.exists("user_data.json") and os.path.exists(save_dir):
            self.read_json()
            self.textEdit_log.append("存档编译:已读取到userdata.json,开始编译...")
            pc_save = self.encode_to_pc_save(json.dumps(self.read_json(),indent=2))
            with open("user1.dat","wb") as f:
                f.write(pc_save)
                self.textEdit_log.append("存档编译:完成")
                f.close()
            self.msg = QMessageBox()
            self.msg.setWindowTitle("询问？")
            self.msg.setText("是否替换原有存档?")
            self.msg.setIcon(QMessageBox.Question)
            self.msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            result = self.msg.exec_()
            if result == QMessageBox.Yes:
                shutil.copyfile("./user1.dat",save_dir)
                self.textEdit_log.append("存档编译:已替换存档")
            else:
                self.textEdit_log.append("存档编译:未替换存档")
        else:
            self.textEdit_log.append("编译存档:没有生成userdata.json,你编译个几把?")
    def main(self):
        self.btn_flash.hide()
        self.play_background_music()
        self.textEdit_log.setReadOnly(True)
        self.btn_readsave.clicked.connect(self.read_save)
        self.btn_openuserdata.clicked.connect(self.opendatajson)
        self.btn_saveas.clicked.connect(self.saveas_file)
        self.btn_change_geo.clicked.connect(self.changeGeo)
        self.btn_change_health.clicked.connect(self.changeHelath)
        self.btn_change_maxhealth.clicked.connect(self.changeMaxHealth)
        self.btn_change_mp.clicked.connect(self.changeMP)
        self.btn_change_maxmp.clicked.connect(self.changeMaxMP)
        self.btn_change_nailDamage.clicked.connect(self.changenailDamage)
        self.btn_change_nailDamageupdate.clicked.connect(self.changenailDamageupdate)
        self.btn_flash.clicked.connect(lambda: self.flash_data(self.read_json()))
        self.btn_encode.clicked.connect(self.encoder_save)
if __name__ == '__main__':
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    hksm = HKS()
    app.exec_()