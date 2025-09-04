#!/usr/bin/env python3
"""
跨平台构建脚本
支持Windows EXE和macOS DMG构建
"""

import os
import sys
import platform
import subprocess
import shutil


def run_command(command, shell=True):
    """运行命令并返回结果"""
    try:
        result = subprocess.run(command, shell=shell, capture_output=True, text=True)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def check_dependencies():
    """检查依赖是否安装"""
    print("检查依赖...")

    # 检查Python
    if sys.version_info < (3, 8):
        print("❌ 需要Python 3.8或更高版本")
        return False

    # 检查PyInstaller
    success, _, _ = run_command("pyinstaller --version")
    if not success:
        print("❌ 未找到PyInstaller，正在安装...")
        success, _, error = run_command("pip3 install pyinstaller")
        if not success:
            print(f"❌ 安装PyInstaller失败: {error}")
            return False

    # 安装其他依赖
    print("安装项目依赖...")
    success, _, error = run_command("pip3 install -r requirements.txt")
    if not success:
        print(f"❌ 安装依赖失败: {error}")
        return False

    print("✅ 依赖检查完成")
    return True


def clean_build():
    """清理构建文件"""
    print("清理之前的构建文件...")
    dirs_to_clean = ['dist', 'build', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  删除 {dir_name}")


def build_windows():
    """构建Windows EXE"""
    print("开始构建Windows EXE...")

    # 使用PyInstaller构建
    success, stdout, stderr = run_command("pyinstaller image_viewer.spec")

    if success and os.path.exists("dist/Image Viewer.exe"):
        print("✅ Windows EXE构建成功！")
        print(f"文件位置: dist/Image Viewer.exe")

        # 显示文件大小
        try:
            size = os.path.getsize("dist/Image Viewer.exe")
            size_mb = size / (1024 * 1024)
            print(f"文件大小: {size_mb:.1f} MB")
        except:
            pass

        return True
    else:
        print("❌ Windows EXE构建失败！")
        if stderr:
            print(f"错误信息: {stderr}")
        return False


def build_macos():
    """构建macOS DMG"""
    print("开始构建macOS DMG...")

    # 使用PyInstaller构建APP
    success, stdout, stderr = run_command("pyinstaller image_viewer.spec")

    if not success or not os.path.exists("dist/Image Viewer.app"):
        print("❌ macOS APP构建失败！")
        if stderr:
            print(f"错误信息: {stderr}")
        return False

    print("✅ macOS APP构建成功！")

    # 创建DMG
    print("创建DMG文件...")

    dmg_temp = "temp_dmg"
    dmg_name = "Image_Viewer"
    app_name = "Image Viewer"

    try:
        # 清理之前的DMG
        if os.path.exists(f"{dmg_name}.dmg"):
            os.remove(f"{dmg_name}.dmg")

        # 创建临时目录并复制APP
        if os.path.exists(dmg_temp):
            shutil.rmtree(dmg_temp)
        os.makedirs(dmg_temp)

        shutil.copytree(f"dist/{app_name}.app", f"{dmg_temp}/{app_name}.app")

        # 创建Applications的符号链接
        os.symlink("/Applications", f"{dmg_temp}/Applications")

        # 创建DMG
        success, _, error = run_command(
            f'hdiutil create -srcfolder "{dmg_temp}" -volname "{app_name}" -fs HFS+ -format UDZO -o "{dmg_name}.dmg"')

        if success:
            print("✅ macOS DMG构建成功！")
            print(f"DMG文件位置: {dmg_name}.dmg")

            # 显示文件大小
            try:
                size = os.path.getsize(f"{dmg_name}.dmg")
                size_mb = size / (1024 * 1024)
                print(f"文件大小: {size_mb:.1f} MB")
            except:
                pass

            return True
        else:
            print(f"❌ DMG创建失败: {error}")
            return False

    finally:
        # 清理临时文件
        if os.path.exists(dmg_temp):
            shutil.rmtree(dmg_temp)


def main():
    """主函数"""
    print("=" * 50)
    print("图片浏览器构建脚本")
    print("=" * 50)

    # 检查依赖
    if not check_dependencies():
        sys.exit(1)

    # 清理构建文件
    clean_build()

    # 根据平台构建
    system = platform.system().lower()

    if system == "windows":
        success = build_windows()
    elif system == "darwin":  # macOS
        success = build_macos()
    else:
        print(f"❌ 不支持的操作系统: {system}")
        print("支持的平台: Windows, macOS")
        sys.exit(1)

    if success:
        print("\n🎉 构建完成！")
    else:
        print("\n❌ 构建失败！")
        sys.exit(1)


if __name__ == "__main__":
    main()
