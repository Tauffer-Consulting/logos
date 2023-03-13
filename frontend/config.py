import os
import json

class Config:
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    COHERE_API_KEY = os.environ.get("COHERE_API_KEY")
    QDRANT_HOST = os.environ.get("QDRANT_HOST")
    QDRANT_PORT = os.environ.get("QDRANT_PORT")
    QDRANT_API_KEY = os.environ.get("QDRANT_API_KEY")

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