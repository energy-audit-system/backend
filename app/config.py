import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        "postgresql://asattorov:neda2020luba@localhost:5432/energy_audit"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = "neda2331"
    JWT_ALGORITHM = "HS256"
    JWT_EXPIRE_HOURS = 24
