from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.config.settings import settings
from app.config.logger import logger
from app.common.limiter import limiter
from app.api.user_api import router as user_router
from app.api.recharge_api import router as recharge_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    docs_url=None,       # 禁用默认docs（避免加载外网CDN报错）
    redoc_url=None,
    openapi_url="/openapi.json"
)

# 限流
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# ============ 全局异常处理 ============
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"未捕获异常: {request.method} {request.url.path} -> {exc}")
    return JSONResponse(
        status_code=200,
        content={"code": 500, "msg": f"服务器内部错误: {exc}", "data": None},
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=200,
        content={"code": 400, "msg": str(exc), "data": None},
    )

# 路由注册
app.include_router(user_router, prefix="/api/user", tags=["用户接口"])
app.include_router(recharge_router, prefix="/api/recharge", tags=["充值接口"])

# 离线Swagger（不依赖外网CDN）
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - API文档",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/")
async def root():
    return {"code": 200, "msg": "服务运行正常", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    logger.info(f"服务启动：http://{settings.HOST}:{settings.PORT}")
    uvicorn.run(app, host=settings.HOST, port=settings.PORT)
