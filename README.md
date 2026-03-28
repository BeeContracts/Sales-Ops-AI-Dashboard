# Sales Ops AI Dashboard

A GitHub-safe Python desktop app for loading sales or operations CSV data, mapping business columns, calculating KPI summaries, and generating AI-style insights automatically.

## Features

- load CSV files
- choose business columns
- calculate totals, averages, counts, and stage/category breakdowns
- generate rule-based AI-style insight summaries
- export summary to text
- export summary to JSON
- optional LLM config example with placeholder secrets only
- fake sample data only
- recruiter-friendly local desktop GUI

## Why this project exists

Sales and operations teams often have raw CSV exports but no quick local tool for turning them into readable metrics and insights. This project combines KPI analysis with automated insight generation in a way that stays safe for public GitHub posting.

## Security / GitHub Safety

- no real API keys
- no real LLM credentials
- no real customer data
- fake sample CSV only
- optional LLM config uses placeholders like `XXXXXXXXXXXXXXXXXXXXXXXX`

## Project Structure

```bash
sales-ops-ai-dashboard/
├── sales_ops_ai_dashboard.py
├── sample_sales_ops_data.csv
├── llm_config.example.json
├── run_dashboard.bat
├── launch_dashboard.sh
├── app_icon.svg
├── app_icon.png
├── app_icon.ico
├── build_exe_instructions.md
├── .gitignore
├── requirements.txt
└── README.md
```

## How to Run

### Windows
Double-click:

```bash
run_dashboard.bat
```

### Linux / macOS
```bash
python3 sales_ops_ai_dashboard.py
```

## License

MIT
