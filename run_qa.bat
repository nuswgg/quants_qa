@echo off
:: 切换到 Anaconda 环境（确保依赖包正常加载）
call D:\ProgramData\Anaconda3\Scripts\activate.bat D:\ProgramData\Anaconda3

:: 运行你的目标 Python 文件
python "D:\ProgramData\Anaconda3\Lib\site-packages\QUANTAXIS\QASU\save_tdx.py"