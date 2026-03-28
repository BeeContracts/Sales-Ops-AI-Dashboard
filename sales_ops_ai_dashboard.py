#!/usr/bin/env python3
"""Sales Ops AI Dashboard

GitHub-safe desktop app for loading CSVs, choosing columns, computing KPIs,
and generating rule-based AI-style insights with optional local LLM config placeholders.
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

APP_BG = '#0f172a'
PANEL_BG = '#111827'
TEXT = '#e5e7eb'
MUTED = '#94a3b8'
ACCENT = '#38bdf8'
BUTTON = '#1f2937'
CARD_1 = '#1d4ed8'
CARD_2 = '#0f766e'
CARD_3 = '#7c3aed'
CARD_4 = '#b45309'

LLM_CONFIG_EXAMPLE = {
    'provider': 'openai_or_claude',
    'api_key': 'XXXXXXXXXXXXXXXXXXXXXXXX',
    'model': '________________________',
    'enabled': False,
}


class SalesOpsAIDashboard:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title('Sales Ops AI Dashboard')
        self.root.geometry('1320x860')
        self.root.configure(bg=APP_BG)
        self.rows: list[dict[str, str]] = []
        self.headers: list[str] = []
        self.last_summary = None
        self._set_icon_if_available()
        self._build_ui()

    def _set_icon_if_available(self) -> None:
        icon = Path(__file__).with_name('app_icon.png')
        if icon.exists():
            try:
                photo = tk.PhotoImage(file=str(icon))
                self.root.iconphoto(True, photo)
                self._icon_ref = photo
            except Exception:
                pass

    def _button(self, parent, text, command, bold=False):
        return tk.Button(parent, text=text, command=command, bg=BUTTON, fg=TEXT, activebackground=ACCENT, activeforeground='black', relief='flat', padx=10, pady=6, font=('Segoe UI', 10, 'bold' if bold else 'normal'))

    def _card(self, parent, title, var, bg):
        frame = tk.Frame(parent, bg=bg, padx=12, pady=10)
        tk.Label(frame, text=title, bg=bg, fg=TEXT, font=('Segoe UI', 9, 'bold')).pack(anchor='w')
        tk.Label(frame, textvariable=var, bg=bg, fg='white', font=('Segoe UI', 18, 'bold')).pack(anchor='w', pady=(4, 0))
        return frame

    def _build_ui(self):
        tk.Label(self.root, text='Sales Ops AI Dashboard', font=('Segoe UI', 18, 'bold'), bg=APP_BG, fg=TEXT).pack(pady=(12, 4))
        tk.Label(self.root, text='Load a CSV, map business columns, compute KPIs, and generate AI-style insights safely.', font=('Segoe UI', 10), bg=APP_BG, fg=MUTED).pack(pady=(0, 10))

        cards = tk.Frame(self.root, bg=APP_BG)
        cards.pack(fill='x', padx=12, pady=(0, 10))
        self.total_records_var = tk.StringVar(value='0')
        self.total_value_var = tk.StringVar(value='$0.00')
        self.avg_value_var = tk.StringVar(value='$0.00')
        self.top_stage_var = tk.StringVar(value='-')
        self._card(cards, 'Total Records', self.total_records_var, CARD_1).pack(side='left', fill='x', expand=True, padx=(0, 6))
        self._card(cards, 'Total Value', self.total_value_var, CARD_2).pack(side='left', fill='x', expand=True, padx=6)
        self._card(cards, 'Average Value', self.avg_value_var, CARD_3).pack(side='left', fill='x', expand=True, padx=6)
        self._card(cards, 'Top Stage / Category', self.top_stage_var, CARD_4).pack(side='left', fill='x', expand=True, padx=(6, 0))

        controls = tk.Frame(self.root, bg=APP_BG)
        controls.pack(fill='x', padx=12, pady=(0, 10))
        self._button(controls, 'Load CSV', self.load_csv, bold=True).pack(side='left')
        self._button(controls, 'Analyze', self.run_analysis).pack(side='left', padx=8)
        self._button(controls, 'Export Summary Text', self.export_text).pack(side='left')
        self._button(controls, 'Export Summary JSON', self.export_json).pack(side='left', padx=8)
        self._button(controls, 'Show LLM Config Example', self.show_llm_example).pack(side='left')

        mapping = tk.Frame(self.root, bg=PANEL_BG, padx=12, pady=12)
        mapping.pack(fill='x', padx=12, pady=(0, 10))
        self.value_var = tk.StringVar(value='')
        self.stage_var = tk.StringVar(value='')
        self.owner_var = tk.StringVar(value='')
        self.status_var = tk.StringVar(value='')
        labels = [
            ('Value / Revenue Column', self.value_var),
            ('Stage / Category Column', self.stage_var),
            ('Owner Column (optional)', self.owner_var),
            ('Status Column (optional)', self.status_var),
        ]
        for idx, (label, var) in enumerate(labels):
            tk.Label(mapping, text=label, bg=PANEL_BG, fg=TEXT).grid(row=0, column=idx*2, sticky='w', padx=(0, 6), pady=4)
            combo = ttk.Combobox(mapping, textvariable=var, values=[], state='readonly', width=22)
            combo.grid(row=0, column=idx*2+1, sticky='ew', padx=(0, 14), pady=4)
            setattr(self, f'combo_{idx}', combo)
        for i in range(1, 8, 2):
            mapping.grid_columnconfigure(i, weight=1)

        lower = tk.Frame(self.root, bg=APP_BG)
        lower.pack(fill='both', expand=True, padx=12, pady=(0, 10))
        left = tk.Frame(lower, bg=APP_BG)
        left.pack(side='left', fill='both', expand=True, padx=(0, 8))
        right = tk.Frame(lower, bg=APP_BG)
        right.pack(side='left', fill='both', expand=True)

        tk.Label(left, text='CSV Preview', font=('Segoe UI', 11, 'bold'), bg=APP_BG, fg=TEXT).pack(anchor='w')
        self.tree = ttk.Treeview(left, show='headings', height=22)
        self.tree.pack(fill='both', expand=True, pady=(6, 0))

        tk.Label(right, text='AI Insights Summary', font=('Segoe UI', 11, 'bold'), bg=APP_BG, fg=TEXT).pack(anchor='w')
        self.report = tk.Text(right, bg=PANEL_BG, fg=TEXT, insertbackground=TEXT, relief='flat', wrap='word')
        self.report.pack(fill='both', expand=True, pady=(6, 0))

        style = ttk.Style()
        try:
            style.theme_use('default')
        except Exception:
            pass
        style.configure('Treeview', background=PANEL_BG, fieldbackground=PANEL_BG, foreground=TEXT, rowheight=26)
        style.configure('Treeview.Heading', background=BUTTON, foreground=TEXT)
        style.map('Treeview', background=[('selected', ACCENT)], foreground=[('selected', 'black')])

        self.status_line = tk.StringVar(value='Load a CSV to begin')
        tk.Label(self.root, textvariable=self.status_line, anchor='w', bg=APP_BG, fg=MUTED).pack(fill='x', padx=12, pady=(0, 10))

    def set_status(self, text: str):
        self.status_line.set(text)

    def to_number(self, raw):
        cleaned = ''.join(ch for ch in str(raw) if ch.isdigit() or ch in '.-')
        if not cleaned:
            return None
        try:
            return float(cleaned)
        except ValueError:
            return None

    def load_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV files', '*.csv')])
        if not path:
            return
        try:
            with open(path, newline='', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                self.rows = list(reader)
                self.headers = reader.fieldnames or []
            self.populate_mappings()
            self.populate_preview()
            self.report.delete('1.0', tk.END)
            self.set_status(f'Loaded {len(self.rows)} rows from {path}')
        except Exception as e:
            messagebox.showerror('CSV Error', f'Failed to load CSV: {e}')

    def populate_mappings(self):
        values = [''] + self.headers
        for i in range(4):
            combo = getattr(self, f'combo_{i}')
            combo['values'] = values
        if self.headers:
            numeric_guess = next((h for h in self.headers if any(k in h.lower() for k in ['value', 'revenue', 'amount', 'price', 'sale'])), self.headers[0])
            stage_guess = next((h for h in self.headers if any(k in h.lower() for k in ['stage', 'status', 'category'])), self.headers[0])
            owner_guess = next((h for h in self.headers if any(k in h.lower() for k in ['owner', 'rep', 'salesperson'])), '')
            self.value_var.set(numeric_guess)
            self.stage_var.set(stage_guess)
            self.owner_var.set(owner_guess)

    def populate_preview(self):
        self.tree.delete(*self.tree.get_children())
        self.tree['columns'] = self.headers
        for h in self.headers:
            self.tree.heading(h, text=h)
            self.tree.column(h, width=130, anchor='w')
        for row in self.rows[:100]:
            self.tree.insert('', tk.END, values=[row.get(h, '') for h in self.headers])

    def compute_summary(self):
        if not self.rows:
            return None
        value_col = self.value_var.get().strip()
        stage_col = self.stage_var.get().strip()
        owner_col = self.owner_var.get().strip()
        status_col = self.status_var.get().strip()

        values = [self.to_number(r.get(value_col, '')) for r in self.rows] if value_col else []
        numeric_values = [v for v in values if v is not None]
        stages = [r.get(stage_col, '').strip() for r in self.rows if stage_col and r.get(stage_col, '').strip()]
        owners = [r.get(owner_col, '').strip() for r in self.rows if owner_col and r.get(owner_col, '').strip()]
        statuses = [r.get(status_col, '').strip() for r in self.rows if status_col and r.get(status_col, '').strip()]

        stage_counts = Counter(stages)
        owner_value = defaultdict(float)
        if owner_col and value_col:
            for r in self.rows:
                owner = r.get(owner_col, '').strip()
                num = self.to_number(r.get(value_col, ''))
                if owner and num is not None:
                    owner_value[owner] += num

        summary = {
            'total_records': len(self.rows),
            'total_value': round(sum(numeric_values), 2) if numeric_values else 0,
            'average_value': round(mean(numeric_values), 2) if numeric_values else 0,
            'top_stage': stage_counts.most_common(1)[0][0] if stage_counts else '-',
            'stage_breakdown': dict(stage_counts),
            'owner_value_breakdown': dict(owner_value),
            'status_breakdown': dict(Counter(statuses)),
            'selected_columns': {
                'value': value_col,
                'stage': stage_col,
                'owner': owner_col,
                'status': status_col,
            },
        }
        summary['ai_insights'] = self.generate_ai_insights(summary)
        return summary

    def generate_ai_insights(self, summary):
        insights = []
        total = summary['total_records']
        total_value = summary['total_value']
        avg = summary['average_value']
        stages = summary['stage_breakdown']
        owner_values = summary['owner_value_breakdown']

        insights.append(f'The dataset contains {total} records with a total tracked value of ${total_value:,.2f} and an average value of ${avg:,.2f}.')
        if stages:
            top_stage, top_count = max(stages.items(), key=lambda x: x[1])
            insights.append(f'The largest concentration of records is in "{top_stage}" with {top_count} entries, which may indicate the biggest current workflow bottleneck or focus area.')
        if len(stages) >= 2:
            sorted_stages = sorted(stages.items(), key=lambda x: x[1], reverse=True)
            lowest = sorted_stages[-1]
            insights.append(f'The least populated stage/category is "{lowest[0]}" with {lowest[1]} records, which may suggest a conversion drop-off or underdeveloped segment.')
        if owner_values:
            top_owner, top_owner_value = max(owner_values.items(), key=lambda x: x[1])
            insights.append(f'{top_owner} is currently associated with the highest tracked value at ${top_owner_value:,.2f}, making them the strongest value contributor in this dataset.')
        if total_value and avg:
            high_value_threshold = avg * 1.5
            high_value_count = 0
            for row in self.rows:
                value = self.to_number(row.get(summary['selected_columns']['value'], ''))
                if value is not None and value >= high_value_threshold:
                    high_value_count += 1
            if high_value_count:
                insights.append(f'{high_value_count} records are at least 1.5x above the average value, suggesting a small set of high-impact opportunities worth prioritizing.')
        insights.append('This project uses rule-based AI-style insight generation by default and can be extended later with optional LLM summaries using local secret config.')
        return insights

    def render_summary(self, summary):
        self.total_records_var.set(str(summary['total_records']))
        self.total_value_var.set(f"${summary['total_value']:,.2f}")
        self.avg_value_var.set(f"${summary['average_value']:,.2f}")
        self.top_stage_var.set(summary['top_stage'])

        lines = []
        lines.append('=== Sales Ops AI Summary ===')
        lines.append(f"Total Records: {summary['total_records']}")
        lines.append(f"Total Value: ${summary['total_value']:,.2f}")
        lines.append(f"Average Value: ${summary['average_value']:,.2f}")
        lines.append(f"Top Stage / Category: {summary['top_stage']}")
        lines.append('')
        lines.append('Stage Breakdown:')
        for key, value in summary['stage_breakdown'].items():
            lines.append(f'- {key}: {value}')
        if summary['owner_value_breakdown']:
            lines.append('')
            lines.append('Owner Value Breakdown:')
            for key, value in summary['owner_value_breakdown'].items():
                lines.append(f'- {key}: ${value:,.2f}')
        if summary['status_breakdown']:
            lines.append('')
            lines.append('Status Breakdown:')
            for key, value in summary['status_breakdown'].items():
                lines.append(f'- {key}: {value}')
        lines.append('')
        lines.append('AI Insights:')
        for item in summary['ai_insights']:
            lines.append(f'- {item}')
        self.report.delete('1.0', tk.END)
        self.report.insert(tk.END, '\n'.join(lines))

    def run_analysis(self):
        if not self.rows:
            messagebox.showinfo('No Data', 'Load a CSV first.')
            return
        summary = self.compute_summary()
        self.last_summary = summary
        self.render_summary(summary)
        self.set_status('Analysis complete')

    def export_text(self):
        if not self.last_summary:
            messagebox.showinfo('No Summary', 'Run Analyze first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text files', '*.txt')], initialfile='sales_ops_ai_summary.txt')
        if not path:
            return
        Path(path).write_text(self.report.get('1.0', tk.END), encoding='utf-8')
        self.set_status(f'Exported text summary: {path}')

    def export_json(self):
        if not self.last_summary:
            messagebox.showinfo('No Summary', 'Run Analyze first.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.json', filetypes=[('JSON files', '*.json')], initialfile='sales_ops_ai_summary.json')
        if not path:
            return
        Path(path).write_text(json.dumps(self.last_summary, indent=2), encoding='utf-8')
        self.set_status(f'Exported JSON summary: {path}')

    def show_llm_example(self):
        self.report.delete('1.0', tk.END)
        self.report.insert(tk.END, json.dumps(LLM_CONFIG_EXAMPLE, indent=2))
        self.set_status('Showing GitHub-safe optional LLM config example')


def main():
    root = tk.Tk()
    app = SalesOpsAIDashboard(root)
    root.mainloop()


if __name__ == '__main__':
    main()
