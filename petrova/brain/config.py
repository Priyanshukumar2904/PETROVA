"""
PETROVA Brain Configuration (Backward Compatibility Bridge).
"""
from petrova.config.settings import get_config

config = get_config()
MODEL_PATH = config.get("model_path")
MODEL_NAME = config.model_name
