from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.models import TestStatus, TestCaseType, Priority

# 基礎模式
class BaseSchema(BaseModel):
    class Config:
        orm_mode = True
        populate_by_name = True
        arbitrary_types_allowed = True

# 測試計劃模式
class TestPlanBase(BaseSchema):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: bool = True

class TestPlanCreate(TestPlanBase):
    pass

class TestPlanUpdate(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class TestPlanResponse(TestPlanBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 測試案例模式
class TestCaseBase(BaseSchema):
    title: str
    description: Optional[str] = None
    prerequisites: Optional[str] = None
    steps: str
    expected_result: str
    test_type: TestCaseType = TestCaseType.MANUAL
    priority: Priority = Priority.MEDIUM
    created_by: Optional[str] = None

class TestCaseCreate(TestCaseBase):
    pass

class TestCaseUpdate(BaseSchema):
    title: Optional[str] = None
    description: Optional[str] = None
    prerequisites: Optional[str] = None
    steps: Optional[str] = None
    expected_result: Optional[str] = None
    test_type: Optional[TestCaseType] = None
    priority: Optional[Priority] = None

class TestCaseResponse(TestCaseBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# 測試結果模式
class TestResultBase(BaseSchema):
    step_number: int
    step_description: str
    status: TestStatus
    screenshot_url: Optional[str] = None
    notes: Optional[str] = None

class TestResultCreate(TestResultBase):
    pass

class TestResultUpdate(BaseSchema):
    status: Optional[TestStatus] = None
    screenshot_url: Optional[str] = None
    notes: Optional[str] = None

class TestResultResponse(TestResultBase):
    id: int
    test_execution_id: int

# 測試執行模式
class TestExecutionBase(BaseSchema):
    status: TestStatus = TestStatus.PENDING
    executed_by: Optional[str] = None
    notes: Optional[str] = None
    test_plan_id: int
    test_case_id: int

class TestExecutionCreate(TestExecutionBase):
    pass

class TestExecutionUpdate(BaseSchema):
    status: Optional[TestStatus] = None
    executed_by: Optional[str] = None
    notes: Optional[str] = None
    executed_at: Optional[datetime] = None
    duration: Optional[int] = None

class TestExecutionResponse(TestExecutionBase):
    id: int
    executed_at: Optional[datetime] = None
    duration: Optional[int] = None
    test_results: List[TestResultResponse] = []

# Jira整合模式
class JiraIntegrationBase(BaseSchema):
    jira_project_key: str
    jira_issue_key: str
    test_case_id: Optional[int] = None
    test_execution_id: Optional[int] = None

class JiraIntegrationCreate(JiraIntegrationBase):
    pass

class JiraIntegrationResponse(JiraIntegrationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

# API密鑰模式
class ApiKeyBase(BaseSchema):
    name: str
    description: Optional[str] = None
    is_active: bool = True

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyResponse(ApiKeyBase):
    id: int
    key: str
    created_at: datetime

# 報告請求模式
class ReportRequest(BaseSchema):
    test_plan_id: int
    format: str = "pdf"  # pdf, html, csv

# 分頁響應
class PaginatedResponse(BaseSchema):
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int 