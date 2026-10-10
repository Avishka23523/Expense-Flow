import math
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date, datetime
from collections import defaultdict
from calendar import month_name
from reports import export_pdf, export_excel
from budgets import create_budget_table, save_budget, remove_budget, get_budget_summary, CATEGORIES
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import customtkinter as ctk
from database import create_table, add_transaction, get_transactions, update_transaction, delete_transaction

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')
create_table()
create_budget_table()

BG = '#0b1020'
PANEL = '#182239'
FIELD = '#101827'
TEXT = '#f8fafc'
MUTED = '#94a3b8'
PURPLE = '#635bdf'
GREEN = '#4ade80'
RED = '#fb7185'

class ExpenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title('ExpenseFlow | Personal Expense Tracker')
        self.geometry('1150x760')
        self.minsize(920, 680)
        self.configure(fg_color=BG)
        self.selected_id = None
        self.selected_date = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.build_sidebar()
        self.build_content()
        self.build_analytics()
        self.build_reports()
        self.build_budgets()
        self.show_page("dashboard")
        self.refresh()

    def build_sidebar(self):
        side = ctk.CTkFrame(self, width=205, corner_radius=0, fg_color='#111a2c')
        side.grid(row=0, column=0, sticky='nsw')
        side.grid_propagate(False)
        ctk.CTkLabel(side, text='◈  ExpenseFlow', font=('Segoe UI', 21, 'bold'), text_color=TEXT).pack(pady=(35, 8), padx=14)
        ctk.CTkLabel(side, text='PERSONAL FINANCE', font=('Segoe UI', 10), text_color=MUTED).pack(pady=(0, 35))
        self.dashboard_button = ctk.CTkButton(side, text='▦   Dashboard', fg_color=PURPLE, hover_color='#514ac5', height=42,
                      anchor='w', command=lambda: self.show_page('dashboard'))
        self.dashboard_button.pack(fill='x', padx=15, pady=6)
        self.analytics_button = ctk.CTkButton(side, text='◉   Analytics', fg_color='transparent', hover_color='#25304a', height=42,
                      anchor='w', command=lambda: self.show_page('analytics'))
        self.analytics_button.pack(fill='x', padx=15, pady=6)
        self.reports_button = ctk.CTkButton(side, text='▤   Reports', fg_color='transparent', hover_color='#25304a', height=42,
                      anchor='w', command=lambda: self.show_page('reports'))
        self.reports_button.pack(fill='x', padx=15, pady=6)
        self.budgets_button = ctk.CTkButton(side, text='◫   Budgets', fg_color='transparent', hover_color='#25304a', height=42,
                      anchor='w', command=lambda: self.show_page('budgets'))
        self.budgets_button.pack(fill='x', padx=15, pady=6)
        ctk.CTkButton(side, text='↻   Refresh', fg_color='transparent', hover_color='#25304a', height=42,
                      anchor='w', command=self.refresh).pack(fill='x', padx=15, pady=6)
        ctk.CTkLabel(side, text='Built with Python + SQLite', text_color=MUTED, font=('Segoe UI', 10)).pack(side='bottom', pady=25)

    def build_content(self):
        content = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        self.dashboard_page = content
        content.grid(row=0, column=1, sticky='nsew', padx=20, pady=12)
        content.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkLabel(content, text='Financial Dashboard', font=('Segoe UI', 27, 'bold'), text_color=TEXT).grid(row=0, column=0, columnspan=3, sticky='w', pady=(8, 2))
        ctk.CTkLabel(content, text='Manage your money with clarity.', text_color=MUTED).grid(row=1, column=0, columnspan=3, sticky='w', pady=(0, 18))

        self.income_value = self.make_card(content, 0, 'TOTAL INCOME', GREEN)
        self.expense_value = self.make_card(content, 1, 'TOTAL EXPENSES', RED)
        self.balance_value = self.make_card(content, 2, 'BALANCE', '#a5b4fc')

        form = ctk.CTkFrame(content, fg_color=PANEL, corner_radius=16)
        form.grid(row=3, column=0, columnspan=3, sticky='ew', pady=(18, 14))
        form.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(form, text='Add / Edit Transaction', font=('Segoe UI', 19, 'bold')).grid(row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(18, 10))

        self.kind = self.add_option(form, 'Transaction Type', ['Expense', 'Income'], 1, 0)
        self.category = self.add_option(form, 'Category', ['Food', 'Transport', 'Shopping', 'Bills', 'Salary', 'Other'], 1, 1)
        self.amount = self.add_entry(form, 'Amount (Rs.)', 'e.g. 1500', 3, 0)
        self.description = self.add_entry(form, 'Description', 'Optional note', 3, 1)

        actions = ctk.CTkFrame(form, fg_color='transparent')
        actions.grid(row=5, column=0, columnspan=2, sticky='ew', padx=15, pady=(14, 18))
        for i in range(4):
            actions.grid_columnconfigure(i, weight=1)
        for i, (label, color, callback) in enumerate([
            ('+ Add', PURPLE, self.save), ('Update', '#15803d', self.update),
            ('Delete', '#be123c', self.delete), ('Clear', '#475569', self.clear)
        ]):
            ctk.CTkButton(actions, text=label, fg_color=color, hover_color=color, command=callback, height=38).grid(row=0, column=i, padx=5, sticky='ew')

        self.build_filters(content)
        ctk.CTkLabel(content, text='Transaction History', font=('Segoe UI', 19, 'bold')).grid(row=8, column=0, columnspan=3, sticky='w', pady=(6, 10))
        table_holder = ctk.CTkFrame(content, fg_color=PANEL, corner_radius=12)
        table_holder.grid(row=9, column=0, columnspan=3, sticky='nsew', pady=(0, 10))
        table_holder.grid_columnconfigure(0, weight=1)
        table_holder.grid_rowconfigure(0, weight=1)
        style = ttk.Style(self)
        style.theme_use('clam')
        style.configure('Dark.Treeview', background=FIELD, foreground=TEXT, fieldbackground=FIELD,
                        rowheight=34, borderwidth=0, font=('Segoe UI', 10))
        style.configure('Dark.Treeview.Heading', background='#25304a', foreground=TEXT,
                        font=('Segoe UI', 10, 'bold'), relief='flat')
        style.map('Dark.Treeview', background=[('selected', PURPLE)], foreground=[('selected', 'white')])
        columns = ('ID', 'Type', 'Category', 'Amount', 'Date', 'Description')
        self.table = ttk.Treeview(table_holder, columns=columns, show='headings', selectmode='browse', style='Dark.Treeview', height=9)
        for col in columns:
            self.table.heading(col, text=col)
            self.table.column(col, width=85 if col == 'ID' else 135, anchor='center', stretch=True)
        self.table.grid(row=0, column=0, sticky='nsew', padx=(10, 0), pady=10)
        scroll = ttk.Scrollbar(table_holder, orient='vertical', command=self.table.yview)
        scroll.grid(row=0, column=1, sticky='ns', padx=(0, 10), pady=10)
        self.table.configure(yscrollcommand=scroll.set)
        self.table.bind('<<TreeviewSelect>>', self.on_select)
        self.status = ctk.CTkLabel(content, text='Select a row to edit or delete.', text_color=MUTED)
        self.status.grid(row=10, column=0, columnspan=3, sticky='w', pady=(0, 10))

    def build_filters(self, parent):
        filters = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=14)
        filters.grid(row=4, column=0, columnspan=3, sticky='ew', pady=(4, 14))
        for col in range(4):
            filters.grid_columnconfigure(col, weight=1)
        ctk.CTkLabel(filters, text='Search & Filter Transactions', font=('Segoe UI', 17, 'bold')).grid(
            row=0, column=0, columnspan=4, sticky='w', padx=18, pady=(15, 7))
        self.search_entry = self.add_entry(filters, 'Search category / description', 'Search...', 1, 0)
        self.filter_type = self.add_option(filters, 'Type', ['All', 'Income', 'Expense'], 1, 1)
        self.filter_category = self.add_option(filters, 'Category',
            ['All', 'Food', 'Transport', 'Shopping', 'Bills', 'Salary', 'Other'], 1, 2)
        self.from_entry = self.add_entry(filters, 'From (YYYY-MM-DD)', 'Optional', 3, 0)
        self.to_entry = self.add_entry(filters, 'To (YYYY-MM-DD)', 'Optional', 3, 1)
        self.filter_type.set('All')
        self.filter_category.set('All')
        ctk.CTkButton(filters, text='Apply Filters', fg_color=PURPLE, command=self.apply_filters,
                      height=38).grid(row=4, column=2, sticky='ew', padx=20, pady=(8, 18))
        ctk.CTkButton(filters, text='Reset Filters', fg_color='#475569', command=self.reset_filters,
                      height=38).grid(row=4, column=3, sticky='ew', padx=20, pady=(8, 18))
        self.search_entry.bind('<Return>', lambda event: self.apply_filters())
        # The summary cards and charts always use all transactions; filters affect history only.
        self.filter_note = ctk.CTkLabel(filters, text='Showing all transactions', text_color=MUTED)
        self.filter_note.grid(row=5, column=0, columnspan=4, sticky='w', padx=20, pady=(0, 12))

    def apply_filters(self):
        try:
            start_text = self.from_entry.get().strip()
            end_text = self.to_entry.get().strip()
            start = date.fromisoformat(start_text) if start_text else None
            end = date.fromisoformat(end_text) if end_text else None
            if start and end and start > end:
                raise ValueError('From date cannot be after To date.')
        except ValueError as exc:
            messagebox.showerror('Invalid Date', f'Use YYYY-MM-DD. {exc}')
            return
        query = self.search_entry.get().strip().casefold()
        kind = self.filter_type.get()
        category = self.filter_category.get()
        try:
            records = get_transactions()
            visible = []
            for rec in records:
                _, rec_kind, rec_category, _, rec_date, rec_description = rec
                if kind != 'All' and rec_kind != kind:
                    continue
                if category != 'All' and rec_category != category:
                    continue
                if query and query not in f'{rec_category} {rec_description or ""}'.casefold():
                    continue
                try:
                    rec_day = date.fromisoformat(str(rec_date))
                except ValueError:
                    if start or end:
                        continue
                    rec_day = None
                if start and rec_day < start:
                    continue
                if end and rec_day > end:
                    continue
                visible.append(rec)
            self.populate_history(visible)
            self.filter_note.configure(text=f'Showing {len(visible)} of {len(records)} transactions')
        except Exception as exc:
            messagebox.showerror('Database Error', str(exc))

    def reset_filters(self):
        self.search_entry.delete(0, 'end')
        self.filter_type.set('All')
        self.filter_category.set('All')
        self.from_entry.delete(0, 'end')
        self.to_entry.delete(0, 'end')
        self.apply_filters()

    def populate_history(self, records):
        # Prevent an old selection from accidentally editing a different row.
        self.selected_id = None
        self.selected_date = None
        self.status.configure(text='Select a row to edit or delete.')
        for row in self.table.get_children():
            self.table.delete(row)
        for rec in records:
            self.table.insert('', 'end', values=rec)

    def make_card(self, parent, col, title, color):
        card = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=15)
        card.grid(row=2, column=col, sticky='ew', padx=(0, 8) if col < 2 else 0)
        ctk.CTkLabel(card, text=title, text_color=MUTED, font=('Segoe UI', 11, 'bold')).pack(anchor='w', padx=17, pady=(17, 5))
        value = ctk.CTkLabel(card, text='Rs. 0.00', text_color=color, font=('Segoe UI', 22, 'bold'))
        value.pack(anchor='w', padx=17, pady=(0, 17))
        return value

    def add_option(self, parent, label, values, row, col):
        ctk.CTkLabel(parent, text=label, text_color=MUTED).grid(row=row, column=col, sticky='w', padx=20, pady=(4, 2))
        option = ctk.CTkOptionMenu(parent, values=values, fg_color=FIELD, button_color='#334155', button_hover_color=PURPLE, height=38)
        option.grid(row=row + 1, column=col, sticky='ew', padx=20, pady=(0, 10))
        option.set(values[0])
        return option

    def add_entry(self, parent, label, placeholder, row, col):
        ctk.CTkLabel(parent, text=label, text_color=MUTED).grid(row=row, column=col, sticky='w', padx=20, pady=(4, 2))
        entry = ctk.CTkEntry(parent, placeholder_text=placeholder, fg_color=FIELD, border_color='#334155', height=38)
        entry.grid(row=row + 1, column=col, sticky='ew', padx=20, pady=(0, 10))
        return entry

    def build_analytics(self):
        self.analytics_page = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        page = self.analytics_page
        # Place Analytics in the SAME content cell as Dashboard, beside the sidebar.
        page.grid(row=0, column=1, sticky='nsew', padx=20, pady=12)
        page.grid_remove()
        page.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(page, text='Financial Analytics', font=('Segoe UI', 27, 'bold'), text_color=TEXT).grid(
            row=0, column=0, columnspan=2, sticky='w', pady=(8, 2))
        ctk.CTkLabel(page, text='Understand your spending and cash flow.', text_color=MUTED).grid(
            row=1, column=0, columnspan=2, sticky='w', pady=(0, 18))

        self.category_fig, self.category_ax, self.category_canvas = self.make_chart(page, 2, 0, 'Expense Categories')
        self.monthly_fig, self.monthly_ax, self.monthly_canvas = self.make_chart(page, 2, 1, 'Monthly Income vs Expenses')
        self.trend_fig, self.trend_ax, self.trend_canvas = self.make_chart(page, 3, 0, 'Monthly Net Cash Flow', span=2)
        self.analytics_note = ctk.CTkLabel(page, text='', text_color=MUTED)
        self.analytics_note.grid(row=4, column=0, columnspan=2, sticky='w', pady=10)

    def build_reports(self):
        self.reports_page = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        page = self.reports_page
        page.grid(row=0, column=1, sticky='nsew', padx=20, pady=12)
        page.grid_remove()
        page.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(page, text='Monthly Reports', font=('Segoe UI', 27, 'bold'), text_color=TEXT).grid(
            row=0, column=0, sticky='w', pady=(10, 5))
        ctk.CTkLabel(page, text='Export your monthly transactions and summary to PDF or Excel.',
                     text_color=MUTED).grid(row=1, column=0, sticky='w', pady=(0, 18))
        card = ctk.CTkFrame(page, fg_color=PANEL, corner_radius=16)
        card.grid(row=2, column=0, sticky='ew', pady=(0, 12))
        card.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(card, text='Select Report Period', font=('Segoe UI', 19, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(20, 14))
        self.report_month = self.add_option(card, 'Month', list(month_name)[1:], 1, 0)
        self.report_year = self.add_option(card, 'Year', [str(y) for y in range(2020, 2101)], 1, 1)
        today = date.today()
        self.report_month.set(month_name[today.month])
        self.report_year.set(str(today.year))
        buttons = ctk.CTkFrame(card, fg_color='transparent')
        buttons.grid(row=3, column=0, columnspan=2, sticky='ew', padx=15, pady=(14, 20))
        buttons.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(buttons, text='Export PDF', fg_color=PURPLE, height=44,
                      command=lambda: self.save_report('pdf')).grid(row=0, column=0, padx=6, sticky='ew')
        ctk.CTkButton(buttons, text='Export Excel', fg_color='#15803d', height=44,
                      command=lambda: self.save_report('xlsx')).grid(row=0, column=1, padx=6, sticky='ew')
        ctk.CTkLabel(page, text='Reports include: Income • Expenses • Net Balance • Transaction History',
                     text_color=MUTED).grid(row=3, column=0, sticky='w', pady=12)

    def build_budgets(self):
        self.budgets_page = ctk.CTkScrollableFrame(self, fg_color=BG, corner_radius=0)
        page = self.budgets_page
        page.grid(row=0, column=1, sticky='nsew', padx=20, pady=12)
        page.grid_remove()
        page.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(page, text='Monthly Budgets', font=('Segoe UI', 27, 'bold'), text_color=TEXT).grid(
            row=0, column=0, sticky='w', pady=(10, 5))
        ctk.CTkLabel(page, text='Plan your spending by category and track your limits.', text_color=MUTED).grid(
            row=1, column=0, sticky='w', pady=(0, 18))

        card = ctk.CTkFrame(page, fg_color=PANEL, corner_radius=16)
        card.grid(row=2, column=0, sticky='ew', pady=(0, 14))
        card.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(card, text='Set or Update a Budget', font=('Segoe UI', 19, 'bold')).grid(
            row=0, column=0, columnspan=2, sticky='w', padx=20, pady=(18, 12))
        self.budget_month = self.add_option(card, 'Month', list(month_name)[1:], 1, 0)
        self.budget_year = self.add_option(card, 'Year', [str(y) for y in range(2020, 2101)], 1, 1)
        self.budget_category = self.add_option(card, 'Category', list(CATEGORIES), 3, 0)
        self.budget_amount = self.add_entry(card, 'Monthly Limit (Rs.)', 'e.g. 10000', 3, 1)
        today = date.today()
        self.budget_month.set(month_name[today.month])
        self.budget_year.set(str(today.year))
        buttons = ctk.CTkFrame(card, fg_color='transparent')
        buttons.grid(row=5, column=0, columnspan=2, sticky='ew', padx=15, pady=(12, 20))
        buttons.grid_columnconfigure((0, 1, 2), weight=1)
        ctk.CTkButton(buttons, text='Save / Update Budget', fg_color=PURPLE, height=40,
                      command=self.save_budget_action).grid(row=0, column=0, sticky='ew', padx=5)
        ctk.CTkButton(buttons, text='Delete Budget', fg_color='#be123c', height=40,
                      command=self.delete_budget_action).grid(row=0, column=1, sticky='ew', padx=5)
        ctk.CTkButton(buttons, text='View Month', fg_color='#475569', height=40,
                      command=self.refresh_budgets).grid(row=0, column=2, sticky='ew', padx=5)
        self.budget_month.configure(command=lambda _value: self.refresh_budgets())
        self.budget_year.configure(command=lambda _value: self.refresh_budgets())
        ctk.CTkLabel(page, text='Budget Overview', font=('Segoe UI', 19, 'bold')).grid(
            row=3, column=0, sticky='w', pady=(12, 10))
        self.budget_list = ctk.CTkFrame(page, fg_color='transparent')
        self.budget_list.grid(row=4, column=0, sticky='ew')
        self.budget_list.grid_columnconfigure(0, weight=1)
        self.budget_note = ctk.CTkLabel(page, text='', text_color=MUTED)
        self.budget_note.grid(row=5, column=0, sticky='w', pady=10)

    def budget_period(self):
        return int(self.budget_year.get()), list(month_name).index(self.budget_month.get())

    def save_budget_action(self):
        try:
            year, month = self.budget_period()
            save_budget(year, month, self.budget_category.get(), self.budget_amount.get().strip())
            self.budget_amount.delete(0, 'end')
            self.refresh_budgets()
            messagebox.showinfo('Budget Saved', 'Monthly budget saved successfully.')
        except (ValueError, TypeError) as exc:
            messagebox.showerror('Invalid Budget', str(exc))
        except Exception as exc:
            messagebox.showerror('Database Error', str(exc))

    def delete_budget_action(self):
        year, month = self.budget_period()
        category = self.budget_category.get()
        if not messagebox.askyesno('Delete Budget', f'Delete {category} budget for {month_name[month]} {year}?'):
            return
        try:
            removed = remove_budget(year, month, category)
            self.refresh_budgets()
            if not removed:
                messagebox.showinfo('Not Found', 'No budget was set for this category and month.')
        except Exception as exc:
            messagebox.showerror('Database Error', str(exc))

    def refresh_budgets(self):
        try:
            year, month = self.budget_period()
            summaries = get_budget_summary(year, month)
            for child in self.budget_list.winfo_children():
                child.destroy()
            if not summaries:
                ctk.CTkLabel(self.budget_list, text='No budgets set for this month. Add your first budget above.',
                             text_color=MUTED).grid(row=0, column=0, sticky='w', padx=12, pady=18)
            for index, (category, limit, spent) in enumerate(summaries):
                ratio = spent / limit
                status = 'OVER BUDGET' if ratio > 1 else 'WARNING' if ratio >= .8 else 'ON TRACK'
                color = RED if ratio > 1 else '#fbbf24' if ratio >= .8 else GREEN
                tile = ctk.CTkFrame(self.budget_list, fg_color=PANEL, corner_radius=14)
                tile.grid(row=index, column=0, sticky='ew', pady=6)
                tile.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(tile, text=f'{category}  •  {status}', text_color=color,
                             font=('Segoe UI', 16, 'bold')).grid(row=0, column=0, sticky='w', padx=18, pady=(14, 4))
                ctk.CTkLabel(tile, text=f'Rs. {spent:,.2f} spent  /  Rs. {limit:,.2f} limit   •   {ratio:.0%} used',
                             text_color=TEXT).grid(row=1, column=0, sticky='w', padx=18)
                bar = ctk.CTkProgressBar(tile, progress_color=color, fg_color='#334155', height=12)
                bar.grid(row=2, column=0, sticky='ew', padx=18, pady=(12, 15))
                bar.set(min(1.0, max(0.0, ratio)))
            self.budget_note.configure(text=f'{len(summaries)} budgets  •  {month_name[month]} {year}  •  Warning at 80%, alert above 100%')
        except Exception as exc:
            messagebox.showerror('Budget Error', str(exc))

    def save_report(self, extension):
        try:
            year = int(self.report_year.get())
            month = list(month_name).index(self.report_month.get())
            filename = f'ExpenseFlow_Report_{year:04d}_{month:02d}.{extension}'
            path = filedialog.asksaveasfilename(
                title=f'Save {extension.upper()} report', defaultextension=f'.{extension}',
                initialfile=filename,
                filetypes=[('PDF documents', '*.pdf')] if extension == 'pdf' else [('Excel workbooks', '*.xlsx')]
            )
            if not path:
                return
            if extension == 'pdf':
                export_pdf(path, year, month)
            else:
                export_excel(path, year, month)
            messagebox.showinfo('Report Exported', f'Report saved successfully:\n{path}')
        except Exception as exc:
            messagebox.showerror('Export Failed', str(exc))

    def make_chart(self, parent, row, col, heading, span=1):
        card = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=16)
        card.grid(row=row, column=col, columnspan=span, sticky='nsew', padx=6, pady=8)
        ctk.CTkLabel(card, text=heading, font=('Segoe UI', 17, 'bold'), text_color=TEXT).pack(
            anchor='w', padx=18, pady=(15, 5))
        fig = Figure(figsize=(5.2 if span == 1 else 10, 3.25), dpi=100, facecolor=PANEL)
        ax = fig.add_subplot(111)
        fig.subplots_adjust(left=.13, right=.95, top=.90, bottom=.22)
        canvas = FigureCanvasTkAgg(fig, master=card)
        canvas.get_tk_widget().configure(bg=PANEL, highlightthickness=0)
        canvas.get_tk_widget().pack(fill='both', expand=True, padx=10, pady=(0, 10))
        return fig, ax, canvas

    def style_axes(self, ax):
        ax.set_facecolor(PANEL)
        ax.tick_params(colors=MUTED, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color('#334155')
        ax.grid(axis='y', color='#334155', alpha=.55)
        ax.set_axisbelow(True)

    def refresh_analytics(self, records):
        categories = defaultdict(float)
        monthly = defaultdict(lambda: [0.0, 0.0])
        for _, kind, category, amount, transaction_date, _ in records:
            try:
                month = str(transaction_date)[:7]
                if len(month) != 7 or month[4] != '-':
                    continue
                if kind == 'Income':
                    monthly[month][0] += amount
                elif kind == 'Expense':
                    monthly[month][1] += amount
                    categories[category] += amount
            except (TypeError, ValueError):
                continue

        ax = self.category_ax
        ax.clear()
        ax.set_facecolor(PANEL)
        if categories:
            names = list(categories)
            values = list(categories.values())
            colors = ['#818cf8', '#fb7185', '#34d399', '#fbbf24', '#38bdf8', '#c084fc']
            ax.pie(values, labels=None, startangle=90, colors=[colors[i % len(colors)] for i in range(len(names))],
                   wedgeprops={'width': .43, 'edgecolor': PANEL}, autopct='%1.0f%%',
                   pctdistance=.79, textprops={'color': TEXT, 'fontsize': 9})
            ax.legend(names, loc='lower center', bbox_to_anchor=(.5, -.19), ncol=3,
                      frameon=False, labelcolor=TEXT, fontsize=8)
        else:
            ax.text(.5, .5, 'No expense data yet', ha='center', va='center', color=MUTED, transform=ax.transAxes)
            ax.set_xticks([]); ax.set_yticks([])
        self.category_canvas.draw_idle()

        months = sorted(monthly)
        ax = self.monthly_ax
        ax.clear()
        self.style_axes(ax)
        if months:
            indices = list(range(len(months)))
            ax.bar([i - .19 for i in indices], [monthly[m][0] for m in months], width=.38,
                   color='#34d399', label='Income')
            ax.bar([i + .19 for i in indices], [monthly[m][1] for m in months], width=.38,
                   color='#fb7185', label='Expenses')
            ax.set_xticks(indices, months, rotation=35, ha='right')
            ax.legend(facecolor=PANEL, edgecolor='#334155', labelcolor=TEXT, fontsize=8)
        else:
            ax.text(.5, .5, 'No transactions yet', ha='center', va='center', color=MUTED, transform=ax.transAxes)
        self.monthly_canvas.draw_idle()

        ax = self.trend_ax
        ax.clear()
        self.style_axes(ax)
        if months:
            net = [monthly[m][0] - monthly[m][1] for m in months]
            ax.plot(months, net, color='#a5b4fc', linewidth=2.5, marker='o', markersize=6)
            ax.axhline(0, color=MUTED, linestyle='--', linewidth=.8)
            ax.tick_params(axis='x', rotation=25)
            ax.set_ylabel('Net amount (Rs.)', color=MUTED)
        else:
            ax.text(.5, .5, 'Add transactions to see trends', ha='center', va='center',
                    color=MUTED, transform=ax.transAxes)
        self.trend_canvas.draw_idle()
        self.analytics_note.configure(text=f'{len(records)} transactions  •  {len(months)} months analysed')

    def show_page(self, page):
        pages = {'dashboard': self.dashboard_page,
                 'analytics': self.analytics_page,
                 'reports': self.reports_page,
                 'budgets': self.budgets_page}
        buttons = {'dashboard': self.dashboard_button,
                   'analytics': self.analytics_button,
                   'reports': self.reports_button,
                   'budgets': self.budgets_button}
        for name, frame in pages.items():
            if name == page:
                frame.grid(row=0, column=1, sticky='nsew', padx=20, pady=12)
            else:
                frame.grid_remove()
            buttons[name].configure(fg_color=PURPLE if name == page else 'transparent')

    def form_data(self):
        try:
            amount = float(self.amount.get().strip())
            if not math.isfinite(amount) or amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror('Invalid Amount', 'Enter a positive, valid amount.')
            return None
        return self.kind.get(), self.category.get(), amount, self.description.get().strip()

    def refresh(self):
        try:
            records = get_transactions()
            income = expense = 0.0
            for rec in records:
                if rec[1] == 'Income':
                    income += rec[3]
                elif rec[1] == 'Expense':
                    expense += rec[3]
            self.income_value.configure(text=f'Rs. {income:,.2f}')
            self.expense_value.configure(text=f'Rs. {expense:,.2f}')
            self.balance_value.configure(text=f'Rs. {income - expense:,.2f}')
            self.refresh_analytics(records)
            self.apply_filters()
            self.refresh_budgets()
        except Exception as exc:
            messagebox.showerror('Database Error', str(exc))

    def clear(self):
        self.selected_id = None
        self.selected_date = None
        self.kind.set('Expense')
        self.category.set('Food')
        self.amount.delete(0, 'end')
        self.description.delete(0, 'end')
        for row in self.table.selection():
            self.table.selection_remove(row)
        self.status.configure(text='Select a row to edit or delete.')

    def on_select(self, event=None):
        selected = self.table.selection()
        if not selected:
            return
        rec = self.table.item(selected[0], 'values')
        self.selected_id = int(rec[0])
        self.selected_date = rec[4]
        self.kind.set(rec[1])
        self.category.set(rec[2])
        self.amount.delete(0, 'end')
        self.amount.insert(0, rec[3])
        self.description.delete(0, 'end')
        self.description.insert(0, rec[5])
        self.status.configure(text=f'Editing transaction #{self.selected_id}')

    def save(self):
        if self.selected_id is not None:
            messagebox.showwarning('Selection Active', 'Click Clear before adding a new transaction.')
            return
        data = self.form_data()
        if data is None:
            return
        try:
            add_transaction(*data[:3], date.today().isoformat(), data[3])
            self.clear()
            self.refresh()
            messagebox.showinfo('Saved', 'Transaction added successfully.')
        except Exception as exc:
            messagebox.showerror('Database Error', str(exc))

    def update(self):
        if self.selected_id is None:
            messagebox.showwarning('No Selection', 'Select a transaction first.')
            return
        data = self.form_data()
        if data is None:
            return
        try:
            changed = update_transaction(self.selected_id, *data[:3], self.selected_date, data[3])
            self.clear()
            self.refresh()
            if changed:
                messagebox.showinfo('Updated', 'Transaction updated successfully.')
            else:
                messagebox.showwarning('Not Found', 'Transaction no longer exists.')
        except Exception as exc:
            messagebox.showerror('Database Error', str(exc))

    def delete(self):
        if self.selected_id is None:
            messagebox.showwarning('No Selection', 'Select a transaction first.')
            return
        if not messagebox.askyesno('Confirm Delete', 'Delete the selected transaction?'):
            return
        try:
            deleted = delete_transaction(self.selected_id)
            self.clear()
            self.refresh()
            if deleted:
                messagebox.showinfo('Deleted', 'Transaction deleted successfully.')
            else:
                messagebox.showwarning('Not Found', 'Transaction no longer exists.')
        except Exception as exc:
            messagebox.showerror('Database Error', str(exc))

if __name__ == '__main__':
    ExpenseApp().mainloop()
