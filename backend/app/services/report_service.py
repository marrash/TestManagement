import os
import tempfile
from datetime import datetime
from sqlalchemy.orm import Session
from app.models.models import TestPlan, TestExecution, TestCase, TestResult
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(test_plan_id: int, db: Session) -> str:
    """生成測試計劃的PDF報告"""
    # 獲取測試計劃數據
    test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if not test_plan:
        raise ValueError(f"測試計劃ID {test_plan_id} 不存在")
    
    # 獲取測試執行數據
    executions = db.query(TestExecution).filter(TestExecution.test_plan_id == test_plan_id).all()
    
    # 計算統計數據
    total = len(executions)
    passed = sum(1 for e in executions if e.status == "passed")
    failed = sum(1 for e in executions if e.status == "failed")
    skipped = sum(1 for e in executions if e.status == "skipped")
    pending = sum(1 for e in executions if e.status == "pending")
    
    # 創建報告目錄
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # 創建PDF文件
    file_path = os.path.join(reports_dir, f"test_plan_{test_plan_id}_report.pdf")
    doc = SimpleDocTemplate(file_path, pagesize=letter)
    
    # 準備內容
    styles = getSampleStyleSheet()
    title_style = styles["Heading1"]
    heading2_style = styles["Heading2"]
    normal_style = styles["Normal"]
    
    # 創建內容元素列表
    elements = []
    
    # 標題
    elements.append(Paragraph(f"測試計劃報告: {test_plan.name}", title_style))
    elements.append(Spacer(1, 12))
    
    # 測試計劃信息
    elements.append(Paragraph("測試計劃信息", heading2_style))
    elements.append(Spacer(1, 6))
    
    plan_data = [
        ["計劃ID:", str(test_plan.id)],
        ["名稱:", test_plan.name],
        ["描述:", test_plan.description or "無"],
        ["開始日期:", test_plan.start_date.strftime("%Y-%m-%d") if test_plan.start_date else "未設置"],
        ["結束日期:", test_plan.end_date.strftime("%Y-%m-%d") if test_plan.end_date else "未設置"],
        ["創建時間:", test_plan.created_at.strftime("%Y-%m-%d %H:%M:%S")],
    ]
    
    plan_table = Table(plan_data, colWidths=[100, 400])
    plan_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(plan_table)
    elements.append(Spacer(1, 12))
    
    # 測試執行摘要
    elements.append(Paragraph("測試執行摘要", heading2_style))
    elements.append(Spacer(1, 6))
    
    # 計算完成率和通過率
    completion_rate = (passed + failed + skipped) / total if total > 0 else 0
    pass_rate = passed / (passed + failed) if (passed + failed) > 0 else 0
    
    summary_data = [
        ["總測試案例數:", str(total)],
        ["通過:", str(passed)],
        ["失敗:", str(failed)],
        ["跳過:", str(skipped)],
        ["待執行:", str(pending)],
        ["完成率:", f"{round(completion_rate * 100, 2)}%"],
        ["通過率:", f"{round(pass_rate * 100, 2)}%"],
    ]
    
    summary_table = Table(summary_data, colWidths=[100, 400])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))
    
    # 詳細測試結果
    if executions:
        elements.append(Paragraph("詳細測試結果", heading2_style))
        elements.append(Spacer(1, 6))
        
        for execution in executions:
            # 獲取測試案例信息
            test_case = db.query(TestCase).filter(TestCase.id == execution.test_case_id).first()
            if not test_case:
                continue
            
            # 測試案例標題
            elements.append(Paragraph(f"測試案例: {test_case.title}", styles["Heading3"]))
            
            # 測試案例數據
            case_data = [
                ["案例ID:", str(test_case.id)],
                ["優先級:", test_case.priority],
                ["類型:", test_case.test_type],
                ["狀態:", execution.status],
                ["執行者:", execution.executed_by or "未記錄"],
                ["執行時間:", execution.executed_at.strftime("%Y-%m-%d %H:%M:%S") if execution.executed_at else "未執行"],
                ["持續時間:", f"{execution.duration} 秒" if execution.duration else "未記錄"],
            ]
            
            case_table = Table(case_data, colWidths=[100, 400])
            case_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(case_table)
            elements.append(Spacer(1, 6))
            
            # 測試結果
            if execution.test_results:
                elements.append(Paragraph("測試步驟結果:", normal_style))
                result_header = ["步驟#", "描述", "狀態", "備註"]
                result_data = [result_header]
                
                for result in sorted(execution.test_results, key=lambda x: x.step_number):
                    result_data.append([
                        str(result.step_number),
                        result.step_description,
                        result.status,
                        result.notes or ""
                    ])
                
                result_table = Table(result_data, colWidths=[40, 260, 80, 120])
                result_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(result_table)
            
            elements.append(Spacer(1, 12))
    
    # 生成PDF
    doc.build(elements)
    
    return file_path

