from fastapi import Request, HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.main import application
from app.utils.exceptions import ErrorResponse


@application.exception_handler(ErrorResponse)
async def api_error_response_handler(
    request: Request, exc: ErrorResponse
) -> JSONResponse:
    """Exception handler for API Error responses."""
    return JSONResponse(
        {"status_code": exc.status, "message": exc.message},
        status_code=exc.status,
    )


@application.exception_handler(HTTPException)
async def http_error_response_handler(
    _request: Request, exc: HTTPException
) -> JSONResponse:
    """Exception handler for Default HTTP Error responses."""
    return JSONResponse(
        {"status_code": exc.status_code, "message": exc.detail},
        status_code=exc.status_code,
    )


@application.exception_handler(RequestValidationError)
async def validation_error_response_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    """Exception handler for Validation Error responses."""
    errors = [
        f"{err['loc'][-1]} {err['msg']} {ctx.get('error', '') if (ctx := err.get('ctx', {})) else ''}"
        for err in exc.errors()
    ]

    return JSONResponse(
        jsonable_encoder(
            {
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "message": "Validation Errors",
                "errors": errors,
            }
        ),
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
    )


@application.exception_handler(Exception)
async def generic_error_response_handler(
    _request: Request, exc: Exception
) -> JSONResponse:
    """Exception handler for Generic Error responses."""
    return JSONResponse(
        {
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "message": "Something went wrong. Please try again later.",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
