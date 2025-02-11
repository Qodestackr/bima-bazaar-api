import yaml 
import logging
from contextvars import ContextVar
from pathlib import Path  
from fastapi import Request
from pythonjsonlogger import jsonlogger

# Shared context variables
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="")
client_ip_ctx: ContextVar[str] = ContextVar("client_ip", default="")

class InsuranceLogFilter(logging.Filter):
    def filter(self, record):
        record.request_id = request_id_ctx.get()
        record.client_ip = client_ip_ctx.get()
        return True

def configure_logging():
    config_path = Path(__file__).resolve().parent.parent / "logging.yaml"
    
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        logging.config.dictConfig(config)
    
    for handler in logging.getLogger("bimabazaar").handlers:
        handler.addFilter(InsuranceLogFilter())