def generate_html_report(test_plan_id: int, db: Session) -> str:
    """生成測試計劃的HTML報告"""
    # 獲取測試計劃數據
    test_plan = db.query(TestPlan).filter(TestPlan.id == test_plan_id).first()
    if not test_plan:
        raise ValueError(f"測試計劃ID {test_plan_id} 不存在")
    
    # 獲取測試執行數據
    executions = db.query(TestExecution).filter(TestExecution.test_plan_id == test_plan_id).all()
    
    # 計算統計數據
    total = len(executions)
    passed = sum(1 for e in executions if e.status == "passed")
    failed = sum(1 for e in executions if e.status == "failed")
    skipped = sum(1 for e in executions if e.status == "skipped")
    pending = sum(1 for e in executions if e.status == "pending")
    
    # 計算完成率和通過率
    completion_rate = (passed + failed + skipped) / total if total > 0 else 0
    pass_rate = passed / (passed + failed) if (passed + failed) > 0 else 0
    
    # 創建報告目錄
    reports_dir = os.path.join(os.getcwd(), "reports")
    os.makedirs(reports_dir, exist_ok=True)
    
    # 創建HTML文件
    file_path = os.path.join(reports_dir, f"test_plan_{test_plan_id}_report.html")
    
    # 生成HTML內容
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-TW">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>測試計劃報告: {test_plan.name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; color: #333; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            h1, h2, h3 {{ color: #2c3e50; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ padding: 12px 15px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #34495e; color: white; }}
            tr:hover {{ background-color: #f5f5f5; }}
            .summary-box {{ display: inline-block; padding: 20px; margin: 10px; background-color: #f8f9fa; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; width: 150px; }}
            .passed {{ color: #28a745; }}
            .failed {{ color: #dc3545; }}
            .skipped {{ color: #fd7e14; }}
            .pending {{ color: #6c757d; }}
            .progress-bar {{ background-color: #e9ecef; border-radius: 5px; height: 20px; margin-bottom: 10px; }}
            .progress {{ background-color: #28a745; height: 100%; border-radius: 5px; text-align: center; color: white; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>測試計劃報告: {test_plan.name}</h1>
            
            <h2>測試計劃信息</h2>
            <table>
                <tr><th>計劃ID:</th><td>{test_plan.id}</td></tr>
                <tr><th>名稱:</th><td>{test_plan.name}</td></tr>
                <tr><th>描述:</th><td>{test_plan.description or "無"}</td></tr>
                <tr><th>開始日期:</th><td>{test_plan.start_date.strftime("%Y-%m-%d") if test_plan.start_date else "未設置"}</td></tr>
                <tr><th>結束日期:</th><td>{test_plan.end_date.strftime("%Y-%m-%d") if test_plan.end_date else "未設置"}</td></tr>
                <tr><th>創建時間:</th><td>{test_plan.created_at.strftime("%Y-%m-%d %H:%M:%S")}</td></tr>
            </table>
            
            <h2>測試執行摘要</h2>
            <div>
                <div class="summary-box">
                    <h3>總計</h3>
                    <div style="font-size: 24px;">{total}</div>
                </div>
                <div class="summary-box">
                    <h3 class="passed">通過</h3>
                    <div style="font-size: 24px;" class="passed">{passed}</div>
                </div>
                <div class="summary-box">
                    <h3 class="failed">失敗</h3>
                    <div style="font-size: 24px;" class="failed">{failed}</div>
                </div>
                <div class="summary-box">
                    <h3 class="skipped">跳過</h3>
                    <div style="font-size: 24px;" class="skipped">{skipped}</div>
                </div>
                <div class="summary-box">
                    <h3 class="pending">待執行</h3>
                    <div style="font-size: 24px;" class="pending">{pending}</div>
                </div>
            </div>
            
            <h3>完成率: {round(completion_rate * 100, 2)}%</h3>
            <div class="progress-bar">
                <div class="progress" style="width: {round(completion_rate * 100)}%;">{round(completion_rate * 100)}%</div>
            </div>
            
            <h3>通過率: {round(pass_rate * 100, 2)}%</h3>
            <div class="progress-bar">
                <div class="progress" style="width: {round(pass_rate * 100)}%; background-color: {('#28a745' if pass_rate >= 0.8 else '#fd7e14' if pass_rate >= 0.6 else '#dc3545')};">
                    {round(pass_rate * 100)}%
                </div>
            </div>
    """
    
    # 詳細測試結果
    if executions:
        html_content += """
            <h2>詳細測試結果</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>測試案例</th>
                    <th>優先級</th>
                    <th>類型</th>
                    <th>狀態</th>
                    <th>執行者</th>
                    <th>執行時間</th>
                </tr>
        """
        
        for execution in executions:
            test_case = db.query(TestCase).filter(TestCase.id == execution.test_case_id).first()
            if not test_case:
                continue
                
            status_class = ""
            if execution.status == "passed":
                status_class = "passed"
            elif execution.status == "failed":
                status_class = "failed"
            elif execution.status == "skipped":
                status_class = "skipped"
            elif execution.status == "pending":
                status_class = "pending"
                
            html_content += f"""
                <tr>
                    <td>{test_case.id}</td>
                    <td>{test_case.title}</td>
                    <td>{test_case.priority}</td>
                    <td>{test_case.test_type}</td>
                    <td class="{status_class}">{execution.status}</td>
                    <td>{execution.executed_by or "未記錄"}</td>
                    <td>{execution.executed_at.strftime("%Y-%m-%d %H:%M:%S") if execution.executed_at else "未執行"}</td>
                </tr>
            """
            
        html_content += """
            </table>
        """
    
    # 結束HTML
    html_content += """
        </div>
    </body>
    </html>
    """
    
    # 寫入文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return file_path 