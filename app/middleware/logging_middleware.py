from fastapi import Request
from uuid import uuid4
from app.app_logging import request_id_ctx, client_ip_ctx

async def logging_middleware(request: Request, call_next):
    request_id = str(uuid4())
    client_ip = request.client.host if request.client else "0.0.0.0"
    
    # Set context vars
    request_id_ctx.set(request_id)
    client_ip_ctx.set(client_ip)
    
    response = await call_next(request)
    
    # Log critical request metrics
    request.app.logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration": ... # Calculate response time
        }
    )
    return response