from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Response
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import os
import tempfile
from app.db.database import get_db
from app.models.models import TestPlan, TestExecution, TestCase
from app.schemas.schemas import ReportRequest
from app.services.report_service import generate_pdf_report, generate_html_report

router = APIRouter()

@router.post("/generate")
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """生成測試報告 - 異步任務"""
    # 檢查測試計劃是否存在
    test_plan = db.query(TestPlan).filter(TestPlan.id == request.test_plan_id).first()
    if not test_plan:
        raise HTTPException(status_code=404, detail="測試計劃不存在")
    
    # 創建一個任務ID
    import uuid
    task_id = str(uuid.uuid4())
    
    # 啟動背景任務生成報告
    background_tasks.add_task(
        _generate_report_task,
        test_plan_id=request.test_plan_id,
        format=request.format,
        task_id=task_id,
        db=db
    )
    
    return {
        "message": f"報告生成任務已啟動，任務ID: {task_id}",
        "task_id": task_id
    }

@router.get("/download/{test_plan_id}")
async def download_report(test_plan_id: int, format: str = "pdf", db: Session = Depends(get_db)):
    """下載測試報告"""
    # 檢查測試計劃是否存在
    test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if not test_plan:
        raise HTTPException(status_code=404, detail="測試計劃不存在")
    
    # 生成報告文件路徑
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    filename = f"test_plan_{test_plan_id}_report"
    
    if format.lower() == "pdf":
        file_path = os.path.join(reports_dir, f"{filename}.pdf")
        if not os.path.exists(file_path):
            # 即時生成報告
            file_path = generate_pdf_report(test_plan_id, db)
        return FileResponse(
            path=file_path,
            filename=f"{test_plan.name}_report.pdf",
            media_type="application/pdf"
        )
    elif format.lower() == "html":
        file_path = os.path.join(reports_dir, f"{filename}.html")
        if not os.path.exists(file_path):
            # 即時生成報告
            file_path = generate_html_report(test_plan_id, db)
        return FileResponse(
            path=file_path,
            filename=f"{test_plan.name}_report.html",
            media_type="text/html"
        )
    else:
        raise HTTPException(status_code=400, detail="不支持的報告格式，目前支持pdf和html")

@router.get("/summary/{test_plan_id}")
async def get_test_summary(test_plan_id: int, db: Session = Depends(get_db)):
    """獲取測試計劃的摘要信息，包括通過/失敗/跳過的數量"""
    # 檢查測試計劃是否存在
    test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if not test_plan:
        raise HTTPException(status_code=404, detail="測試計劃不存在")
    
    # 獲取該測試計劃下的所有測試執行
    executions = db.query(TestExecution).filter(TestExecution.test_plan_id == test_plan_id).all()
    
    # 計算統計數據
    total = len(executions)
    passed = sum(1 for e in executions if e.status == "passed")
    failed = sum(1 for e in executions if e.status == "failed")
    skipped = sum(1 for e in executions if e.status == "skipped")
    pending = sum(1 for e in executions if e.status == "pending")
    blocked = sum(1 for e in executions if e.status == "blocked")
    
    # 計算完成率
    completion_rate = (passed + failed + skipped) / total if total > 0 else 0
    pass_rate = passed / (passed + failed) if (passed + failed) > 0 else 0
    
    return {
        "test_plan": {
            "id": test_plan.id,
            "name": test_plan.name,
            "start_date": test_plan.start_date,
            "end_date": test_plan.end_date,
        },
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pending": pending,
            "blocked": blocked,
            "completion_rate": round(completion_rate * 100, 2),
            "pass_rate": round(pass_rate * 100, 2)
        }
    }

# 後台任務函數
async def _generate_report_task(test_plan_id: int, format: str, task_id: str, db: Session):
    """背景任務：生成報告"""
    try:
        if format.lower() == "pdf":
            generate_pdf_report(test_plan_id, db)
        elif format.lower() == "html":
            generate_html_report(test_plan_id, db)
        else:
            print(f"不支持的報告格式: {format}")
    except Exception as e:
        print(f"生成報告時出錯: {str(e)}") 