@echo off
chcp 65001 >nul
cd /d "%~dp0"

rem ====== 在这里配置机器人 ======
set APPID=102817881
set SECRET=Sl5Ql7UsGf5WxPsMqLrOvT2cCnP1eIxc
rem ==============================

rem 写入配置
(
  echo appid: "%APPID%"
  echo secret: "%SECRET%"
) > config.yaml

rem 首次运行自动创建虚拟环境并安装依赖
if not exist .venv\Scripts\python.exe (
    echo [首次运行] 创建虚拟环境并安装依赖...
    python -m venv .venv
    .venv\Scripts\python.exe -m pip install -q -r requirements.txt
)

echo [启动] 机器人...
.venv\Scripts\python.exe bot.py
pause
