# Hollow-Knight-Save-Manager-for-python
# V1.0.2
# By Sky.柚子
## PyQt5编写的空洞骑士存档编辑器，可以将dat存档文件解码为json文件
### 加密和解密方法来自[@KayDeeTee](https://github.com/KayDeeTee)'s [Hollow Knight Save Manager](https://github.com/KayDeeTee/Hollow-Knight-SaveManager). 

### 说明
1. 在使用前建议先手动备份您的 "%LOCALAPPDATA%Low\Team Cherry目录
2. 请使用Steam正版空洞骑士客户端，否则找不到游戏
3. 请将exe可执行文件放到独立文件夹内运行
4. 不要删除文件夹内的config.ini
5. 初次使用务必先读取存档
6. 此程序会在运行目录生成存放存档信息的json文件，您可以按照喜好随意更改
### 已知问题
1.主程序记事打开userdata.json会卡住
2.读取存档有概率崩溃
3.有概率输出的json文件没格式化
### 仅在X86_64架构的Windows 10 22H2(19045.6332)和 Windows 11 25H2(26200.7171) 测试无严重问题 
Linux MacOS 暂未适配
#### 版本历史
1. V1.0.0 练手项目，第一次提交
2. V1.0.1 修复了改生命值不会改基础血量的问题
3. V1.0.2 新功能: 1.可以选择多存档 2.优化UI页面 
