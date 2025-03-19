# 測試管理平台 - 後端API

這個項目是測試管理平台的後端API，基於FastAPI開發，提供測試案例管理、測試計劃管理、測試執行記錄和報告生成等功能。

## 技術棧

- **Python**: 3.8+
- **Web框架**: FastAPI
- **數據庫**: PostgreSQL
- **ORM**: SQLAlchemy
- **遷移工具**: Alembic
- **異步處理**: Celery + Redis
- **報告生成**: ReportLab (PDF) / HTML
- **第三方集成**: Jira API

## 功能模塊

- 測試計劃管理
- 測試案例管理
- 測試執行記錄
- 測試報告生成
- Jira整合
- 外部API整合（用於自動化測試結果上傳）

## 如何開始

### 環境準備

1. 安裝 Python 3.8+
2. 安裝 PostgreSQL
3. 創建虛擬環境（推薦）

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或者
venv\Scripts\activate  # Windows
```

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 設置數據庫

1. 創建PostgreSQL數據庫

```bash
createdb testmanagement
```

2. 設置環境變量（可選，或者修改配置文件）

```bash
export DATABASE_URL="postgresql://username:password@localhost/testmanagement"
```

### 運行數據庫遷移

```bash
alembic upgrade head
```

### 啟動服務

```bash
uvicorn app.main:app --reload
```

訪問 http://localhost:8000/docs 查看API文檔。

### 環境變量

主要的環境變量：

- `DATABASE_URL`: 數據庫連接URL
- `JIRA_URL`: Jira服務器URL（用於Jira集成）
- `JIRA_USERNAME`: Jira用戶名
- `JIRA_API_TOKEN`: Jira API令牌

## API端點

主要的API端點：

- `/api/test-plans/`: 測試計劃管理
- `/api/test-cases/`: 測試案例管理
- `/api/test-executions/`: 測試執行記錄
- `/api/reports/`: 報告生成
- `/api/jira/`: Jira整合
- `/api/integration/`: 外部API整合

## 項目結構

```
app/
├── api/              # API路由
│   └── routes/       # API端點
├── core/             # 核心配置
├── db/               # 數據庫相關
├── models/           # 數據模型
├── schemas/          # Pydantic模式
├── services/         # 業務服務
└── utils/            # 工具函數
``` 