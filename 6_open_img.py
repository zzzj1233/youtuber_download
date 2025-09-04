import os.path
import sys
import math
import glob
import json
import time
import requests
from collections import OrderedDict
from urllib.parse import urljoin, urlparse
import lxml.html

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *


class ConfigManager:
    """配置管理器，用于保存和加载用户设置"""
    def __init__(self):
        self.config_file = "image_viewer_config.json"
        self.default_config = {
            'image_folder': "/Users/jiangjie/Downloads/img",
            'items_per_page': 9,
            'cache_size_gb': 1,
            'xpath_configs': []
        }
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # 合并默认配置和用户配置
                    merged_config = self.default_config.copy()
                    merged_config.update(config)
                    return merged_config
        except Exception as e:
            print(f"加载配置失败: {e}")
        return self.default_config.copy()
    
    def save_config(self, config):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key, default=None):
        """获取配置项"""
        config = self.load_config()
        return config.get(key, default)
    
    def set(self, key, value):
        """设置配置项"""
        config = self.load_config()
        config[key] = value
        self.save_config(config)


class ConfigDialog(QDialog):
    """配置对话框"""
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_config = config_manager.load_config()
        self.setup_ui()
        self.load_current_config()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("⚙️ 配置设置")
        self.setModal(True)
        self.resize(600, 600)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("⚙️ 配置设置")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 8px;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 配置区域
        config_scroll = QScrollArea()
        config_scroll.setWidgetResizable(True)
        config_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                background: white;
            }
        """)
        
        config_widget = QWidget()
        config_layout = QVBoxLayout(config_widget)
        config_layout.setSpacing(15)
        
        # 文件夹选择区域
        folder_group = QGroupBox("📁 文件夹设置")
        folder_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        folder_layout = QVBoxLayout(folder_group)
        
        # 当前路径显示
        self.path_label = QLabel("当前路径: " + self.current_config.get('image_folder', ''))
        self.path_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background: #f5f5f5;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        """)
        self.path_label.setWordWrap(True)
        folder_layout.addWidget(self.path_label)
        
        # 选择文件夹按钮
        self.folder_button = QPushButton("📁 选择图片文件夹")
        self.folder_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.folder_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_button)
        
        config_layout.addWidget(folder_group)
        
        # 显示设置区域
        display_group = QGroupBox("🖼️ 显示设置")
        display_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        display_layout = QVBoxLayout(display_group)
        
        # 每页显示数量
        page_layout = QHBoxLayout()
        page_layout.addWidget(QLabel("每页显示数量:"))
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setRange(1, 50)
        self.page_spinbox.setValue(self.current_config.get('items_per_page', 9))
        page_layout.addWidget(self.page_spinbox)
        page_layout.addStretch()
        display_layout.addLayout(page_layout)
        
        # 缓存大小设置
        cache_group = QGroupBox("💾 缓存设置")
        cache_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        cache_group_layout = QVBoxLayout(cache_group)
        
        # 缓存大小滑动块
        cache_size_layout = QHBoxLayout()
        cache_size_layout.addWidget(QLabel("缓存大小:"))
        self.cache_slider = QSlider(Qt.Orientation.Horizontal)
        self.cache_slider.setRange(1, 10)  # 1-10GB
        self.cache_slider.setValue(self.current_config.get('cache_size_gb', 1))
        self.cache_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.cache_slider.setTickInterval(1)
        self.cache_slider.valueChanged.connect(self.update_cache_size_label)
        cache_size_layout.addWidget(self.cache_slider)
        
        self.cache_size_label = QLabel(f"{self.current_config.get('cache_size_gb', 1)} GB")
        self.cache_size_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                color: #2196f3;
                min-width: 50px;
            }
        """)
        cache_size_layout.addWidget(self.cache_size_label)
        cache_group_layout.addLayout(cache_size_layout)
        
        # 缓存使用情况显示
        self.cache_usage_label = QLabel("正在计算缓存使用情况...")
        self.cache_usage_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                background: #f5f5f5;
                border-radius: 4px;
                border: 1px solid #ddd;
                font-size: 12px;
            }
        """)
        cache_group_layout.addWidget(self.cache_usage_label)
        
        config_layout.addWidget(cache_group)
        
        config_layout.addWidget(display_group)
        
        # XPath配置区域
        xpath_group = QGroupBox("🔍 XPath配置")
        xpath_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        xpath_group_layout = QVBoxLayout(xpath_group)
        
        # XPath配置列表
        self.xpath_list = QListWidget()
        self.xpath_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background: white;
                alternate-background-color: #f9f9f9;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #1976d2;
            }
        """)
        self.xpath_list.setAlternatingRowColors(True)
        xpath_group_layout.addWidget(self.xpath_list)
        
        # XPath操作按钮
        xpath_button_layout = QHBoxLayout()
        
        self.add_xpath_btn = QPushButton("➕ 添加")
        self.add_xpath_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.add_xpath_btn.clicked.connect(self.add_xpath_config)
        xpath_button_layout.addWidget(self.add_xpath_btn)
        
        self.edit_xpath_btn = QPushButton("✏️ 编辑")
        self.edit_xpath_btn.setStyleSheet(Styles.BUTTON_SECONDARY)
        self.edit_xpath_btn.clicked.connect(self.edit_xpath_config)
        self.edit_xpath_btn.setEnabled(False)
        xpath_button_layout.addWidget(self.edit_xpath_btn)
        
        self.delete_xpath_btn = QPushButton("🗑️ 删除")
        self.delete_xpath_btn.setStyleSheet(Styles.BUTTON_DANGER)
        self.delete_xpath_btn.clicked.connect(self.delete_xpath_config)
        self.delete_xpath_btn.setEnabled(False)
        xpath_button_layout.addWidget(self.delete_xpath_btn)
        
        xpath_group_layout.addLayout(xpath_button_layout)
        
        # 连接列表选择事件
        self.xpath_list.itemSelectionChanged.connect(self.on_xpath_selection_changed)
        
        config_layout.addWidget(xpath_group)
        
        config_layout.addStretch()
        config_scroll.setWidget(config_widget)
        main_layout.addWidget(config_scroll)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 重置按钮
        reset_button = QPushButton("🔄 重置")
        reset_button.setStyleSheet(Styles.BUTTON_SECONDARY)
        reset_button.clicked.connect(self.reset_config)
        button_layout.addWidget(reset_button)
        
        # 取消按钮
        cancel_button = QPushButton("❌ 取消")
        cancel_button.setStyleSheet(Styles.BUTTON_SECONDARY)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 确定按钮
        ok_button = QPushButton("✅ 确定")
        ok_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        ok_button.clicked.connect(self.accept_config)
        button_layout.addWidget(ok_button)
        
        main_layout.addLayout(button_layout)
    
    def load_current_config(self):
        """加载当前配置到UI"""
        self.current_config = self.config_manager.load_config()
        self.path_label.setText("当前路径: " + self.current_config.get('image_folder', ''))
        self.page_spinbox.setValue(self.current_config.get('items_per_page', 9))
        self.cache_slider.setValue(self.current_config.get('cache_size_gb', 1))
        self.update_cache_size_label()
        self.update_cache_usage_display()
        self.load_xpath_configs()
    
    def select_folder(self):
        """选择文件夹"""
        folder = QFileDialog.getExistingDirectory(
            self, 
            "选择图片文件夹", 
            self.current_config.get('image_folder', '/'),
            QFileDialog.Option.ShowDirsOnly
        )
        
        if folder:
            self.current_config['image_folder'] = folder
            self.path_label.setText("当前路径: " + folder)
    
    def update_cache_size_label(self):
        """更新缓存大小标签"""
        size_gb = self.cache_slider.value()
        self.cache_size_label.setText(f"{size_gb} GB")
    
    def update_cache_usage_display(self):
        """更新缓存使用情况显示"""
        # 获取主应用的缓存信息
        parent_app = self.parent()
        if hasattr(parent_app, 'cache_current_mb') and hasattr(parent_app, 'cache_max_mb'):
            current_mb = parent_app.cache_current_mb
            max_mb = parent_app.cache_max_mb
            
            # 转换为GB显示
            current_gb = current_mb / 1024
            max_gb = max_mb / 1024
            
            # 计算使用百分比
            usage_percent = (current_mb / max_mb * 100) if max_mb > 0 else 0
            
            # 设置颜色
            if usage_percent > 80:
                color = "#f44336"  # 红色
            elif usage_percent > 60:
                color = "#ff9800"  # 橙色
            else:
                color = "#4caf50"  # 绿色
            
            usage_text = f"已使用: {current_gb:.2f} GB / {max_gb:.2f} GB ({usage_percent:.1f}%)"
            self.cache_usage_label.setText(usage_text)
            self.cache_usage_label.setStyleSheet(f"""
                QLabel {{
                    padding: 8px;
                    background: #f5f5f5;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                    font-size: 12px;
                    color: {color};
                    font-weight: bold;
                }}
            """)
        else:
            self.cache_usage_label.setText("缓存信息不可用")
    
    def load_xpath_configs(self):
        """加载xpath配置到列表"""
        self.xpath_list.clear()
        xpath_configs = self.current_config.get('xpath_configs', [])
        for config in xpath_configs:
            domain = config.get('domain', '')
            xpath = config.get('xpath', '')
            item_text = f"域名: {domain}\nXPath: {xpath}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, config)
            self.xpath_list.addItem(item)
    
    def on_xpath_selection_changed(self):
        """xpath列表选择改变时的处理"""
        has_selection = len(self.xpath_list.selectedItems()) > 0
        self.edit_xpath_btn.setEnabled(has_selection)
        self.delete_xpath_btn.setEnabled(has_selection)
    
    def add_xpath_config(self):
        """添加xpath配置"""
        dialog = XPathEditDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            domain, xpath = dialog.get_config()
            if domain and xpath:
                new_config = {'domain': domain, 'xpath': xpath}
                xpath_configs = self.current_config.get('xpath_configs', [])
                xpath_configs.append(new_config)
                self.current_config['xpath_configs'] = xpath_configs
                self.load_xpath_configs()
    
    def edit_xpath_config(self):
        """编辑xpath配置"""
        selected_items = self.xpath_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        config = item.data(Qt.ItemDataRole.UserRole)
        
        dialog = XPathEditDialog(self, config)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            domain, xpath = dialog.get_config()
            if domain and xpath:
                # 更新配置
                config['domain'] = domain
                config['xpath'] = xpath
                self.load_xpath_configs()
    
    def delete_xpath_config(self):
        """删除xpath配置"""
        selected_items = self.xpath_list.selectedItems()
        if not selected_items:
            return
        
        item = selected_items[0]
        config = item.data(Qt.ItemDataRole.UserRole)
        
        # 确认删除
        reply = QMessageBox.question(
            self, 
            "确认删除", 
            f"确定要删除域名 '{config.get('domain', '')}' 的XPath配置吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            xpath_configs = self.current_config.get('xpath_configs', [])
            if config in xpath_configs:
                xpath_configs.remove(config)
                self.current_config['xpath_configs'] = xpath_configs
                self.load_xpath_configs()
    
    def reset_config(self):
        """重置配置"""
        self.current_config = self.config_manager.default_config.copy()
        self.load_current_config()
    
    def accept_config(self):
        """接受配置"""
        # 更新配置
        self.current_config.update({
            'items_per_page': self.page_spinbox.value(),
            'cache_size_gb': self.cache_slider.value()
        })
        
        # 保存配置
        self.config_manager.save_config(self.current_config)
        
        # 发送配置更新信号
        self.accept()


class XPathEditDialog(QDialog):
    """XPath配置编辑对话框"""
    def __init__(self, parent=None, config=None):
        super().__init__(parent)
        self.config = config or {}
        self.setup_ui()
        self.load_config()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("🔍 XPath配置")
        self.setModal(True)
        self.resize(500, 300)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("🔍 XPath配置")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 8px;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 表单区域
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # 域名输入
        self.domain_edit = QLineEdit()
        self.domain_edit.setPlaceholderText("例如: example.com")
        self.domain_edit.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #2196f3;
            }
        """)
        form_layout.addRow("域名:", self.domain_edit)
        
        # XPath输入
        self.xpath_edit = QTextEdit()
        self.xpath_edit.setPlaceholderText("例如: //div[@class='image']//img/@src")
        self.xpath_edit.setMaximumHeight(100)
        self.xpath_edit.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
                font-family: 'Courier New';
            }
            QTextEdit:focus {
                border-color: #2196f3;
            }
        """)
        form_layout.addRow("XPath:", self.xpath_edit)
        
        main_layout.addLayout(form_layout)
        
        # 说明文本
        help_label = QLabel("💡 提示: 域名用于匹配网站，XPath用于提取图片链接")
        help_label.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 12px;
                padding: 8px;
                background: #f5f5f5;
                border-radius: 4px;
                border: 1px solid #ddd;
            }
        """)
        main_layout.addWidget(help_label)
        
        main_layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_button = QPushButton("❌ 取消")
        cancel_button.setStyleSheet(Styles.BUTTON_SECONDARY)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 确定按钮
        ok_button = QPushButton("✅ 确定")
        ok_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        ok_button.clicked.connect(self.accept_config)
        button_layout.addWidget(ok_button)
        
        main_layout.addLayout(button_layout)
    
    def load_config(self):
        """加载配置到UI"""
        if self.config:
            self.domain_edit.setText(self.config.get('domain', ''))
            self.xpath_edit.setPlainText(self.config.get('xpath', ''))
    
    def get_config(self):
        """获取配置"""
        domain = self.domain_edit.text().strip()
        xpath = self.xpath_edit.toPlainText().strip()
        return domain, xpath
    
    def accept_config(self):
        """接受配置"""
        domain, xpath = self.get_config()
        
        if not domain:
            QMessageBox.warning(self, "输入错误", "请输入域名")
            return
        
        if not xpath:
            QMessageBox.warning(self, "输入错误", "请输入XPath")
            return
        
        self.accept()


