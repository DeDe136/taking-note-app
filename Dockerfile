# Sử dụng Python base image
FROM python:3.13-alpine

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Copy file requirements trước (để cache layer)
COPY requirements.txt .

# Cài đặt các thư viện cần thiết
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ source code vào container
COPY . .

# Đặt biến môi trường Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port Flask
EXPOSE 5000

# Chạy ứng dụng Flask
#CMD ["flask", "run", "--host=0.0.0.0"]
CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]
