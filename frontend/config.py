import os
import json

class Config:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
    QDRANT_URL = os.environ.get("QDRANT_URL")
    QDRANT_PORT = os.environ.get("QDRANT_PORT")

class DevConfig(Config):
    DEBUG = True
    HOST = '0.0.0.0'
    PORT = 8050

class ProdConfig(Config):
    DEBUG = False
    HOST = '0.0.0.0'
    PORT = 8050

def get_stage_config():
    config_map = {
        "dev": DevConfig,
        "prod": ProdConfig
    }
    stage = os.environ.get('STAGE', 'dev')
    return config_map[stage]()

config: Config = get_stage_config()