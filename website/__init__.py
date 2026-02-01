# __init__.py

import os # <-- 1. Thêm import này
import random # <-- Thêm import random
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

# 1. Danh sách 20 màu
COLOR_LIST = [
    '#E57373',  # Red
    '#81C784',  # Green
    '#64B5F6',  # Blue
    '#FFD54F',  # Yellow
    '#BA68C8',  # Purple
    '#FF8A65',  # Orange
    '#4DB6AC',  # Teal
    '#D4E157',  # Lime
    '#7986CB',  # Indigo
    '#F06292',  # Pink
    '#4DD0E1',  # Cyan
    '#FF7043',  # Deep Orange
    '#AED581',  # Light Green
    '#9575CD',  # Deep Purple
    '#4FC3F7',  # Light Blue
    '#FFC107',  # Amber
    '#A1887F',  # Brown
    '#9E9E9E',  # Grey
    '#78909C',  # Blue Grey
    '#EF5350'   # Bright Red
]

# 2. Hàm lấy màu (Giữ nguyên)
def get_server_color():
    """
    Lấy màu cho server.
    Ưu tiên 1: Lấy từ biến môi trường 'SERVER_COLOR'.
    Ưu tiên 2: Nếu không có, chọn ngẫu nhiên một màu.
    """
    color = os.environ.get('SERVER_COLOR')
    if color:
        return color
    return random.choice(COLOR_LIST)

# 3. Đặt màu MỘT LẦN DUY NHẤT khi server khởi động (Giữ nguyên)
SERVER_COLOR = get_server_color()
print(f"🎨 Server color được chọn: {SERVER_COLOR}")  # Debug log

# 4. Lưu màu vào file để đảm bảo cố định trong suốt session
COLOR_FILE = '/tmp/server_color.txt'

def save_server_color():
    """Lưu màu vào file"""
    with open(COLOR_FILE, 'w') as f:
        f.write(SERVER_COLOR)

def get_fixed_server_color():
    """Trả về màu cố định đã được chọn khi khởi động"""
    try:
        # Thử đọc từ file trước
        with open(COLOR_FILE, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        # Nếu file không tồn tại, lưu màu hiện tại
        save_server_color()
        return SERVER_COLOR

# Lưu màu vào file khi module được import
save_server_color()

db = SQLAlchemy()

# 2. Lấy thông tin kết nối từ biến môi trường
# DB_USERNAME = os.environ.get("DB_USER")
# DB_PASSWORD = os.environ.get("DB_PASSWORD")
# DB_ENDPOINT = os.environ.get("DB_ENDPOINT") # Đây sẽ là tên service "db" trong Docker
# DB_NAME = os.environ.get("DB_NAME")
DATABASE_URI = os.environ.get("DATABASE_URI")

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'taking_note_app_secret_key'
    
    # 3. Tạo chuỗi kết nối MySQL
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI
    
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .models import User, Note
    
    with app.app_context():
        db.create_all() # Lệnh này sẽ tự tạo các bảng trong MySQL

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    @app.context_processor
    def inject_server_color():
        """Tiêm biến server_color vào mọi template"""
        # Sử dụng màu từ file (cố định trong suốt container lifecycle)
        fixed_color = get_fixed_server_color()
        print(f"🔍 Injecting server color: {fixed_color}")
        return dict(server_color=fixed_color)

    return app