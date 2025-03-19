from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.models.models import TestPlan
from app.schemas.schemas import TestPlanCreate, TestPlanResponse, TestPlanUpdate, PaginatedResponse

router = APIRouter()

@router.post("/", response_model=TestPlanResponse, status_code=status.HTTP_201_CREATED)
def create_test_plan(test_plan: TestPlanCreate, db: Session = Depends(get_db)):
    """創建新的測試計劃"""
    db_test_plan = TestPlan(**test_plan.dict())
    db.add(db_test_plan)
    db.commit()
    db.refresh(db_test_plan)
    return db_test_plan

@router.get("/", response_model=PaginatedResponse)
def get_test_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """獲取測試計劃列表，支持分頁和篩選"""
    query = db.query(TestPlan)
    
    # 根據活動狀態篩選
    if is_active is not None:
        query = query.filter(TestPlan.is_active == is_active)
    
    # 計算總數
    total = query.count()
    
    # 應用分頁
    test_plans = query.offset(skip).limit(limit).all()
    
    # 計算總頁數
    pages = (total + limit - 1) // limit if total > 0 else 0
    
    return {
        "items": test_plans,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit,
        "pages": pages
    }

@router.get("/{test_plan_id}", response_model=TestPlanResponse)
def get_test_plan(test_plan_id: int, db: Session = Depends(get_db)):
    """根據ID獲取測試計劃詳情"""
    db_test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if db_test_plan is None:
        raise HTTPException(status_code=404, detail="測試計劃不存在")
    return db_test_plan

@router.put("/{test_plan_id}", response_model=TestPlanResponse)
def update_test_plan(
    test_plan_id: int, 
    test_plan: TestPlanUpdate, 
    db: Session = Depends(get_db)
):
    """更新測試計劃信息"""
    db_test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if db_test_plan is None:
        raise HTTPException(status_code=404, detail="測試計劃不存在")
    
    # 更新非空字段
    update_data = test_plan.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_test_plan, key, value)
    
    db.commit()
    db.refresh(db_test_plan)
    return db_test_plan

@router.delete("/{test_plan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_test_plan(test_plan_id: int, db: Session = Depends(get_db)):
    """刪除測試計劃"""
    db_test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if db_test_plan is None:
        raise HTTPException(status_code=404, detail="測試計劃不存在")
    
    db.delete(db_test_plan)
    db.commit()
    return None 