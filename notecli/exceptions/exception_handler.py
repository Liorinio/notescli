from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi import Request


async def validation_exception_handler(request: Request,
    exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "code": 422,
            "message": "Validation error",
            "details": [
                error["msg"]
                for error in exc.errors()
            ]
        }
    )