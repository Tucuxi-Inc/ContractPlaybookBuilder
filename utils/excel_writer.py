"""
Excel playbook writer - creates professional Excel output from playbook data.
"""
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Border, Side, Alignment
from openpyxl.utils import get_column_letter
import os
from datetime import datetime


# Color definitions
COLORS = {
    "header_bg": "1F4E79",      # Dark blue
    "header_fg": "FFFFFF",      # White text
    "red_bg": "FFCCCC",         # Light red for high risk
    "yellow_bg": "FFFFCC",      # Light yellow for medium risk
    "green_bg": "CCFFCC",       # Light green for low risk
    "alt_row": "F2F2F2",        # Light gray for alternating rows
    "border": "CCCCCC",         # Gray border
}

# Styles
HEADER_FONT = Font(bold=True, color=COLORS["header_fg"], size=11)
HEADER_FILL = PatternFill(start_color=COLORS["header_bg"], end_color=COLORS["header_bg"], fill_type="solid")
TITLE_FONT = Font(bold=True, size=14)
SUBTITLE_FONT = Font(bold=True, size=12)
WRAP_ALIGNMENT = Alignment(wrap_text=True, vertical="top")
CENTER_ALIGNMENT = Alignment(horizontal="center", vertical="center")
THIN_BORDER = Border(
    left=Side(style="thin", color=COLORS["border"]),
    right=Side(style="thin", color=COLORS["border"]),
    top=Side(style="thin", color=COLORS["border"]),
    bottom=Side(style="thin", color=COLORS["border"])
)


def get_risk_fill(risk_level: str) -> PatternFill:
    """Get the appropriate fill color for a risk level."""
    risk = risk_level.lower() if risk_level else ""
    if risk == "red" or risk == "high":
        return PatternFill(start_color=COLORS["red_bg"], end_color=COLORS["red_bg"], fill_type="solid")
    elif risk == "yellow" or risk == "medium":
        return PatternFill(start_color=COLORS["yellow_bg"], end_color=COLORS["yellow_bg"], fill_type="solid")
    else:
        return PatternFill(start_color=COLORS["green_bg"], end_color=COLORS["green_bg"], fill_type="solid")


def set_column_widths(ws, widths: dict):
    """Set column widths for a worksheet."""
    for col, width in widths.items():
        ws.column_dimensions[col].width = width


def create_overview_sheet(wb: Workbook, playbook_data: dict) -> None:
    """Create the Overview sheet with agreement summary."""
    ws = wb.active
    ws.title = "Overview"

    summary = playbook_data.get("agreement_summary", {})

    # Title
    ws["A1"] = "CONTRACT PLAYBOOK"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:D1")

    ws["A2"] = f"Generated: {datetime.now().strftime('%B %d, %Y')}"
    ws["A2"].font = Font(italic=True)
    ws.merge_cells("A2:D2")

    # Agreement Summary section
    ws["A4"] = "AGREEMENT SUMMARY"
    ws["A4"].font = SUBTITLE_FONT
    ws.merge_cells("A4:D4")

    summary_data = [
        ("Agreement Title:", summary.get("title", "Not specified")),
        ("Parties:", summary.get("parties", "Not specified")),
        ("Purpose:", summary.get("purpose", "Not specified")),
        ("Key Dates/Terms:", summary.get("key_dates", "Not specified")),
        ("Overall Risk Level:", summary.get("overall_risk_level", "Medium")),
        ("Critical Issues:", str(summary.get("critical_issues_count", 0))),
    ]

    row = 6
    for label, value in summary_data:
        ws[f"A{row}"] = label
        ws[f"A{row}"].font = Font(bold=True)
        ws[f"B{row}"] = value
        ws[f"B{row}"].alignment = WRAP_ALIGNMENT
        row += 1

    # Risk level color coding legend
    row += 2
    ws[f"A{row}"] = "RISK LEVEL LEGEND"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws.merge_cells(f"A{row}:D{row}")

    row += 2
    ws[f"A{row}"] = "Red"
    ws[f"A{row}"].fill = get_risk_fill("red")
    ws[f"B{row}"] = "Deal breaker - requires legal review and executive approval"

    row += 1
    ws[f"A{row}"] = "Yellow"
    ws[f"A{row}"].fill = get_risk_fill("yellow")
    ws[f"B{row}"] = "Needs attention - requires manager or legal approval"

    row += 1
    ws[f"A{row}"] = "Green"
    ws[f"A{row}"].fill = get_risk_fill("green")
    ws[f"B{row}"] = "Acceptable - can proceed without escalation"

    # Quick Reference
    quick_ref = playbook_data.get("quick_reference", {})

    row += 3
    ws[f"A{row}"] = "DEAL BREAKERS (Do Not Accept)"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws[f"A{row}"].fill = get_risk_fill("red")

    row += 1
    for item in quick_ref.get("deal_breakers", [])[:10]:
        ws[f"A{row}"] = f"• {item}"
        row += 1

    row += 1
    ws[f"A{row}"] = "HIGH PRIORITY ITEMS"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws[f"A{row}"].fill = get_risk_fill("yellow")

    row += 1
    for item in quick_ref.get("high_priority_items", [])[:10]:
        ws[f"A{row}"] = f"• {item}"
        row += 1

    set_column_widths(ws, {"A": 25, "B": 60, "C": 30, "D": 30})


