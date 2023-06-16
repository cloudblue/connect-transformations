from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def custom_http_exception_handler(request, exc):
    errors = exc.errors()
    data = errors[0]
    key = '.'.join(data['loc'][1:])
    return JSONResponse({'error': data['msg'] + f' ({key})'}, status_code=400)


class CustomExceptionHandlers:
    @classmethod
    def get_exception_handlers(cls, exception_handlers):
        exception_handlers[RequestValidationError] = custom_http_exception_handler
        return exception_handlers
