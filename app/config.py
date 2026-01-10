import os

class Config:
    # Database configuration
    # Поддержка переменных окружения для Docker, с fallback на локальные значения
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URI',
        'postgresql://asattorov:neda2020luba@localhost:5432/energy_audit'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Security configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'neda2331')
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_EXPIRE_HOURS = int(os.getenv('JWT_EXPIRE_HOURS', 24))