def create_clause_analysis_sheet(wb: Workbook, playbook_data: dict) -> None:
    """Create the main Clause Analysis sheet."""
    ws = wb.create_sheet("Clause Analysis")

    # Headers
    headers = [
        "Section",
        "Issue/Clause",
        "Original Language",
        "Business Context",
        "Customer Concerns",
        "Provider Concerns",
        "Preferred Position",
        "Preferred Language",
        "Fallback Positions",
        "Don't Accept",
        "Risk Level",
        "Approval Required",
        "Negotiation Tips"
    ]

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER_ALIGNMENT
        cell.border = THIN_BORDER

    # Freeze header row
    ws.freeze_panes = "A2"

    # Add clause data
    clauses = playbook_data.get("clauses", [])

    for row_idx, clause in enumerate(clauses, 2):
        # Section reference
        ws.cell(row=row_idx, column=1, value=clause.get("section_reference", ""))

        # Issue/Clause title
        ws.cell(row=row_idx, column=2, value=clause.get("clause_title", ""))

        # Original language
        ws.cell(row=row_idx, column=3, value=clause.get("original_language", ""))

        # Business context
        ws.cell(row=row_idx, column=4, value=clause.get("business_context", ""))

        # Customer perspective
        customer = clause.get("customer_perspective", {})
        customer_text = f"Concerns: {customer.get('concerns', '')}\n\nObjectives: {customer.get('objectives', '')}"
        ws.cell(row=row_idx, column=5, value=customer_text)

        # Provider perspective
        provider = clause.get("provider_perspective", {})
        provider_text = f"Concerns: {provider.get('concerns', '')}\n\nObjectives: {provider.get('objectives', '')}"
        ws.cell(row=row_idx, column=6, value=provider_text)

        # Preferred position
        preferred = clause.get("preferred_position", {})
        ws.cell(row=row_idx, column=7, value=preferred.get("description", ""))
        ws.cell(row=row_idx, column=8, value=preferred.get("sample_language", ""))

        # Fallback positions
        fallbacks = clause.get("fallback_positions", [])
        fallback_text = ""
        for i, fb in enumerate(fallbacks, 1):
            fallback_text += f"{i}. {fb.get('description', '')}\n"
            if fb.get("sample_language"):
                fallback_text += f"   Language: {fb.get('sample_language')}\n"
            if fb.get("conditions"):
                fallback_text += f"   When: {fb.get('conditions')}\n"
            fallback_text += "\n"
        ws.cell(row=row_idx, column=9, value=fallback_text.strip())

        # Positions to avoid
        avoid = clause.get("positions_to_avoid", [])
        avoid_text = ""
        for item in avoid:
            avoid_text += f"• {item.get('description', '')}\n"
            if item.get("reason"):
                avoid_text += f"  Reason: {item.get('reason')}\n"
        ws.cell(row=row_idx, column=10, value=avoid_text.strip())

        # Risk level
        risk = clause.get("risk_level", "Green")
        risk_cell = ws.cell(row=row_idx, column=11, value=risk)
        risk_cell.fill = get_risk_fill(risk)
        risk_cell.alignment = CENTER_ALIGNMENT

        # Approval required
        ws.cell(row=row_idx, column=12, value=clause.get("approval_required", "None"))

        # Negotiation tips
        ws.cell(row=row_idx, column=13, value=clause.get("negotiation_tips", ""))

        # Apply formatting to all cells in the row
        for col in range(1, 14):
            cell = ws.cell(row=row_idx, column=col)
            cell.alignment = WRAP_ALIGNMENT
            cell.border = THIN_BORDER

            # Alternating row colors (except risk level column)
            if row_idx % 2 == 0 and col != 11:
                cell.fill = PatternFill(start_color=COLORS["alt_row"], end_color=COLORS["alt_row"], fill_type="solid")

    # Set column widths
    set_column_widths(ws, {
        "A": 12,   # Section
        "B": 25,   # Issue
        "C": 40,   # Original Language
        "D": 35,   # Business Context
        "E": 35,   # Customer Concerns
        "F": 35,   # Provider Concerns
        "G": 35,   # Preferred Position
        "H": 40,   # Preferred Language
        "I": 45,   # Fallback Positions
        "J": 35,   # Don't Accept
        "K": 12,   # Risk Level
        "L": 15,   # Approval
        "M": 40,   # Negotiation Tips
    })


