from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.models import TestExecution, TestResult
from app.schemas.schemas import (
    TestExecutionCreate, 
    TestExecutionResponse, 
    TestExecutionUpdate, 
    TestResultCreate,
    TestResultResponse,
    PaginatedResponse
)

router = APIRouter()

@router.post("/", response_model=TestExecutionResponse, status_code=status.HTTP_201_CREATED)
def create_test_execution(test_execution: TestExecutionCreate, db: Session = Depends(get_db)):
    """創建新的測試執行記錄"""
    db_test_execution = TestExecution(**test_execution.dict())
    db.add(db_test_execution)
    db.commit()
    db.refresh(db_test_execution)
    return db_test_execution

@router.get("/", response_model=PaginatedResponse)
def get_test_executions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    test_plan_id: Optional[int] = None,
    test_case_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取測試執行記錄列表，支持分頁和篩選"""
    query = db.query(TestExecution)
    
    # 應用篩選條件
    if test_plan_id:
        query = query.filter(TestExecution.test_plan_id == test_plan_id)
    
    if test_case_id:
        query = query.filter(TestExecution.test_case_id == test_case_id)
    
    if status:
        query = query.filter(TestExecution.status == status)
    
    # 計算總數
    total = query.count()
    
    # 應用分頁
    test_executions = query.offset(skip).limit(limit).all()
    
    # 計算總頁數
    pages = (total + limit - 1) // limit if total > 0 else 0
    
    return {
        "items": test_executions,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": pages
    }

@router.get("/{execution_id}", response_model=TestExecutionResponse)
def get_test_execution(execution_id: int, db: Session = Depends(get_db)):
    """根據ID獲取測試執行記錄詳情"""
    db_test_execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if db_test_execution is None:
        raise HTTPException(status_code=404, detail="測試執行記錄不存在")
    return db_test_execution

@router.put("/{execution_id}", response_model=TestExecutionResponse)
def update_test_execution(
    execution_id: int, 
    test_execution: TestExecutionUpdate, 
    db: Session = Depends(get_db)
):
    """更新測試執行記錄信息"""
    db_test_execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if db_test_execution is None:
        raise HTTPException(status_code=404, detail="測試執行記錄不存在")
    
    # 更新非空字段
    update_data = test_execution.dict(exclude_unset=True)
    
    # 如果狀態改變為已完成，更新執行時間
    if "status" in update_data and update_data["status"] in ["passed", "failed", "skipped"]:
        if not db_test_execution.executed_at:
            update_data["executed_at"] = datetime.now()
    
    for key, value in update_data.items():
        setattr(db_test_execution, key, value)
    
    db.commit()
    db.refresh(db_test_execution)
    return db_test_execution

@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_execution(execution_id: int, db: Session = Depends(get_db)):
    """刪除測試執行記錄"""
    db_test_execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if db_test_execution is None:
        raise HTTPException(status_code=404, detail="測試執行記錄不存在")
    
    db.delete(db_test_execution)
    db.commit()
    return None

# 測試結果相關路由
@router.post("/{execution_id}/results", response_model=TestResultResponse)
def add_test_result(
    execution_id: int,
    test_result: TestResultCreate,
    db: Session = Depends(get_db)
):
    """添加測試步驟結果"""
    # 檢查測試執行記錄是否存在
    db_test_execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if db_test_execution is None:
        raise HTTPException(status_code=404, detail="測試執行記錄不存在")
    
    # 創建測試結果
    db_test_result = TestResult(**test_result.dict(), test_execution_id=execution_id)
    db.add(db_test_result)
    db.commit()
    db.refresh(db_test_result)
    
    return db_test_result

@router.get("/{execution_id}/results", response_model=List[TestResultResponse])
def get_test_results(execution_id: int, db: Session = Depends(get_db)):
    """獲取測試執行的所有步驟結果"""
    # 檢查測試執行記錄是否存在
    db_test_execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if db_test_execution is None:
        raise HTTPException(status_code=404, detail="測試執行記錄不存在")
    
    # 獲取所有測試結果
    results = db.query(TestResult).filter(TestResult.test_execution_id == execution_id).all()
    return results 