"""Turn exceptions into the standard error body: the @ControllerAdvice of this app."""

from http import HTTPStatus

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errors import ConflictError, NotFoundError
from app.schemas.errors import ErrorDetail, ErrorResponse


def _error_response(
    status_code: int,
    code: str,
    message: str,
    details: list[ErrorDetail] | None = None,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    body = ErrorResponse(code=code, message=message, details=details or [])
    return JSONResponse(
        status_code=status_code, content=body.model_dump(mode="json"), headers=headers
    )


async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
    return _error_response(status.HTTP_404_NOT_FOUND, "not_found", str(exc))


async def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
    return _error_response(status.HTTP_409_CONFLICT, "conflict", str(exc))


async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = [
        ErrorDetail(field=".".join(str(part) for part in error["loc"]), message=error["msg"])
        for error in exc.errors()
    ]
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "validation_error", "The request is invalid", details
    )


async def handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Errors raised by the framework itself, such as an unknown path or the wrong method."""
    code = HTTPStatus(exc.status_code).phrase.lower().replace(" ", "_")
    return _error_response(exc.status_code, code, str(exc.detail), headers=exc.headers)


async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    """Hide internal details from clients. Uvicorn still logs the full traceback."""
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "internal_error", "An unexpected error occurred"
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(NotFoundError, handle_not_found)
    app.add_exception_handler(ConflictError, handle_conflict)
    app.add_exception_handler(RequestValidationError, handle_validation_error)
    app.add_exception_handler(StarletteHTTPException, handle_http_exception)
    app.add_exception_handler(Exception, handle_unexpected_error)
