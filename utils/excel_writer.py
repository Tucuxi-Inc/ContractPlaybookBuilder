"""
Excel playbook writer with topic-based sheet organization.

Creates professional contract playbooks matching the structure of
high-quality legal playbooks with separate sheets per topic.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter


# Styling
HEADER_FONT = Font(bold=True, size=11, color="FFFFFF")
HEADER_FILL = PatternFill(start_color="2B579A", end_color="2B579A", fill_type="solid")
TITLE_FONT = Font(bold=True, size=18, color="2B579A")
SECTION_FONT = Font(bold=True, size=12)
THIN_BORDER = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)
WRAP_ALIGNMENT = Alignment(wrap_text=True, vertical='top')
ALT_ROW_FILL = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")

# Column structure for clause analysis sheets
CLAUSE_COLUMNS = [
    ("Section", 10),
    ("Subsection", 12),
    ("Issue", 25),
    ("Current Language", 50),
    ("Purpose/Rationale", 40),
    ("Customer Concerns", 40),
    ("Customer Edits to Watch", 35),
    ("Provider Position", 40),
    ("Acceptable Modifications", 40),
    ("Fallback Language", 50),
    ("Do Not Accept", 35),
    ("Notes", 30)
]


def generate_playbook_excel(playbook_data: dict, output_path: str):
    """
    Generate a professional Excel playbook with topic-based sheets.

    Args:
        playbook_data: The structured playbook data from Claude analysis
        output_path: Path to save the Excel file
    """
    wb = Workbook()

    # Remove default sheet
    if "Sheet" in wb.sheetnames:
        del wb["Sheet"]

    # Create Overview sheet
    create_overview_sheet(wb, playbook_data.get("overview", {}))

    # Create topic sheets
    topics = playbook_data.get("topics", {})
    for topic_name, clauses in topics.items():
        if clauses:  # Only create sheet if there are clauses
            create_topic_sheet(wb, topic_name, clauses)

    # Create Quick Reference sheet
    create_quick_reference_sheet(wb, playbook_data.get("quick_reference", []))

    wb.save(output_path)
    return output_path


def create_overview_sheet(wb: Workbook, overview: dict):
    """Create the Overview sheet with agreement summary and guidance."""
    ws = wb.create_sheet("Overview", 0)

    # Title
    title = overview.get("title", "Contract Playbook")
    ws["A1"] = f"{title} Contracting Playbook"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:B1")

    row = 3

    # Agreement details
    details = [
        ("Agreement Type:", overview.get("agreement_type", "")),
        ("Perspective:", overview.get("perspective", "")),
        ("Parties:", overview.get("parties", "")),
        ("Effective Date:", overview.get("effective_date", "")),
        ("Governing Law:", overview.get("governing_law", "")),
    ]

    for label, value in details:
        if value:
            ws.cell(row=row, column=1, value=label).font = Font(bold=True)
            ws.cell(row=row, column=2, value=value)
            row += 1

    row += 1

    # Key Principles
    ws.cell(row=row, column=1, value="KEY PRINCIPLES").font = SECTION_FONT
    row += 1

    for i, principle in enumerate(overview.get("key_principles", []), 1):
        ws.cell(row=row, column=1, value=f"{i}. {principle}")
        ws.cell(row=row, column=1).alignment = WRAP_ALIGNMENT
        row += 1

    row += 1

    # Executive Summary
    ws.cell(row=row, column=1, value="EXECUTIVE SUMMARY").font = SECTION_FONT
    row += 1
    summary = overview.get("executive_summary", "")
    ws.cell(row=row, column=1, value=summary)
    ws.cell(row=row, column=1).alignment = WRAP_ALIGNMENT
    ws.merge_cells(f"A{row}:B{row}")
    ws.row_dimensions[row].height = 100
    row += 2

    # How to Use
    ws.cell(row=row, column=1, value="HOW TO USE THIS PLAYBOOK").font = SECTION_FONT
    row += 1

    for i, instruction in enumerate(overview.get("how_to_use", []), 1):
        ws.cell(row=row, column=1, value=f"{i}. {instruction}")
        ws.cell(row=row, column=1).alignment = WRAP_ALIGNMENT
        row += 1

    # Set column widths
    ws.column_dimensions["A"].width = 25
    ws.column_dimensions["B"].width = 80


def create_topic_sheet(wb: Workbook, topic_name: str, clauses: list):
    """Create a sheet for a specific contract topic."""
    # Sanitize sheet name - remove invalid characters and truncate
    # Excel doesn't allow: / \ ? * [ ] :
    sheet_name = topic_name.replace("/", "-").replace("\\", "-").replace("?", "").replace("*", "").replace("[", "").replace("]", "").replace(":", "-")
    sheet_name = sheet_name[:31] if len(sheet_name) > 31 else sheet_name
    ws = wb.create_sheet(sheet_name)

    # Headers
    for col_idx, (header, width) in enumerate(CLAUSE_COLUMNS, 1):
        cell = ws.cell(row=1, column=col_idx, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = Alignment(horizontal='center', vertical='center')
        cell.border = THIN_BORDER
        ws.column_dimensions[get_column_letter(col_idx)].width = width

    # Freeze header row
    ws.freeze_panes = "A2"

    # Add clause data
    for row_idx, clause in enumerate(clauses, 2):
        ws.cell(row=row_idx, column=1, value=clause.get("section", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=clause.get("subsection", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=3, value=clause.get("issue", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=4, value=clause.get("current_language", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=5, value=clause.get("purpose_rationale", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=6, value=clause.get("customer_concerns", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=7, value=clause.get("customer_edits_to_watch", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=8, value=clause.get("provider_position", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=9, value=clause.get("acceptable_modifications", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=10, value=clause.get("fallback_language", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=11, value=clause.get("do_not_accept", "")).border = THIN_BORDER
        ws.cell(row=row_idx, column=12, value=clause.get("notes", "")).border = THIN_BORDER

        # Apply wrap text and alternating row colors
        for col in range(1, 13):
            cell = ws.cell(row=row_idx, column=col)
            cell.alignment = WRAP_ALIGNMENT
            if row_idx % 2 == 0:
                cell.fill = ALT_ROW_FILL

    # Set row heights for better readability
    for row in range(2, len(clauses) + 2):
        ws.row_dimensions[row].height = 80


def create_quick_reference_sheet(wb: Workbook, quick_reference: list):
    """Create the Quick Reference sheet with hard limits."""
    ws = wb.create_sheet("Quick Reference")

    # Title
    ws["A1"] = "Quick Reference - Hard Limits"
    ws["A1"].font = Font(bold=True, size=14, color="2B579A")
    ws.merge_cells("A1:B1")

    ws["A2"] = "Items below require executive approval before deviating from standard position"
    ws["A2"].font = Font(italic=True, color="666666")
    ws.merge_cells("A2:B2")

    # Headers
    ws["A4"] = "Topic"
    ws["B4"] = "Hard Limit (Do Not Accept Without Executive Approval)"
    ws["A4"].font = HEADER_FONT
    ws["B4"].font = HEADER_FONT
    ws["A4"].fill = HEADER_FILL
    ws["B4"].fill = HEADER_FILL
    ws["A4"].border = THIN_BORDER
    ws["B4"].border = THIN_BORDER

    # Data
    for row_idx, item in enumerate(quick_reference, 5):
        issue_cell = ws.cell(row=row_idx, column=1, value=item.get("issue", ""))
        limit_cell = ws.cell(row=row_idx, column=2, value=item.get("limit", ""))
        issue_cell.alignment = WRAP_ALIGNMENT
        limit_cell.alignment = WRAP_ALIGNMENT
        issue_cell.border = THIN_BORDER
        limit_cell.border = THIN_BORDER
        if row_idx % 2 == 0:
            issue_cell.fill = ALT_ROW_FILL
            limit_cell.fill = ALT_ROW_FILL

    # Column widths
    ws.column_dimensions["A"].width = 30
    ws.column_dimensions["B"].width = 70

    # Freeze header
    ws.freeze_panes = "A5"
