# Build a Windows .exe for Sales Ops AI Dashboard

## 1) Open terminal in the project folder

```bash
cd path\to\sales-ops-ai-dashboard
```

## 2) Optional virtual environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 3) Install PyInstaller

```bash
pip install pyinstaller
```

## 4) Build the .exe

```bash
pyinstaller --onefile --windowed --name SalesOpsAIDashboard --icon app_icon.ico sales_ops_ai_dashboard.py
```

## 5) Finished executable

```bash
dist\SalesOpsAIDashboard.exe
```
