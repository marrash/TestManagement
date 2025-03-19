from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

# 導入路由模塊（暫時註釋掉）
# from app.api.routes import test_plans, test_cases, test_executions, reports, jira_integration, api_integration

app = FastAPI(
    title="測試管理平台 API",
    description="企業級測試案例管理系統的API接口",
    version="0.1.0",
)

# CORS設置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生產環境中應限制為前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊API路由（暫時註釋掉）
# app.include_router(test_plans.router, prefix="/api/test-plans", tags=["測試計劃"])
# app.include_router(test_cases.router, prefix="/api/test-cases", tags=["測試案例"])
# app.include_router(test_executions.router, prefix="/api/test-executions", tags=["測試執行"])
# app.include_router(reports.router, prefix="/api/reports", tags=["測試報告"])
# app.include_router(jira_integration.router, prefix="/api/jira", tags=["Jira整合"])
# app.include_router(api_integration.router, prefix="/api/integration", tags=["API整合"])

@app.get("/", include_in_schema=False)
async def root():
    return {"message": "歡迎使用測試管理平台API，訪問 /docs 查看API文檔"}

@app.get("/ping", include_in_schema=False)
async def ping():
    return {"status": "ok", "message": "服務正常運行"}

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="測試管理平台 API 文檔",
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 