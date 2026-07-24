"""
Simple logger wrapper (uses standard logging).
"""

import logging
from config import CONFIG

logging.basicConfig(level=CONFIG.get("log_level", "INFO"))
logger = logging.getLogger("ShadowC2")
