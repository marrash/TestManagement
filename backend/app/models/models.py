from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.db.database import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

# 測試執行狀態枚舉
class TestStatus(str, enum.Enum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    PENDING = "pending"
    BLOCKED = "blocked"

# 測試案例類型枚舉
class TestCaseType(str, enum.Enum):
    MANUAL = "manual"
    AUTOMATED = "automated"
    HYBRID = "hybrid"

# 測試優先級枚舉
class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# 測試計劃模型
class TestPlan(Base):
    __tablename__ = "test_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # 關聯
    test_executions = relationship("TestExecution", back_populates="test_plan", cascade="all, delete-orphan")

# 測試案例模型
class TestCase(Base):
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    prerequisites = Column(Text, nullable=True)
    steps = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    test_type = Column(Enum(TestCaseType), default=TestCaseType.MANUAL)
    priority = Column(Enum(Priority), default=Priority.MEDIUM)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(255), nullable=True)
    
    # 關聯
    test_executions = relationship("TestExecution", back_populates="test_case", cascade="all, delete-orphan")
    
# 測試執行模型
class TestExecution(Base):
    __tablename__ = "test_executions"
    
    id = Column(Integer, primary_key=True, index=True)
    status = Column(Enum(TestStatus), default=TestStatus.PENDING)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    executed_by = Column(String(255), nullable=True)
    duration = Column(Integer, nullable=True)  # 執行持續時間(秒)
    notes = Column(Text, nullable=True)
    test_plan_id = Column(Integer, ForeignKey("test_plans.id"))
    test_case_id = Column(Integer, ForeignKey("test_cases.id"))
    
    # 關聯
    test_plan = relationship("TestPlan", back_populates="test_executions")
    test_case = relationship("TestCase", back_populates="test_executions")
    test_results = relationship("TestResult", back_populates="test_execution", cascade="all, delete-orphan")

# 測試結果模型(詳細的測試步驟結果)
class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    step_number = Column(Integer, nullable=False)
    step_description = Column(Text, nullable=False)
    status = Column(Enum(TestStatus), nullable=False)
    screenshot_url = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"))
    
    # 關聯
    test_execution = relationship("TestExecution", back_populates="test_results")

# Jira整合模型
class JiraIntegration(Base):
    __tablename__ = "jira_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    jira_project_key = Column(String(50), nullable=False)
    jira_issue_key = Column(String(50), nullable=False)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True)
    test_execution_id = Column(Integer, ForeignKey("test_executions.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# API密鑰模型(用於外部系統集成)
class ApiKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(255), default=lambda: str(uuid.uuid4()), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 