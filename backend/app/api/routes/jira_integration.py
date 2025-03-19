from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
from app.db.database import get_db
from app.models.models import JiraIntegration, TestExecution, TestCase
from app.schemas.schemas import JiraIntegrationCreate, JiraIntegrationResponse

# Jira API相關
from jira import JIRA
from jira.exceptions import JIRAError

router = APIRouter()

# 獲取Jira客戶端
def get_jira_client():
    jira_url = os.getenv("JIRA_URL")
    jira_username = os.getenv("JIRA_USERNAME")
    jira_api_token = os.getenv("JIRA_API_TOKEN")
    
    if not jira_url or not jira_username or not jira_api_token:
        raise HTTPException(
            status_code=500,
            detail="Jira整合未配置，請設置JIRA_URL、JIRA_USERNAME和JIRA_API_TOKEN環境變量"
        )
    
    try:
        jira = JIRA(
            server=jira_url,
            basic_auth=(jira_username, jira_api_token)
        )
        return jira
    except JIRAError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Jira連接失敗: {str(e)}"
        )

@router.post("/link", response_model=JiraIntegrationResponse)
def link_to_jira(
    integration: JiraIntegrationCreate,
    db: Session = Depends(get_db),
    jira: JIRA = Depends(get_jira_client)
):
    """將測試案例或測試執行關聯到Jira問題"""
    # 檢查Jira問題是否存在
    try:
        issue = jira.issue(integration.jira_issue_key)
    except JIRAError as e:
        if e.status_code == 404:
            raise HTTPException(status_code=404, detail=f"Jira問題 {integration.jira_issue_key} 不存在")
        raise HTTPException(status_code=500, detail=f"Jira API錯誤: {str(e)}")
    
    # 檢查測試案例是否存在（如果提供了）
    if integration.test_case_id:
        test_case = db.query(TestCase).filter(TestCase.id == integration.test_case_id).first()
        if not test_case:
            raise HTTPException(status_code=404, detail=f"測試案例 ID {integration.test_case_id} 不存在")
    
    # 檢查測試執行是否存在（如果提供了）
    if integration.test_execution_id:
        test_execution = db.query(TestExecution).filter(TestExecution.id == integration.test_execution_id).first()
        if not test_execution:
            raise HTTPException(status_code=404, detail=f"測試執行 ID {integration.test_execution_id} 不存在")
    
    # 創建關聯記錄
    db_integration = JiraIntegration(**integration.dict())
    db.add(db_integration)
    db.commit()
    db.refresh(db_integration)
    
    return db_integration

@router.get("/links", response_model=List[JiraIntegrationResponse])
def get_jira_links(
    test_case_id: Optional[int] = None,
    test_execution_id: Optional[int] = None,
    jira_issue_key: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """獲取Jira關聯記錄"""
    query = db.query(JiraIntegration)
    
    if test_case_id:
        query = query.filter(JiraIntegration.test_case_id == test_case_id)
    
    if test_execution_id:
        query = query.filter(JiraIntegration.test_execution_id == test_execution_id)
    
    if jira_issue_key:
        query = query.filter(JiraIntegration.jira_issue_key == jira_issue_key)
    
    return query.all()

@router.delete("/links/{integration_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_jira_link(integration_id: int, db: Session = Depends(get_db)):
    """刪除Jira關聯記錄"""
    db_integration = db.query(JiraIntegration).filter(JiraIntegration.id == integration_id).first()
    if not db_integration:
        raise HTTPException(status_code=404, detail="關聯記錄不存在")
    
    db.delete(db_integration)
    db.commit()
    return None

@router.post("/update-status/{execution_id}")
def update_jira_status(
    execution_id: int,
    db: Session = Depends(get_db),
    jira: JIRA = Depends(get_jira_client)
):
    """更新Jira問題狀態，基於測試執行結果"""
    # 獲取測試執行
    execution = db.query(TestExecution).filter(TestExecution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="測試執行不存在")
    
    # 檢查是否有關聯的Jira問題
    integrations = db.query(JiraIntegration).filter(JiraIntegration.test_execution_id == execution_id).all()
    if not integrations:
        raise HTTPException(status_code=404, detail="沒有找到關聯的Jira問題")
    
    results = []
    for integration in integrations:
        try:
            issue = jira.issue(integration.jira_issue_key)
            
            # 根據測試結果添加評論
            if execution.status == "passed":
                comment = f"✅ 測試通過: 執行ID {execution_id} 已成功通過測試。"
                transition_name = "Done"  # 假設的工作流轉換名稱
            elif execution.status == "failed":
                comment = f"❌ 測試失敗: 執行ID {execution_id} 未通過測試。請檢查詳細結果。"
                transition_name = "Reopen"  # 假設的工作流轉換名稱
            else:
                comment = f"⚠️ 測試狀態: 執行ID {execution_id} 的狀態為 {execution.status}。"
                transition_name = None
            
            # 添加評論
            jira.add_comment(issue, comment)
            
            # 嘗試轉換問題狀態（這需要根據您的Jira工作流配置）
            if transition_name:
                try:
                    # 獲取可用的轉換
                    transitions = jira.transitions(issue)
                    transition_id = None
                    
                    # 查找匹配的轉換
                    for t in transitions:
                        if t['name'].lower() == transition_name.lower():
                            transition_id = t['id']
                            break
                    
                    if transition_id:
                        jira.transition_issue(issue, transition_id)
                        results.append({
                            "issue_key": integration.jira_issue_key,
                            "comment_added": True,
                            "status_updated": True,
                            "new_status": transition_name
                        })
                    else:
                        results.append({
                            "issue_key": integration.jira_issue_key,
                            "comment_added": True,
                            "status_updated": False,
                            "error": f"無法找到名為 '{transition_name}' 的轉換"
                        })
                except JIRAError as e:
                    results.append({
                        "issue_key": integration.jira_issue_key,
                        "comment_added": True,
                        "status_updated": False,
                        "error": str(e)
                    })
            else:
                results.append({
                    "issue_key": integration.jira_issue_key,
                    "comment_added": True,
                    "status_updated": False
                })
                
        except JIRAError as e:
            results.append({
                "issue_key": integration.jira_issue_key,
                "error": str(e),
                "comment_added": False,
                "status_updated": False
            })
    
    return {"results": results} 