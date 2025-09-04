@echo off
echo 开始构建Windows EXE...

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python
    pause
    exit /b 1
)

REM 安装依赖
echo 安装依赖包...
pip install -r requirements.txt

REM 清理之前的构建
echo 清理之前的构建文件...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM 使用PyInstaller构建
echo 使用PyInstaller构建EXE...
pyinstaller image_viewer.spec

REM 检查构建是否成功
if exist "dist\Image Viewer.exe" (
    echo.
    echo ✅ 构建成功！
    echo EXE文件位置: dist\Image Viewer.exe
    echo.
    echo 文件大小:
    dir "dist\Image Viewer.exe" | findstr "Image Viewer.exe"
) else (
    echo.
    echo ❌ 构建失败！
    echo 请检查错误信息
)

echo.
pause
