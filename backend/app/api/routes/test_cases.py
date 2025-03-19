from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import TestCase
from app.schemas.schemas import TestCaseCreate, TestCaseResponse, TestCaseUpdate, PaginatedResponse

router = APIRouter()

@router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
def create_test_case(test_case: TestCaseCreate, db: Session = Depends(get_db)):
    """創建新的測試案例"""
    db_test_case = TestCase(**test_case.dict())
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

@router.get("/", response_model=PaginatedResponse)
def get_test_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    title: Optional[str] = None,
    test_type: Optional[str] = None,
    priority: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取測試案例列表，支持分頁和篩選"""
    query = db.query(TestCase)
    
    # 應用篩選條件
    if title:
        query = query.filter(TestCase.title.ilike(f"%{title}%"))
    
    if test_type:
        query = query.filter(TestCase.test_type == test_type)
    
    if priority:
        query = query.filter(TestCase.priority == priority)
    
    # 計算總數
    total = query.count()
    
    # 應用分頁
    test_cases = query.offset(skip).limit(limit).all()
    
    # 計算總頁數
    pages = (total + limit - 1) // limit if total > 0 else 0
    
    return {
        "items": test_cases,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": pages
    }

@router.get("/{test_case_id}", response_model=TestCaseResponse)
def get_test_case(test_case_id: int, db: Session = Depends(get_db)):
    """根據ID獲取測試案例詳情"""
    db_test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if db_test_case is None:
        raise HTTPException(status_code=404, detail="測試案例不存在")
    return db_test_case

@router.put("/{test_case_id}", response_model=TestCaseResponse)
def update_test_case(
    test_case_id: int, 
    test_case: TestCaseUpdate, 
    db: Session = Depends(get_db)
):
    """更新測試案例信息"""
    db_test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if db_test_case is None:
        raise HTTPException(status_code=404, detail="測試案例不存在")
    
    # 更新非空字段
    update_data = test_case.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_test_case, key, value)
    
    db.commit()
    db.refresh(db_test_case)
    return db_test_case

@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    """刪除測試案例"""
    db_test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if db_test_case is None:
        raise HTTPException(status_code=404, detail="測試案例不存在")
    
    db.delete(db_test_case)
    db.commit()
    return None 