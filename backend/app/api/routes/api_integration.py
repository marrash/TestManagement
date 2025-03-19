from fastapi import APIRouter, Depends, HTTPException, Header, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.db.database import get_db
from app.models.models import ApiKey, TestCase, TestExecution, TestResult, TestPlan, TestStatus
from app.schemas.schemas import TestExecutionCreate, TestResultCreate

router = APIRouter()

# API密鑰認證
async def verify_api_key(x_api_key: str = Header(...), db: Session = Depends(get_db)):
    api_key = db.query(ApiKey).filter(ApiKey.key == x_api_key, ApiKey.is_active == True).first()
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="無效的API密鑰"
        )
    return api_key

@router.post("/api-keys")
async def create_api_key(name: str, description: Optional[str] = None, db: Session = Depends(get_db)):
    """創建新的API密鑰（需管理員權限）"""
    # 在真實系統中，這裡應該有權限檢查
    
    api_key = ApiKey(name=name, description=description)
    db.add(api_key)
    db.commit()
    db.refresh(api_key)
    
    return {
        "id": api_key.id,
        "key": api_key.key,
        "name": api_key.name,
        "created_at": api_key.created_at
    }

@router.get("/api-keys")
async def list_api_keys(db: Session = Depends(get_db)):
    """列出所有API密鑰（需管理員權限）"""
    # 在真實系統中，這裡應該有權限檢查
    
    api_keys = db.query(ApiKey).all()
    return [
        {
            "id": key.id,
            "key": key.key,
            "name": key.name,
            "description": key.description,
            "is_active": key.is_active,
            "created_at": key.created_at
        }
        for key in api_keys
    ]

@router.delete("/api-keys/{key_id}")
async def delete_api_key(key_id: int, db: Session = Depends(get_db)):
    """停用API密鑰（需管理員權限）"""
    # 在真實系統中，這裡應該有權限檢查
    
    api_key = db.query(ApiKey).filter(ApiKey.id == key_id).first()
    if not api_key:
        raise HTTPException(status_code=404, detail="API密鑰不存在")
    
    api_key.is_active = False
    db.commit()
    
    return {"message": "API密鑰已停用"}

@router.post("/test-results/batch")
async def upload_test_results(
    data: Dict[str, Any],
    background_tasks: BackgroundTasks,
    api_key: ApiKey = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """批量上傳測試結果
    
    要求的JSON格式:
    {
        "test_plan_id": 1,
        "results": [
            {
                "test_case_id": 1,
                "status": "passed",
                "duration": 120,
                "executed_by": "automation",
                "notes": "自動化測試執行",
                "steps": [
                    {
                        "step_number": 1,
                        "step_description": "步驟1",
                        "status": "passed",
                        "screenshot_url": "http://example.com/screenshot1.png",
                        "notes": "步驟執行成功"
                    }
                ]
            }
        ]
    }
    """
    # 驗證測試計劃存在
    test_plan_id = data.get("test_plan_id")
    if not test_plan_id:
        raise HTTPException(status_code=400, detail="缺少test_plan_id字段")
    
    test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if not test_plan:
        raise HTTPException(status_code=404, detail=f"測試計劃ID {test_plan_id} 不存在")
    
    # 驗證請求格式
    results = data.get("results", [])
    if not results:
        raise HTTPException(status_code=400, detail="results列表為空")
    
    # 在後台處理測試結果，避免長時間阻塞請求
    background_tasks.add_task(
        process_test_results,
        test_plan_id=test_plan_id,
        results=results,
        db=db
    )
    
    return {
        "message": "測試結果上傳任務已啟動",
        "test_plan_id": test_plan_id,
        "result_count": len(results)
    }

@router.post("/test-results/single")
async def upload_single_test_result(
    test_plan_id: int,
    test_case_id: int,
    status: TestStatus,
    executed_by: Optional[str] = "api",
    duration: Optional[int] = None,
    notes: Optional[str] = None,
    api_key: ApiKey = Depends(verify_api_key),
    db: Session = Depends(get_db)
):
    """上傳單個測試結果"""
    # 驗證測試計劃和測試案例存在
    test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if not test_plan:
        raise HTTPException(status_code=404, detail=f"測試計劃ID {test_plan_id} 不存在")
    
    test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail=f"測試案例ID {test_case_id} 不存在")
    
    # 創建測試執行記錄
    test_execution = TestExecution(
        status=status,
        executed_at=datetime.now(),
        executed_by=executed_by,
        duration=duration,
        notes=notes,
        test_plan_id=test_plan_id,
        test_case_id=test_case_id
    )
    
    db.add(test_execution)
    db.commit()
    db.refresh(test_execution)
    
    return {
        "message": "測試結果已上傳",
        "execution_id": test_execution.id,
        "status": test_execution.status
    }

# 後台處理函數
async def process_test_results(test_plan_id: int, results: List[Dict[str, Any]], db: Session):
    """處理批量測試結果"""
    try:
        for result in results:
            test_case_id = result.get("test_case_id")
            if not test_case_id:
                print(f"警告: 缺少test_case_id字段: {result}")
                continue
            
            # 檢查測試案例是否存在
            test_case = db.query(TestCase).filter(TestCase.id == test_case_id).first()
            if not test_case:
                print(f"警告: 測試案例ID {test_case_id} 不存在")
                continue
            
            # 創建測試執行記錄
            test_execution = TestExecution(
                status=result.get("status", "pending"),
                executed_at=datetime.now(),
                executed_by=result.get("executed_by", "api"),
                duration=result.get("duration"),
                notes=result.get("notes"),
                test_plan_id=test_plan_id,
                test_case_id=test_case_id
            )
            
            db.add(test_execution)
            db.flush()  # 獲取新生成的ID，但尚未提交
            
            # 處理步驟結果
            steps = result.get("steps", [])
            for step in steps:
                test_result = TestResult(
                    step_number=step.get("step_number", 0),
                    step_description=step.get("step_description", ""),
                    status=step.get("status", "pending"),
                    screenshot_url=step.get("screenshot_url"),
                    notes=step.get("notes"),
                    test_execution_id=test_execution.id
                )
                db.add(test_result)
            
            db.commit()
            
    except Exception as e:
        db.rollback()
        print(f"處理測試結果時出錯: {str(e)}") 