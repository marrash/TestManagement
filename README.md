
# 測試管理平台

這是一個完整的測試管理解決方案，用於追蹤、組織和報告測試計劃、測試案例和測試執行。該平台提供了直觀的界面來管理測試資源並生成測試報告。

## 技術棧

### 後端
- **框架**: FastAPI
- **數據庫**: PostgreSQL
- **遷移工具**: Alembic
- **報告生成**: ReportLab, Jinja2
- **數據處理**: Pandas

### 前端
- **框架**: Next.js (React)
- **狀態管理**: React Query
- **UI框架**: Tailwind CSS
- **圖表**: Recharts
- **圖標**: Heroicons

## 系統要求

- Python 3.8+
- Node.js 14+
- PostgreSQL 14+
- MacOS/Linux/Windows

## 安裝與設置

### 克隆倉庫

```bash
git clone <repository-url>
cd TestMangentent
```

### 後端設置

```bash
# 進入後端目錄
cd backend

# 創建虛擬環境
python -m venv venv
source venv/bin/activate  # 在Windows上使用 venv\Scripts\activate

# 安裝依賴
pip install -r requirements.txt

# 安裝額外依賴
pip install reportlab jinja2 pandas

# 數據庫設置
brew services start postgresql@14  # MacOS使用Homebrew
# 或使用其他平台對應的PostgreSQL啟動命令

# 創建數據庫
createdb testmanagement

# 初始化Alembic（如果尚未完成）
alembic init alembic

# 設置數據庫URL
# 編輯 alembic.ini 將 sqlalchemy.url 設置為：
# postgresql://當前用戶名:@localhost/testmanagement

# 創建並應用遷移
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 前端設置

```bash
# 進入前端目錄
cd frontend

# 安裝依賴
npm install
```

## 運行應用

### 啟動後端

```bash
cd backend
source venv/bin/activate  # 如果尚未激活虛擬環境
uvicorn app.main:app --reload --port 8010
```

成功啟動後，終端將顯示：
```
INFO:     Will watch for changes in these directories: ['/Users/marrash/TestMangentent/backend']
INFO:     Uvicorn running on http://127.0.0.1:8010 (Press CTRL+C to quit)
INFO:     Started reloader process [78966] using StatReload
INFO:     Started server process [78972]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 啟動前端

```bash
cd frontend
npm run dev
```

成功啟動後，終端將顯示：
```
> test-management-frontend@0.1.0 dev
> next dev
   ▲ Next.js 14.0.0
   - Local:        http://localhost:3000
 ✓ Ready in 1020ms
```

## 使用指南

- **前端應用**: http://localhost:3000
- **API文檔**: http://localhost:8010/docs
- **API健康檢查**: http://localhost:8010/ping

## 主要功能

- 測試計劃管理
- 測試案例創建與組織
- 測試執行記錄
- 報告生成
- 儀表板與統計
- Jira整合（開發中）

## 項目結構

```
TestMangentent/
├── backend/                  # 後端代碼
│   ├── alembic/              # 數據庫遷移
│   ├── app/                  # 主應用目錄
│   │   ├── db/               # 數據庫配置
│   │   ├── models/           # 數據模型
│   │   ├── routes/           # API路由
│   │   ├── services/         # 業務邏輯
│   │   └── main.py           # 應用入口
│   └── requirements.txt      # 依賴清單
│
└── frontend/                 # 前端代碼
    ├── components/           # React組件
    ├── pages/                # 頁面
    ├── services/             # API服務
    ├── styles/               # CSS樣式
    └── public/               # 靜態資源
```

## 開發指南

### 後端開發

- 添加新路由: 在`app/routes/`目錄創建新文件
- 更新數據模型: 編輯`app/models/models.py`並創建新遷移
- 數據庫遷移: 使用`alembic revision --autogenerate -m "變更描述"`

### 前端開發

- 添加新頁面: 在`pages/`目錄下創建新文件
- 添加新組件: 在`components/`目錄下創建新文件
- API集成: 在`services/api.js`中添加新的API調用

<img width="1510" alt="image" src="https://github.com/user-attachments/assets/93f0870e-b1c9-426b-96d3-a886bae04d79" />


## 故障排除

- **端口被佔用**: 使用`lsof -i :端口號`檢查，更換端口或終止進程
- **數據庫連接失敗**: 檢查連接URL和PostgreSQL服務狀態
- **模塊未找到**: 檢查並安裝缺失的依賴
- **前端構建錯誤**: 檢查控制台錯誤，更新依賴版本

## 許可證

[MIT](LICENSE)