def create_definitions_sheet(wb: Workbook, playbook_data: dict) -> None:
    """Create the Definitions sheet."""
    ws = wb.create_sheet("Definitions")

    # Headers
    headers = ["Term", "Definition", "Importance/Notes"]
    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER_ALIGNMENT
        cell.border = THIN_BORDER

    ws.freeze_panes = "A2"

    definitions = playbook_data.get("definitions", [])

    for row_idx, defn in enumerate(definitions, 2):
        ws.cell(row=row_idx, column=1, value=defn.get("term", ""))
        ws.cell(row=row_idx, column=2, value=defn.get("definition", ""))
        ws.cell(row=row_idx, column=3, value=defn.get("importance", ""))

        for col in range(1, 4):
            cell = ws.cell(row=row_idx, column=col)
            cell.alignment = WRAP_ALIGNMENT
            cell.border = THIN_BORDER
            if row_idx % 2 == 0:
                cell.fill = PatternFill(start_color=COLORS["alt_row"], end_color=COLORS["alt_row"], fill_type="solid")

    set_column_widths(ws, {"A": 30, "B": 60, "C": 40})


def create_quick_reference_sheet(wb: Workbook, playbook_data: dict) -> None:
    """Create a Quick Reference sheet for at-a-glance info."""
    ws = wb.create_sheet("Quick Reference")

    quick_ref = playbook_data.get("quick_reference", {})

    # Title
    ws["A1"] = "QUICK REFERENCE GUIDE"
    ws["A1"].font = TITLE_FONT
    ws.merge_cells("A1:C1")

    row = 3

    # Deal Breakers
    ws[f"A{row}"] = "DEAL BREAKERS - Never Accept These Terms"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws[f"A{row}"].fill = get_risk_fill("red")
    ws.merge_cells(f"A{row}:C{row}")
    row += 1

    for item in quick_ref.get("deal_breakers", []):
        ws[f"A{row}"] = f"✗ {item}"
        row += 1

    row += 1

    # High Priority
    ws[f"A{row}"] = "HIGH PRIORITY - Requires Approval for Deviation"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws[f"A{row}"].fill = get_risk_fill("yellow")
    ws.merge_cells(f"A{row}:C{row}")
    row += 1

    for item in quick_ref.get("high_priority_items", []):
        ws[f"A{row}"] = f"⚠ {item}"
        row += 1

    row += 1

    # Standard Terms
    ws[f"A{row}"] = "STANDARD ACCEPTABLE TERMS"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws[f"A{row}"].fill = get_risk_fill("green")
    ws.merge_cells(f"A{row}:C{row}")
    row += 1

    for item in quick_ref.get("standard_acceptable_terms", []):
        ws[f"A{row}"] = f"✓ {item}"
        row += 1

    row += 1

    # Common Negotiation Points
    ws[f"A{row}"] = "COMMON NEGOTIATION POINTS"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws.merge_cells(f"A{row}:C{row}")
    row += 1

    for item in quick_ref.get("common_negotiation_points", []):
        ws[f"A{row}"] = f"• {item}"
        row += 1

    set_column_widths(ws, {"A": 60, "B": 30, "C": 30})


def generate_playbook_excel(playbook_data: dict, output_path: str) -> str:
    """
    Generate a complete Excel playbook from playbook data.

    Args:
        playbook_data: Dictionary containing the playbook analysis
        output_path: Path where the Excel file should be saved

    Returns:
        Path to the generated Excel file
    """
    wb = Workbook()

    # Create all sheets
    create_overview_sheet(wb, playbook_data)
    create_clause_analysis_sheet(wb, playbook_data)
    create_definitions_sheet(wb, playbook_data)
    create_quick_reference_sheet(wb, playbook_data)

    # Save the workbook
    wb.save(output_path)

    return output_path