class WebScraper:
    """网页抓取器"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def get_webpage_content(self, url):
        """获取网页内容"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"获取网页内容失败: {e}")
            return None
    
    def extract_images_by_xpath(self, html_content, xpath):
        """根据XPath提取图片URL"""
        try:
            doc = lxml.html.fromstring(html_content)
            elements = doc.xpath(xpath)
            
            image_urls = []
            for element in elements:
                if isinstance(element, str):
                    image_urls.append(element)
                else:
                    # 如果是元素，获取其文本内容或属性
                    if hasattr(element, 'text') and element.text:
                        image_urls.append(element.text.strip())
                    elif hasattr(element, 'get'):
                        # 尝试获取src属性
                        src = element.get('src') or element.get('data-src') or element.get('href')
                        if src:
                            image_urls.append(src.strip())
            
            return list(set(image_urls))  # 去重
        except Exception as e:
            print(f"XPath提取失败: {e}")
            return []


class ImageDownloader:
    """图片下载器"""
    def __init__(self, base_folder):
        self.base_folder = base_folder
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def download_images(self, image_urls, folder_name):
        """下载图片到指定文件夹"""
        if not image_urls:
            return []
        
        # 创建文件夹
        download_folder = os.path.join(self.base_folder, folder_name)
        os.makedirs(download_folder, exist_ok=True)
        
        downloaded_files = []
        for i, url in enumerate(image_urls):
            try:
                # 处理相对URL
                if not url.startswith(('http://', 'https://')):
                    continue
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # 获取文件扩展名
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    # 根据Content-Type确定扩展名
                    content_type = response.headers.get('content-type', '')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'gif' in content_type:
                        ext = '.gif'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        ext = '.jpg'  # 默认
                    filename = f"image_{i+1}{ext}"
                
                # 保存文件
                file_path = os.path.join(download_folder, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_files.append(file_path)
                print(f"下载成功: {filename}")
                
            except Exception as e:
                print(f"下载失败 {url}: {e}")
        
        return downloaded_files


class ClipboardMonitor(QObject):
    """粘贴板监听器"""
    clipboard_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.clipboard = QApplication.clipboard()
        self.last_clipboard_text = ""
        self.clipboard.changed.connect(self.on_clipboard_changed)
    
    def on_clipboard_changed(self):
        """粘贴板内容改变时的处理"""
        try:
            current_text = self.clipboard.text()
            if current_text and current_text != self.last_clipboard_text:
                self.last_clipboard_text = current_text
                # 检查是否是URL
                if current_text.startswith(('http://', 'https://')):
                    self.clipboard_changed.emit(current_text)
        except Exception as e:
            print(f"粘贴板监听错误: {e}")


class DownloadConfirmDialog(QDialog):
    """下载确认对话框"""
    def __init__(self, url, image_count, parent=None):
        super().__init__(parent)
        self.url = url
        self.image_count = image_count
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("🔍 发现图片")
        self.setModal(True)
        self.resize(500, 300)
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("🔍 发现图片")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 8px;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 信息显示
        info_text = f"""
        <p><b>网页地址:</b> {self.url}</p>
        <p><b>发现图片数量:</b> {self.image_count} 张</p>
        <p>是否要下载这些图片到配置的文件夹中？</p>
        """
        
        info_label = QLabel(info_text)
        info_label.setStyleSheet("""
            QLabel {
                padding: 15px;
                background: #f5f5f5;
                border-radius: 6px;
                border: 1px solid #ddd;
                font-size: 14px;
            }
        """)
        info_label.setWordWrap(True)
        main_layout.addWidget(info_label)
        
        # 不再提示选项
        self.dont_ask_again_cb = QCheckBox("不再提示此URL（本次程序运行期间）")
        self.dont_ask_again_cb.setChecked(True)
        self.dont_ask_again_cb.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #666;
            }
        """)
        main_layout.addWidget(self.dont_ask_again_cb)
        
        main_layout.addStretch()
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 取消按钮
        cancel_button = QPushButton("❌ 取消")
        cancel_button.setStyleSheet(Styles.BUTTON_SECONDARY)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # 下载按钮
        download_button = QPushButton("⬇️ 下载")
        download_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        download_button.clicked.connect(self.accept)
        button_layout.addWidget(download_button)
        
        main_layout.addLayout(button_layout)
    
    def should_download(self):
        """是否要下载"""
        return self.exec() == QDialog.DialogCode.Accepted
    
    def dont_ask_again(self):
        """是否不再提示"""
        return self.dont_ask_again_cb.isChecked()


class DownloadProgressDialog(QDialog):
    """下载进度对话框"""
    def __init__(self, total_count, parent=None):
        super().__init__(parent)
        self.total_count = total_count
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("⬇️ 下载图片")
        self.setModal(True)
        self.resize(400, 200)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowCloseButtonHint)  # 禁用关闭按钮
        
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("⬇️ 正在下载图片...")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border-radius: 8px;
                text-align: center;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, self.total_count)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4fc3f7, stop:1 #29b6f6);
                border-radius: 6px;
            }
        """)
        main_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel(f"准备下载 {self.total_count} 张图片...")
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #666;
                padding: 8px;
                text-align: center;
            }
        """)
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(self.status_label)
        
        # 取消按钮
        self.cancel_button = QPushButton("❌ 取消下载")
        self.cancel_button.setStyleSheet(Styles.BUTTON_SECONDARY)
        self.cancel_button.clicked.connect(self.cancel_download)
        main_layout.addWidget(self.cancel_button)
    
    def update_progress(self, current, total):
        """更新进度"""
        self.progress_bar.setValue(current)
        self.status_label.setText(f"已下载 {current}/{total} 张图片...")
    
    def cancel_download(self):
        """取消下载"""
        reply = QMessageBox.question(
            self, 
            "确认取消", 
            "确定要取消下载吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.reject()


class WorkerSignals(QObject):
    imageLoaded = pyqtSignal(int, QPixmap)


class DownloadSignals(QObject):
    """图片下载信号"""
    progress = pyqtSignal(int, int)  # 当前进度, 总数
    finished = pyqtSignal(list)  # 下载完成的文件列表
    error = pyqtSignal(str)  # 错误信息


class ImageDownloadWorker(QRunnable):
    """图片下载工作线程"""
    def __init__(self, image_urls, download_folder, base_url="", original_url=""):
        super().__init__()
        self.image_urls = image_urls
        self.download_folder = download_folder
        self.base_url = base_url
        self.original_url = original_url
        self.signals = DownloadSignals()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    @pyqtSlot()
    def run(self):
        """执行下载任务"""
        downloaded_files = []
        total = len(self.image_urls)
        
        for i, url in enumerate(self.image_urls):
            try:
                # 处理相对URL
                if not url.startswith(('http://', 'https://')):
                    if self.base_url:
                        url = urljoin(self.base_url, url)
                    else:
                        continue
                
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # 获取文件扩展名
                parsed_url = urlparse(url)
                filename = os.path.basename(parsed_url.path)
                if not filename or '.' not in filename:
                    # 根据Content-Type确定扩展名
                    content_type = response.headers.get('content-type', '')
                    if 'jpeg' in content_type or 'jpg' in content_type:
                        ext = '.jpg'
                    elif 'png' in content_type:
                        ext = '.png'
                    elif 'gif' in content_type:
                        ext = '.gif'
                    elif 'webp' in content_type:
                        ext = '.webp'
                    else:
                        ext = '.jpg'  # 默认
                    filename = f"image_{i+1}{ext}"
                
                # 保存文件
                file_path = os.path.join(self.download_folder, filename)
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                downloaded_files.append(file_path)
                
                # 发送进度信号
                self.signals.progress.emit(i + 1, total)
                
            except Exception as e:
                print(f"下载失败 {url}: {e}")
                # 继续下载其他图片，不中断整个流程
        
        # 保存原始URL到文件夹
        if self.original_url:
            try:
                url_file_path = os.path.join(self.download_folder, "original_url.txt")
                with open(url_file_path, 'w', encoding='utf-8') as f:
                    f.write(self.original_url)
            except Exception as e:
                print(f"保存原始URL失败: {e}")
        
        # 发送完成信号
        self.signals.finished.emit(downloaded_files)


class ImageLoadWorker(QRunnable):
    def __init__(self, global_index: int, image_path: str, target_size: QSize):
        super().__init__()
        self.global_index = global_index
        self.image_path = image_path
        self.target_size = target_size
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        pixmap = QPixmap(self.image_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                self.target_size,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.signals.imageLoaded.emit(self.global_index, scaled)
        else:
            self.signals.imageLoaded.emit(self.global_index, QPixmap())


class Styles:
    CONTAINER_CARD = """
        QWidget {
            background: white;
            border-radius: 12px;
            padding: 15px;
            border: 1px solid #e0e0e0;
        }
    """

    BADGE_BLUE = """
        QLabel {
            font-size: 14px;
            font-weight: bold;
            color: #495057;
            padding: 8px 12px;
            background: #e3f2fd;
            border-radius: 8px;
            border: 1px solid #bbdefb;
        }
    """

    BADGE_PURPLE = """
        QLabel {
            font-size: 14px;
            font-weight: bold;
            color: #495057;
            padding: 8px 12px;
            background: #f3e5f5;
            border-radius: 8px;
            border: 1px solid #ce93d8;
        }
    """

    BADGE_WARNING = """
        QLabel {
            font-size: 14px;
            font-weight: bold;
            color: #495057;
            padding: 8px 12px;
            background: #fff3cd;
            border-radius: 8px;
            border: 1px solid #ffeeba;
        }
    """

    BUTTON_PRIMARY = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #4fc3f7, stop:1 #29b6f6);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #29b6f6, stop:1 #0288d1);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #0288d1, stop:1 #0277bd);
        }
        QPushButton:disabled {
            background: #bdbdbd;
            color: #757575;
        }
    """
    
    BUTTON_SECONDARY = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #90a4ae, stop:1 #78909c);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #78909c, stop:1 #607d8b);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #607d8b, stop:1 #546e7a);
        }
        QPushButton:disabled {
            background: #bdbdbd;
            color: #757575;
        }
    """

    BUTTON_DANGER = """
        QPushButton {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff7043, stop:1 #ff5722);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            min-width: 80px;
        }
        QPushButton:hover {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ff5722, stop:1 #d84315);
        }
        QPushButton:pressed {
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #d84315, stop:1 #bf360c);
        }
    """

    COMBOBOX = """
        QComboBox {
            background: white;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            padding: 8px 12px;
            font-size: 14px;
            min-width: 100px;
        }
        QComboBox:hover {
            border-color: #4fc3f7;
        }
        QComboBox::drop-down {
            border: none;
            width: 20px;
        }
        QComboBox::down-arrow {
            image: none;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid #666;
            margin-right: 5px;
        }
        QComboBox QAbstractItemView {
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            selection-background-color: #e3f2fd;
        }
    """

    IMAGE_LABEL = """
        QLabel {
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #fafafa, stop:1 #f5f5f5);
            padding: 8px;
        }
        QLabel:hover {
            border-color: #4fc3f7;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffffff, stop:1 #f8f9fa);
        }
    """

    IMAGE_LABEL_ERROR = """
        QLabel {
            border: 2px solid #ffcdd2;
            border-radius: 12px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #ffebee, stop:1 #ffcdd2);
            padding: 8px;
            color: #c62828;
            font-size: 12px;
            font-weight: bold;
        }
    """

    THUMB_ACTIVE = """
        QLabel {
            border: 3px solid #ff5722;
            border-radius: 8px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #fff3e0, stop:1 #ffe0b2);
            padding: 4px;
        }
    """

    THUMB_NORMAL = """
        QLabel {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 #fafafa, stop:1 #f5f5f5);
            padding: 4px;
        }
    """

class ClickableLabel(QLabel):
    clicked = pyqtSignal(int)

    def __init__(self, index: int = -1, parent=None):
        super().__init__(parent)
        self._index = index

    def setIndex(self, index: int):
        self._index = index

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self._index)
        super().mousePressEvent(event)


class ClickableDetailLabel(QLabel):
    """可双击的详情页图片标签"""
    double_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # 初始化配置管理器
        self.config_manager = ConfigManager()
        config = self.config_manager.load_config()
        self.image_folder = config.get('image_folder', '/Users/jiangjie/Downloads/img')
        self.items_per_page = config.get('items_per_page', 9)
        self.cache_max_mb = config.get('cache_size_gb', 1) * 1024  # 转换为MB
        
        # 支持的图片格式
        self.image_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.webp', '*.jfif']
        
        # 加载图片文件列表
        self.image_files = self.load_image_files()
        self.current_page = 1
        self.items_per_page = 9
        # 相册（子目录）列表
        self.albums = self.load_albums()
        self.total_pages = math.ceil(len(self.albums) / self.items_per_page)
        
        # 线程池用于并行加载图片
        self.thread_pool = QThreadPool()
        # 保存当前页面标签，按全局索引映射
        self.label_by_index = {}
        # 图片缓存（FIFO）：按(路径, 目标宽, 目标高)缓存缩放后的QPixmap
        self.pixmap_cache: OrderedDict[tuple, QPixmap] = OrderedDict()
        self.cache_max_mb: float = 100.0
        self.cache_current_mb: float = 0.0
        # 详情视图状态
        self.current_album_index: int = -1
        self.current_image_index: int = -1
        # 缩略图标签列表，用于更新高亮状态
        self.thumb_labels: list[ClickableLabel] = []
        
        # UI组件
        self.folder_button = None
        
        # 粘贴板监听和图片下载
        self.clipboard_monitor = ClipboardMonitor()
        self.clipboard_monitor.clipboard_changed.connect(self.on_clipboard_url)
        self.web_scraper = WebScraper()
        self.image_downloader = None
        self.ignored_urls = set()  # 本次程序运行期间忽略的URL

        self.setup_ui()
        # 设置窗口标题（相册数量）
        self.setWindowTitle(f"🖼️ 图片分页展示 - 共{len(self.albums)}个相册")

    def on_clipboard_url(self, url):
        """处理粘贴板中的URL"""
        # 检查是否在忽略列表中
        if url in self.ignored_urls:
            return
        
        # 获取XPath配置
        config = self.config_manager.load_config()
        xpath_configs = config.get('xpath_configs', [])
        
        # 检查URL是否匹配任何配置的域名
        matched_config = None
        for xpath_config in xpath_configs:
            domain = xpath_config.get('domain', '')
            if domain and domain in url:
                matched_config = xpath_config
                break
        
        if not matched_config:
            return
        
        # 异步处理URL
        QTimer.singleShot(100, lambda: self.process_url(url, matched_config))
    
    def process_url(self, url, xpath_config):
        """处理URL，提取图片并询问是否下载"""
        try:
            # 获取网页内容
            html_content = self.web_scraper.get_webpage_content(url)
            if not html_content:
                return
            
            # 提取图片URL
            xpath = xpath_config.get('xpath', '')
            image_urls = self.web_scraper.extract_images_by_xpath(html_content, xpath)
            
            if not image_urls:
                return
            
            # 显示下载确认对话框
            dialog = DownloadConfirmDialog(url, len(image_urls), self)
            if dialog.should_download():
                self.download_images(url, image_urls)
            elif dialog.dont_ask_again():
                self.ignored_urls.add(url)
                
        except Exception as e:
            print(f"处理URL失败: {e}")
    
    def download_images(self, url, image_urls):
        """下载图片（多线程版本）"""
        try:
            # 获取配置
            config = self.config_manager.load_config()
            base_folder = config.get('image_folder', '/Users/jiangjie/Downloads/img')
            
            # 生成文件夹名称：域名+时间戳
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.replace('www.', '')
            timestamp = int(time.time())
            folder_name = f"{domain}_{timestamp}"
            
            # 创建下载文件夹
            download_folder = os.path.join(base_folder, folder_name)
            os.makedirs(download_folder, exist_ok=True)
            
            # 显示进度对话框
            self.progress_dialog = DownloadProgressDialog(len(image_urls), self)
            
            # 创建下载工作线程
            self.download_worker = ImageDownloadWorker(image_urls, download_folder, url, url)
            
            # 连接信号
            self.download_worker.signals.progress.connect(self.progress_dialog.update_progress)
            self.download_worker.signals.finished.connect(self.on_download_finished)
            self.download_worker.signals.error.connect(self.on_download_error)
            
            # 启动下载线程
            self.thread_pool.start(self.download_worker)
            
            # 显示进度对话框
            self.progress_dialog.show()
                
        except Exception as e:
            QMessageBox.critical(self, "下载错误", f"启动下载时发生错误: {e}")
    
    def on_download_finished(self, downloaded_files):
        """下载完成处理"""
        try:
            # 关闭进度对话框
            if hasattr(self, 'progress_dialog'):
                self.progress_dialog.close()
            
            if downloaded_files:
                # 显示成功消息
                QMessageBox.information(
                    self, 
                    "下载完成", 
                    f"成功下载 {len(downloaded_files)} 张图片"
                )
                
                # 刷新相册列表
                self.albums = self.load_albums()
                self.total_pages = math.ceil(len(self.albums) / self.items_per_page)
                self.current_page = 1
                self.display_current_page()
                self.setWindowTitle(f"🖼️ 图片分页展示 - 共{len(self.albums)}个相册")
            else:
                QMessageBox.warning(self, "下载失败", "没有成功下载任何图片")
                
        except Exception as e:
            QMessageBox.critical(self, "处理错误", f"处理下载结果时发生错误: {e}")
    
    def on_download_error(self, error_message):
        """下载错误处理"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        QMessageBox.critical(self, "下载错误", f"下载过程中发生错误: {error_message}")

    def show_config_dialog(self):
        """显示配置对话框"""
        dialog = ConfigDialog(self.config_manager, self)
        # 在显示对话框前更新缓存使用情况
        dialog.update_cache_usage_display()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 配置已更新，重新加载应用
            self.reload_application()
    
    def reload_application(self):
        """重新加载应用配置"""
        config = self.config_manager.load_config()
        
        # 检查是否需要更新文件夹
        new_folder = config.get('image_folder', self.image_folder)
        if new_folder != self.image_folder:
            self.image_folder = new_folder
            # 清空缓存
            self.pixmap_cache.clear()
            self.cache_current_mb = 0.0
        
        # 更新其他配置
        new_items_per_page = config.get('items_per_page', self.items_per_page)
        if new_items_per_page != self.items_per_page:
            self.items_per_page = new_items_per_page
        
        new_cache_size_gb = config.get('cache_size_gb', self.cache_max_mb / 1024)
        new_cache_size_mb = new_cache_size_gb * 1024
        if new_cache_size_mb != self.cache_max_mb:
            self.cache_max_mb = new_cache_size_mb
        
        # 重新加载相册
        self.albums = self.load_albums()
        self.total_pages = math.ceil(len(self.albums) / self.items_per_page)
        self.current_page = 1
        
        # 更新UI显示
        self.total_label.setText(f"共 {len(self.albums)} 个相册")
        self.setWindowTitle(f"🖼️ 图片分页展示 - 共{len(self.albums)}个相册")
        self.display_current_page()

    def _estimate_pixmap_mb(self, pixmap: QPixmap) -> float:
        if pixmap.isNull():
            return 0.0
        return (pixmap.width() * pixmap.height() * 4) / (1024 * 1024)

    def _cache_put(self, key: tuple, pixmap: QPixmap):
        # 跳过无效或超过最大容量的单张图片
        new_mb = self._estimate_pixmap_mb(pixmap)
        if new_mb <= 0 or new_mb > self.cache_max_mb:
            return

        # 如果键已存在，先移除旧的以便更新插入顺序和容量
        if key in self.pixmap_cache:
            old = self.pixmap_cache.pop(key)
            self.cache_current_mb -= max(0.0, self._estimate_pixmap_mb(old))

        # 需要腾挪空间：按FIFO淘汰最早插入的条目
        while self.cache_current_mb + new_mb > self.cache_max_mb and self.pixmap_cache:
            oldest_key, oldest_pix = self.pixmap_cache.popitem(last=False)
            self.cache_current_mb -= max(0.0, self._estimate_pixmap_mb(oldest_pix))

        # 插入新条目
        self.pixmap_cache[key] = pixmap
        self.cache_current_mb += new_mb
        
        self.setWindowTitle(f"🖼️ 图片分页展示 - 共{len(self.image_files)}张图片")
        # self.setWindowIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))

    def load_image_files(self):
        """从指定文件夹加载图片文件"""
        image_files = []
        for extension in self.image_extensions:
            pattern = os.path.join(self.image_folder, extension)
            image_files.extend(glob.glob(pattern))
            # 也搜索大写扩展名
            pattern = os.path.join(self.image_folder, extension.upper())
            image_files.extend(glob.glob(pattern))
        
        # 去重并排序
        image_files = sorted(list(set(image_files)))
        return image_files
    
    def find_images_in_folder(self, folder_path: str):
        images = []
        for ext in self.image_extensions:
            images.extend(glob.glob(os.path.join(folder_path, ext)))
            images.extend(glob.glob(os.path.join(folder_path, ext.upper())))
        
        # 按照时间戳排序
        def get_timestamp_from_path(path):
            filename = os.path.basename(path)
            if filename.count('_') >= 2:  # 时间戳格式：1234567890_原文件名
                try:
                    first_underscore = filename.find('_')
                    if first_underscore > 0:
                        potential_timestamp = filename[:first_underscore]
                        return int(potential_timestamp)
                except ValueError:
                    pass
            return 0  # 没有时间戳的文件视为0
        
        # 按照时间戳从大到小排序（最新的在前）
        images = list(set(images))
        images.sort(key=get_timestamp_from_path, reverse=True)
        return images

    def get_original_url_from_folder(self, folder_path):
        """从文件夹中获取原始URL"""
        try:
            url_file_path = os.path.join(folder_path, "original_url.txt")
            if os.path.exists(url_file_path):
                with open(url_file_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
        except Exception as e:
            print(f"读取原始URL失败: {e}")
        return None

    def open_url_in_browser(self, url):
        """在默认浏览器中打开URL"""
        try:
            import webbrowser
            webbrowser.open(url)
        except Exception as e:
            QMessageBox.critical(self, "打开失败", f"无法打开URL: {e}")
    
    def open_image_with_default_viewer(self, image_path):
        """使用默认图片查看器打开图片"""
        try:
            import platform
            import subprocess
            import os
            
            system = platform.system().lower()
            
            if system == "darwin":  # macOS
                subprocess.run(["open", image_path], check=True)
            elif system == "windows":  # Windows
                os.startfile(image_path)
            elif system == "linux":  # Linux
                # 尝试使用xdg-open
                subprocess.run(["xdg-open", image_path], check=True)
            else:
                # 回退到webbrowser
                import webbrowser
                webbrowser.open(f"file://{os.path.abspath(image_path)}")
                
        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "打开失败", f"无法使用默认图片查看器打开文件:\n{e}")
        except Exception as e:
            QMessageBox.critical(self, "打开失败", f"打开图片时发生错误:\n{e}")

    def load_albums(self):
        """扫描根目录子目录，构建相册列表（封面为第一张图片）"""
        albums = []
        if not os.path.isdir(self.image_folder):
            return albums
        for entry in os.listdir(self.image_folder):
            subdir = os.path.join(self.image_folder, entry)
            if os.path.isdir(subdir):
                imgs = self.find_images_in_folder(subdir)
                if imgs:
                    # 提取时间戳用于排序
                    timestamp = 0
                    if entry.count('_') >= 2:  # 时间戳格式：1234567890_原名称
                        try:
                            first_underscore = entry.find('_')
                            if first_underscore > 0:
                                potential_timestamp = entry[:first_underscore]
                                timestamp = int(potential_timestamp)
                        except ValueError:
                            pass  # 不是时间戳格式，保持0
                    
                    # 获取原始URL
                    original_url = self.get_original_url_from_folder(subdir)
                    
                    albums.append({
                        'name': entry,
                        'path': subdir,
                        'images': imgs,
                        'cover': imgs[0],
                        'timestamp': timestamp,
                        'original_url': original_url
                    })
        
        # 按照时间戳从大到小排序（最新的在前）
        albums.sort(key=lambda x: x['timestamp'], reverse=True)
        return albums
    
    # 删除缓存与懒加载相关方法，改为线程并行加载
    def setup_ui(self):
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部控制区域容器
        control_container = QWidget()
        control_container.setStyleSheet(Styles.CONTAINER_CARD)
        control_layout = QHBoxLayout(control_container)
        control_layout.setSpacing(15)
        
        # 页面信息标签
        self.page_label = QLabel(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        self.page_label.setStyleSheet(Styles.BADGE_BLUE)
        control_layout.addWidget(self.page_label)
        
        # 图片总数标签
        self.total_label = QLabel(f"共 {len(self.albums)} 个相册")
        self.total_label.setStyleSheet(Styles.BADGE_PURPLE)
        control_layout.addWidget(self.total_label)
        
        # 添加弹性空间
        control_layout.addStretch()
        
        # 配置按钮
        self.config_button = QPushButton("⚙️ 配置")
        self.config_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.config_button.clicked.connect(self.show_config_dialog)
        control_layout.addWidget(self.config_button)

        
        # 上一页按钮
        self.prev_button = QPushButton("◀ 上一页")
        self.prev_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.prev_button.clicked.connect(self.prev_page)
        control_layout.addWidget(self.prev_button)
        
        # 下一页按钮
        self.next_button = QPushButton("下一页 ▶")
        self.next_button.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.next_button.clicked.connect(self.next_page)
        control_layout.addWidget(self.next_button)
        
        # 页面跳转下拉框
        self.page_combo = QComboBox()
        self.page_combo.setStyleSheet(Styles.COMBOBOX)
        for i in range(1, self.total_pages + 1):
            self.page_combo.addItem(f"第 {i} 页")
        self.page_combo.currentIndexChanged.connect(self.jump_to_page)
        control_layout.addWidget(self.page_combo)
        
        # 重新加载当前页按钮
        self.reload_button = QPushButton("↻ 重新加载")
        self.reload_button.setStyleSheet(Styles.BUTTON_DANGER)
        self.reload_button.clicked.connect(self.display_current_page)
        control_layout.addWidget(self.reload_button)
        
        control_layout.addStretch()  # 添加弹性空间
        main_layout.addWidget(control_container)
        
        # 使用堆叠视图：0=相册网格 1=详情页
        self.stacked = QStackedWidget()
        
        # 相册网格页
        grid_page = QWidget()
        grid_page.setStyleSheet(Styles.CONTAINER_CARD)
        self.image_grid = QGridLayout(grid_page)
        self.image_grid.setSpacing(12)
        self.image_grid.setContentsMargins(15, 15, 15, 15)
        self.stacked.addWidget(grid_page)

        # 详情页
        detail_page = QWidget()
        detail_page.setStyleSheet(Styles.CONTAINER_CARD)
        detail_layout = QVBoxLayout(detail_page)
        detail_layout.setSpacing(10)
        detail_layout.setContentsMargins(10, 10, 10, 10)

        # 顶部：返回按钮靠左，跳转按钮靠右
        top_bar = QHBoxLayout()
        self.detail_back_btn = QPushButton("↩ 返回相册")
        self.detail_back_btn.setStyleSheet(Styles.BUTTON_DANGER)
        self.detail_back_btn.clicked.connect(self.detail_back)
        top_bar.addWidget(self.detail_back_btn, 0, Qt.AlignmentFlag.AlignLeft)
        
        top_bar.addStretch()
        
        # 跳转到原始网页按钮
        self.detail_jump_btn = QPushButton("🌐 原始网页")
        self.detail_jump_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.detail_jump_btn.clicked.connect(self.detail_jump_to_original)
        self.detail_jump_btn.setVisible(False)  # 默认隐藏
        top_bar.addWidget(self.detail_jump_btn, 0, Qt.AlignmentFlag.AlignRight)
        
        detail_layout.addLayout(top_bar)

        # 中部：左右侧导航 + 中间图片
        center_wrap = QHBoxLayout()
        center_wrap.setSpacing(10)

        self.detail_prev_btn = QPushButton("◀")
        self.detail_prev_btn.setFixedWidth(48)
        self.detail_prev_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.detail_prev_btn.clicked.connect(self.detail_prev)
        center_wrap.addWidget(self.detail_prev_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        self.detail_label = ClickableDetailLabel()
        self.detail_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.detail_label.setMinimumSize(600, 400)
        self.detail_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.detail_label.customContextMenuRequested.connect(self.on_detail_image_context_menu)
        self.detail_label.double_clicked.connect(self.on_detail_image_double_click)
        center_wrap.addWidget(self.detail_label, 1)

        self.detail_next_btn = QPushButton("▶")
        self.detail_next_btn.setFixedWidth(48)
        self.detail_next_btn.setStyleSheet(Styles.BUTTON_PRIMARY)
        self.detail_next_btn.clicked.connect(self.detail_next)
        center_wrap.addWidget(self.detail_next_btn, 0, Qt.AlignmentFlag.AlignVCenter)

        detail_layout.addLayout(center_wrap)

        # 底部：缩略图条
        self.thumb_container = QScrollArea()
        self.thumb_container.setWidgetResizable(True)
        self.thumb_container.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.thumb_container.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.thumb_container.setFixedHeight(120)
        thumb_inner = QWidget()
        self.thumb_layout = QHBoxLayout(thumb_inner)
        self.thumb_layout.setSpacing(8)
        self.thumb_layout.setContentsMargins(8, 8, 8, 8)
        self.thumb_container.setWidget(thumb_inner)
        detail_layout.addWidget(self.thumb_container)
        
        self.stacked.addWidget(detail_page)

        main_layout.addWidget(self.stacked)
        
        # 显示当前页面的图片
        self.display_current_page()
        
        # 设置主窗口
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        self.resize(1000, 800)
        
    def display_current_page(self):
        # 清除现有的图片标签
        for i in reversed(range(self.image_grid.count())):
            self.image_grid.itemAt(i).widget().setParent(None)
        self.label_by_index.clear()
        
        # 计算当前页面的数据范围（相册）
        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.albums))
        
        # 创建3x3网格显示图片
        target_size = QSize(204, 204)
        for i, idx in enumerate(range(start_idx, end_idx)):
            row = i // 3
            col = i % 3
            
            # 创建可点击图片标签（相册封面）
            image_label = ClickableLabel(index=idx)
            image_label.setFixedSize(220, 220)
            image_label.setStyleSheet(Styles.IMAGE_LABEL)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setScaledContents(True)
            image_label.clicked.connect(self.on_album_clicked)
            
            # 占位文本，异步加载后替换
            image_label.setText("加载中…")
            self.image_grid.addWidget(image_label, row, col)

            # 记录标签与全局索引的映射
            self.label_by_index[idx] = image_label

            # 启动工作线程加载相册封面（带缓存）
            image_path = self.albums[idx]['cover']
            cache_key = (image_path, target_size.width(), target_size.height())
            cached = self.pixmap_cache.get(cache_key)
            if cached is not None and not cached.isNull():
                image_label.setPixmap(cached)
            else:
                worker = ImageLoadWorker(idx, image_path, target_size)
                worker.signals.imageLoaded.connect(self.on_image_loaded)
                self.thread_pool.start(worker)
            # 设置工具提示显示名称，并添加右键菜单：置顶相册
            image_label.setToolTip(self.albums[idx]['name'])
            image_label.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            def _make_album_ctx(album_index=idx, label_ref=image_label):
                def _ctx_menu(pos):
                    self.on_album_cover_context_menu(album_index, label_ref.mapToGlobal(pos))
                return _ctx_menu
            image_label.customContextMenuRequested.connect(_make_album_ctx())
        
        # 如果本页不足9个，使用空白占位补齐，保持网格不变形
        items_on_page = end_idx - start_idx
        if items_on_page < self.items_per_page:
            for j in range(items_on_page, self.items_per_page):
                row = j // 3
                col = j % 3
                placeholder = QLabel()
                placeholder.setFixedSize(220, 220)
                placeholder.setStyleSheet("""
                    QLabel {
                        border: 2px solid transparent;
                        border-radius: 12px;
                        background: transparent;
                        padding: 8px;
                    }
                """)
                placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
                self.image_grid.addWidget(placeholder, row, col)

        # 更新页面信息
        self.page_label.setText(f"第 {self.current_page} 页，共 {self.total_pages} 页")
        self.page_combo.setCurrentIndex(self.current_page - 1)
        

        # 更新按钮状态
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)
        
    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.display_current_page()
            
    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.display_current_page()
            
    def jump_to_page(self, index):
        self.current_page = index + 1
        self.display_current_page()

    @pyqtSlot(int, QPixmap)
    def on_image_loaded(self, global_index: int, pixmap: QPixmap):
        # 如果标签还在当前页面，更新它
        label = self.label_by_index.get(global_index)
        if label is None:
            return
        if pixmap.isNull():
            filename = self.albums[global_index]['name']
            label.setText(f"❌ 加载失败\n{filename}")
            label.setStyleSheet(Styles.IMAGE_LABEL_ERROR)
        else:
            # 写入缓存（FIFO，固定容量）
            image_path = self.albums[global_index]['cover']
            cache_key = (image_path, pixmap.width(), pixmap.height())
            self._cache_put(cache_key, pixmap)
            label.setPixmap(pixmap)

    def on_album_clicked(self, album_index: int):
        if album_index < 0 or album_index >= len(self.albums):
            return
        self.current_album_index = album_index
        self.current_image_index = 0
        self.show_detail_page()

    def show_detail_page(self):
        self.update_detail_image()
        self.build_thumbnails()
        
        # 控制跳转按钮显示
        album = self.albums[self.current_album_index]
        original_url = album.get('original_url')
        self.detail_jump_btn.setVisible(original_url is not None)
        
        self.stacked.setCurrentIndex(1)
        # 延迟滚动，确保缩略图已构建完成
        QTimer.singleShot(100, self.scroll_to_current_thumb)

    def detail_back(self):
        self.stacked.setCurrentIndex(0)
    
    def detail_jump_to_original(self):
        """详情页跳转到原始网页"""
        if self.current_album_index >= 0 and self.current_album_index < len(self.albums):
            album = self.albums[self.current_album_index]
            original_url = album.get('original_url')
            if original_url:
                self.open_url_in_browser(original_url)
    
    def on_detail_image_double_click(self):
        """详情页图片双击事件"""
        if self.current_album_index >= 0 and self.current_album_index < len(self.albums):
            album = self.albums[self.current_album_index]
            images = album.get('images', [])
            if self.current_image_index >= 0 and self.current_image_index < len(images):
                image_path = images[self.current_image_index]
                self.open_image_with_default_viewer(image_path)

    def detail_prev(self):
        images = self.albums[self.current_album_index]['images']
        if self.current_image_index > 0:
            self.current_image_index -= 1
            self.update_detail_image()
            self.update_thumb_highlight()
            self.scroll_to_current_thumb()

    def detail_next(self):
        images = self.albums[self.current_album_index]['images']
        if self.current_image_index < len(images) - 1:
            self.current_image_index += 1
            self.update_detail_image()
            self.update_thumb_highlight()
            self.scroll_to_current_thumb()

    def keyPressEvent(self, event):
        if self.stacked.currentIndex() == 1:
            if event.key() in (Qt.Key.Key_Right, Qt.Key.Key_D):
                self.detail_next()
            elif event.key() in (Qt.Key.Key_Left, Qt.Key.Key_A):
                self.detail_prev()
            elif event.key() in (Qt.Key.Key_Escape, Qt.Key.Key_Backspace):
                self.detail_back()
        super().keyPressEvent(event)

    def update_detail_image(self):
        if self.current_album_index < 0:
            return
        images = self.albums[self.current_album_index]['images']
        if not images:
            return
        image_path = images[self.current_image_index]
        size = self.detail_label.size()
        target_size = QSize(max(200, size.width() - 30), max(150, size.height() - 30))
        cache_key = (image_path, target_size.width(), target_size.height())
        cached = self.pixmap_cache.get(cache_key)
        if cached is not None and not cached.isNull():
            self.detail_label.setPixmap(cached)
            return
        self.detail_label.setText("加载中…")
        worker = ImageLoadWorker(-1, image_path, target_size)
        def _on_detail_loaded(_, pixmap: QPixmap, path=image_path, key=cache_key):
            if pixmap.isNull():
                self.detail_label.setText("❌ 加载失败")
            else:
                self._cache_put(key, pixmap)
                self.detail_label.setPixmap(pixmap)
        worker.signals.imageLoaded.connect(_on_detail_loaded)
        self.thread_pool.start(worker)

    def build_thumbnails(self):
        # 清空旧缩略图
        while self.thumb_layout.count():
            item = self.thumb_layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
        self.thumb_labels.clear()
        
        # 构建新缩略图
        images = self.albums[self.current_album_index]['images']
        thumb_size = QSize(96, 96)
        for idx, path in enumerate(images):
            lbl = ClickableLabel(index=idx)
            lbl.setFixedSize(96, 96)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            # 设置默认样式
            lbl.setStyleSheet(Styles.THUMB_NORMAL)
            lbl.setText("···")
            lbl.clicked.connect(self.on_thumb_clicked)
            lbl.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            def _make_ctx(label_ref=lbl, index=idx):
                def _ctx_menu(pos):
                    self.on_thumb_context_menu(index, label_ref.mapToGlobal(pos))
                return _ctx_menu
            lbl.customContextMenuRequested.connect(_make_ctx())
            self.thumb_layout.addWidget(lbl)
            self.thumb_labels.append(lbl)

            key = (path, thumb_size.width(), thumb_size.height())
            cached = self.pixmap_cache.get(key)
            if cached is not None and not cached.isNull():
                lbl.setPixmap(cached)
            else:
                worker = ImageLoadWorker(-1000 - idx, path, thumb_size)
                def _make_handler(label_ref=lbl, k=key):
                    def _handler(_, pm: QPixmap):
                        if not pm.isNull():
                            self._cache_put(k, pm)
                            label_ref.setPixmap(pm)
                    return _handler
                worker.signals.imageLoaded.connect(_make_handler())
                self.thread_pool.start(worker)
        
        # 设置当前图片的高亮
        self.update_thumb_highlight()

    def update_thumb_highlight(self):
        """更新缩略图的高亮状态"""
        for i, label in enumerate(self.thumb_labels):
            if i == self.current_image_index:
                label.setStyleSheet(Styles.THUMB_ACTIVE)
            else:
                label.setStyleSheet(Styles.THUMB_NORMAL)

    def on_thumb_clicked(self, thumb_index: int):
        self.current_image_index = thumb_index
        self.update_detail_image()
        self.update_thumb_highlight()
        self.scroll_to_current_thumb()

    def scroll_to_current_thumb(self):
        """滚动缩略图容器，使当前图片的缩略图居中显示"""
        if self.current_album_index < 0:
            return
        
        # 计算当前缩略图的位置
        thumb_width = 96  # 缩略图宽度
        thumb_spacing = 8  # 缩略图间距
        thumb_total_width = thumb_width + thumb_spacing
        
        # 当前缩略图的起始位置
        thumb_x = self.current_image_index * thumb_total_width
        
        # 容器可见宽度
        container_width = self.thumb_container.width()
        
        # 计算滚动位置，使当前缩略图居中
        scroll_x = thumb_x - (container_width - thumb_width) // 2
        
        # 确保滚动位置在有效范围内
        max_scroll = max(0, self.thumb_layout.count() * thumb_total_width - container_width)
        scroll_x = max(0, min(scroll_x, max_scroll))
        
        # 执行滚动
        self.thumb_container.horizontalScrollBar().setValue(int(scroll_x))

    def on_detail_image_context_menu(self, pos):
        """详情页主图片的右键菜单"""
        menu = QMenu(self)
        pin_action = QAction("置顶到第一张", self)
        def _do_pin():
            self.pin_image_to_first(self.current_image_index)
        pin_action.triggered.connect(_do_pin)
        menu.addAction(pin_action)
        menu.exec(self.detail_label.mapToGlobal(pos))

    def on_album_cover_context_menu(self, album_index: int, global_pos: QPoint):
        """相册封面的右键菜单"""
        menu = QMenu(self)
        
        # 置顶选项
        pin_action = QAction("置顶相册到第一位", self)
        def _do_pin():
            self.pin_album_to_first(album_index)
        pin_action.triggered.connect(_do_pin)
        menu.addAction(pin_action)
        
        # 跳转到原始网页选项
        if album_index < len(self.albums):
            album = self.albums[album_index]
            original_url = album.get('original_url')
            if original_url:
                jump_action = QAction("🌐 跳转到原始网页", self)
                jump_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_FileDialogDetailedView))
                def _do_jump():
                    self.open_url_in_browser(original_url)
                jump_action.triggered.connect(_do_jump)
                menu.addAction(jump_action)
        
        # 分隔线
        menu.addSeparator()
        
        # 删除选项
        delete_action = QAction("🗑️ 删除相册", self)
        # QAction不支持setStyleSheet，使用其他方式突出显示
        delete_action.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCancelButton))
        def _do_delete():
            self.delete_album(album_index)
        delete_action.triggered.connect(_do_delete)
        menu.addAction(delete_action)
        
        menu.exec(global_pos)

    def pin_album_to_first(self, album_index: int):
        """将相册置顶到第一位"""
        if album_index < 0 or album_index >= len(self.albums):
            return
        
        album = self.albums[album_index]
        album_name = album['name']
        album_path = album['path']
        
        # 获取父目录
        parent_dir = os.path.dirname(album_path)
        
        # 生成当前时间戳（毫秒级，确保唯一性）
        import time
        timestamp = int(time.time() * 1000)
        
        # 如果当前文件夹已经有时间戳前缀，先去掉
        original_name = album_name
        if album_name.count('_') >= 2:  # 时间戳格式：1234567890_原名称
            try:
                # 检查第一个下划线前是否是数字（时间戳）
                first_underscore = album_name.find('_')
                if first_underscore > 0:
                    potential_timestamp = album_name[:first_underscore]
                    int(potential_timestamp)  # 如果能转换为整数，说明是时间戳
                    original_name = album_name[first_underscore + 1:]  # 去掉时间戳前缀
            except ValueError:
                pass  # 不是时间戳格式，保持原名
        
        # 生成新的文件夹名：时间戳_原名称
        new_name = f"{timestamp}_{original_name}"
        
        try:
            old_path = album_path
            new_path = os.path.join(parent_dir, new_name)
            os.rename(old_path, new_path)
        except Exception as e:
            QMessageBox.warning(self, "置顶失败", f"无法重命名文件夹:\n{e}")
            return
        
        # 刷新相册列表
        self.albums = self.load_albums()
        self.total_pages = math.ceil(len(self.albums) / self.items_per_page)
        
        # 重新显示当前页面
        self.display_current_page()
        
    def delete_album(self, album_index: int):
        """删除相册"""
        if album_index < 0 or album_index >= len(self.albums):
            return
        
        album = self.albums[album_index]
        album_name = album['name']
        album_path = album['path']
        
        # 确认删除对话框
        reply = QMessageBox.question(
            self, 
            "确认删除相册", 
            f"确定要删除相册 '{album_name}' 吗？\n\n此操作将永久删除文件夹及其所有内容，无法恢复！",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No  # 默认选择"否"
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # 删除文件夹
                import shutil
                shutil.rmtree(album_path)
                
                # 重新加载相册列表
                self.albums = self.load_albums()
                self.total_pages = math.ceil(len(self.albums) / self.items_per_page)
                
                # 调整当前页面
                if self.current_page > self.total_pages and self.total_pages > 0:
                    self.current_page = self.total_pages
                elif self.total_pages == 0:
                    self.current_page = 1
                
                # 重新显示当前页面
                self.display_current_page()
                
                # 更新窗口标题
                self.setWindowTitle(f"🖼️ 图片分页展示 - 共{len(self.albums)}个相册")
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "删除失败", 
                    f"删除相册时发生错误:\n{e}"
                )

    def on_thumb_context_menu(self, thumb_index: int, global_pos: QPoint):
        menu = QMenu(self)
        pin_action = QAction("置顶到第一张", self)
        def _do_pin():
            self.pin_image_to_first(thumb_index)
        pin_action.triggered.connect(_do_pin)
        menu.addAction(pin_action)
        menu.exec(global_pos)

    def pin_image_to_first(self, thumb_index: int):
        if self.current_album_index < 0:
            return
        album = self.albums[self.current_album_index]
        images = album['images']
        if thumb_index < 0 or thumb_index >= len(images):
            return
        path = images[thumb_index]
        folder, filename = os.path.split(path)
        # 生成当前时间戳（毫秒级，确保唯一性）
        import time
        timestamp = int(time.time() * 1000)
        
        # 如果当前文件已经有时间戳前缀，先去掉
        original_filename = filename
        if filename.count('_') >= 2:  # 时间戳格式：1234567890_原文件名
            try:
                # 检查第一个下划线前是否是数字（时间戳）
                first_underscore = filename.find('_')
                if first_underscore > 0:
                    potential_timestamp = filename[:first_underscore]
                    int(potential_timestamp)  # 如果能转换为整数，说明是时间戳
                    original_filename = filename[first_underscore + 1:]  # 去掉时间戳前缀
            except ValueError:
                pass  # 不是时间戳格式，保持原名
        
        # 生成新的文件名：时间戳_原文件名
        new_filename = f"{timestamp}_{original_filename}"
        new_path = os.path.join(folder, new_filename)
        
        try:
            os.rename(path, new_path)
        except Exception as e:
            QMessageBox.warning(self, "置顶失败", f"无法重命名文件:\n{e}")
            return
        # 刷新相册图片顺序与封面
        album['images'] = self.find_images_in_folder(folder)
        album['cover'] = album['images'][0] if album['images'] else ''
        # 当前索引调整为第一张
        self.current_image_index = 0
        # 重建缩略图与主图
        self.build_thumbnails()
        self.update_detail_image()


app = QApplication([])
myapp = MyApp()
myapp.show()

sys.exit(app.exec())
