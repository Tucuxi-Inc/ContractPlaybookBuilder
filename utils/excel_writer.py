"""
Excel playbook writer - creates professional Excel output from playbook data.

Generates comprehensive playbooks matching professional legal standards with
detailed clause-by-clause analysis.
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
    "section_bg": "E6E6E6",     # Section header background
}

# Styles
HEADER_FONT = Font(bold=True, color=COLORS["header_fg"], size=11)
HEADER_FILL = PatternFill(start_color=COLORS["header_bg"], end_color=COLORS["header_bg"], fill_type="solid")
TITLE_FONT = Font(bold=True, size=16)
SUBTITLE_FONT = Font(bold=True, size=12)
SECTION_FONT = Font(bold=True, size=11)
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


def format_list(items, prefix="•"):
    """Format a list of items with bullet points."""
    if not items:
        return ""
    if isinstance(items, str):
        return items
    formatted = []
    for item in items:
        if isinstance(item, str):
            # Clean up existing bullets
            clean_item = item.lstrip("•-* ").strip()
            if clean_item:
                formatted.append(f"{prefix} {clean_item}")
        elif isinstance(item, dict):
            # Handle dict items (like fallback positions)
            desc = item.get("description", "")
            if desc:
                formatted.append(f"{prefix} {desc}")
    return "\n".join(formatted)


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
        ("Agreement Type:", summary.get("agreement_type", "Not specified")),
        ("Parties:", summary.get("parties", "Not specified")),
        ("Purpose:", summary.get("purpose", "Not specified")),
        ("Key Dates/Terms:", summary.get("key_dates", "Not specified")),
        ("Governing Law:", summary.get("governing_law", "Not specified")),
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

    # Executive Summary
    row += 1
    ws[f"A{row}"] = "EXECUTIVE SUMMARY"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws.merge_cells(f"A{row}:D{row}")
    row += 1

    exec_summary = summary.get("executive_summary", "")
    ws[f"A{row}"] = exec_summary
    ws[f"A{row}"].alignment = WRAP_ALIGNMENT
    ws.merge_cells(f"A{row}:D{row}")
    ws.row_dimensions[row].height = 80

    # Risk level color coding legend
    row += 3
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
    ws.merge_cells(f"A{row}:D{row}")

    row += 1
    for item in quick_ref.get("deal_breakers", [])[:15]:
        ws[f"A{row}"] = f"✗ {item}"
        ws.merge_cells(f"A{row}:D{row}")
        row += 1

    row += 1
    ws[f"A{row}"] = "HIGH PRIORITY ITEMS"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws[f"A{row}"].fill = get_risk_fill("yellow")
    ws.merge_cells(f"A{row}:D{row}")

    row += 1
    for item in quick_ref.get("high_priority_items", [])[:15]:
        ws[f"A{row}"] = f"⚠ {item}"
        ws.merge_cells(f"A{row}:D{row}")
        row += 1

    set_column_widths(ws, {"A": 25, "B": 60, "C": 30, "D": 30})


def create_clause_analysis_sheet(wb: Workbook, playbook_data: dict) -> None:
    """Create the main Clause Analysis sheet matching professional playbook format."""
    ws = wb.create_sheet("Clause Analysis")

    # Headers matching the example playbook structure
    headers = [
        "Section",           # A - Section reference
        "Subpart",           # B - Subsection (a), (b), new, etc.
        "Issue",             # C - Clause title / issue name
        "Existing Language", # D - Original contract language or suggested new language
        "Customer Issues",   # E - Customer concerns (bullet points)
        "Customer Edits",    # F - Customer edit suggestions
        "Provider Issues",   # G - Provider concerns (bullet points)
        "Provider Edits",    # H - Provider edit suggestions
        "Preferred Position", # I - Preferred outcome description
        "Preferred Language", # J - Preferred contract language
        "Fallback Positions", # K - Fallback options
        "Don't Accept",      # L - Positions to avoid
        "Risk",              # M - Risk level (Red/Yellow/Green)
        "Approval",          # N - Who needs to approve
        "Negotiation Tips"   # O - Practical negotiation guidance
    ]

    for col, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col, value=header)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER_ALIGNMENT
        cell.border = THIN_BORDER

    # Freeze header row and first 3 columns
    ws.freeze_panes = "D2"

    # Add clause data
    clauses = playbook_data.get("clauses", [])

    for row_idx, clause in enumerate(clauses, 2):
        # A: Section reference
        ws.cell(row=row_idx, column=1, value=clause.get("section_reference", ""))

        # B: Subpart
        ws.cell(row=row_idx, column=2, value=clause.get("subpart", ""))

        # C: Issue/Clause title
        ws.cell(row=row_idx, column=3, value=clause.get("clause_title", ""))

        # D: Original/Existing language
        ws.cell(row=row_idx, column=4, value=clause.get("original_language", ""))

        # E: Customer issues (format as bullet points)
        customer_issues = clause.get("customer_issues", [])
        ws.cell(row=row_idx, column=5, value=format_list(customer_issues))

        # F: Customer edits to consider
        customer_edits = clause.get("customer_edits_to_consider", [])
        ws.cell(row=row_idx, column=6, value=format_list(customer_edits))

        # G: Provider issues
        provider_issues = clause.get("provider_issues", [])
        ws.cell(row=row_idx, column=7, value=format_list(provider_issues))

        # H: Provider edits to consider
        provider_edits = clause.get("provider_edits_to_consider", [])
        ws.cell(row=row_idx, column=8, value=format_list(provider_edits))

        # I: Preferred position description
        preferred = clause.get("preferred_position", {})
        if isinstance(preferred, dict):
            ws.cell(row=row_idx, column=9, value=preferred.get("description", ""))
            # J: Preferred language
            ws.cell(row=row_idx, column=10, value=preferred.get("sample_language", ""))
        else:
            ws.cell(row=row_idx, column=9, value=str(preferred))

        # K: Fallback positions
        fallbacks = clause.get("fallback_positions", [])
        fallback_text = ""
        for i, fb in enumerate(fallbacks, 1):
            if isinstance(fb, dict):
                fallback_text += f"{i}. {fb.get('description', '')}\n"
                if fb.get("sample_language"):
                    fallback_text += f"   Language: {fb.get('sample_language')}\n"
                if fb.get("conditions"):
                    fallback_text += f"   When: {fb.get('conditions')}\n"
                if fb.get("trade_offs"):
                    fallback_text += f"   Trade-off: {fb.get('trade_offs')}\n"
                fallback_text += "\n"
            else:
                fallback_text += f"{i}. {fb}\n"
        ws.cell(row=row_idx, column=11, value=fallback_text.strip())

        # L: Positions to avoid / Don't Accept
        avoid = clause.get("positions_to_avoid", [])
        avoid_text = ""
        for item in avoid:
            if isinstance(item, dict):
                avoid_text += f"✗ {item.get('description', '')}\n"
                if item.get("reason"):
                    avoid_text += f"  Reason: {item.get('reason')}\n"
                if item.get("red_flag_language"):
                    avoid_text += f"  Red flag: \"{item.get('red_flag_language')}\"\n"
            else:
                avoid_text += f"✗ {item}\n"
        ws.cell(row=row_idx, column=12, value=avoid_text.strip())

        # M: Risk level
        risk = clause.get("risk_level", "Green")
        risk_cell = ws.cell(row=row_idx, column=13, value=risk)
        risk_cell.fill = get_risk_fill(risk)
        risk_cell.alignment = CENTER_ALIGNMENT

        # N: Approval required
        ws.cell(row=row_idx, column=14, value=clause.get("approval_required", "None"))

        # O: Negotiation tips
        tips = clause.get("negotiation_tips", [])
        ws.cell(row=row_idx, column=15, value=format_list(tips))

        # Apply formatting to all cells in the row
        for col in range(1, 16):
            cell = ws.cell(row=row_idx, column=col)
            cell.alignment = WRAP_ALIGNMENT
            cell.border = THIN_BORDER

            # Alternating row colors (except risk level column)
            if row_idx % 2 == 0 and col != 13:
                cell.fill = PatternFill(start_color=COLORS["alt_row"], end_color=COLORS["alt_row"], fill_type="solid")

        # Set row height for readability
        ws.row_dimensions[row_idx].height = 80

    # Set column widths
    set_column_widths(ws, {
        "A": 10,   # Section
        "B": 10,   # Subpart
        "C": 25,   # Issue
        "D": 50,   # Existing Language
        "E": 40,   # Customer Issues
        "F": 45,   # Customer Edits
        "G": 40,   # Provider Issues
        "H": 45,   # Provider Edits
        "I": 35,   # Preferred Position
        "J": 50,   # Preferred Language
        "K": 45,   # Fallback Positions
        "L": 40,   # Don't Accept
        "M": 10,   # Risk
        "N": 12,   # Approval
        "O": 45,   # Negotiation Tips
    })


def create_definitions_sheet(wb: Workbook, playbook_data: dict) -> None:
    """Create the Definitions sheet with detailed term analysis."""
    ws = wb.create_sheet("Definitions")

    # Headers
    headers = [
        "Term",
        "Definition",
        "Why It Matters",
        "Customer Considerations",
        "Provider Considerations",
        "Suggested Modifications"
    ]

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
        ws.cell(row=row_idx, column=4, value=defn.get("customer_considerations", ""))
        ws.cell(row=row_idx, column=5, value=defn.get("provider_considerations", ""))
        ws.cell(row=row_idx, column=6, value=defn.get("suggested_modifications", ""))

        for col in range(1, 7):
            cell = ws.cell(row=row_idx, column=col)
            cell.alignment = WRAP_ALIGNMENT
            cell.border = THIN_BORDER
            if row_idx % 2 == 0:
                cell.fill = PatternFill(start_color=COLORS["alt_row"], end_color=COLORS["alt_row"], fill_type="solid")

        ws.row_dimensions[row_idx].height = 60

    set_column_widths(ws, {"A": 25, "B": 50, "C": 35, "D": 35, "E": 35, "F": 40})


def create_quick_reference_sheet(wb: Workbook, playbook_data: dict) -> None:
    """Create a Quick Reference sheet for at-a-glance info."""
    ws = wb.create_sheet("Quick Reference")

    quick_ref = playbook_data.get("quick_reference", {})
    strategy = playbook_data.get("negotiation_strategy", {})

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
        ws.merge_cells(f"A{row}:C{row}")
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
        ws.merge_cells(f"A{row}:C{row}")
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
        ws.merge_cells(f"A{row}:C{row}")
        row += 1

    row += 1

    # Recommended Negotiation Order
    ws[f"A{row}"] = "RECOMMENDED ORDER OF NEGOTIATION"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws.merge_cells(f"A{row}:C{row}")
    row += 1

    for i, item in enumerate(quick_ref.get("recommended_order_of_negotiation", []), 1):
        ws[f"A{row}"] = f"{i}. {item}"
        ws.merge_cells(f"A{row}:C{row}")
        row += 1

    row += 2

    # Negotiation Strategy
    ws[f"A{row}"] = "NEGOTIATION STRATEGY"
    ws[f"A{row}"].font = SUBTITLE_FONT
    ws.merge_cells(f"A{row}:C{row}")
    row += 2

    ws[f"A{row}"] = "Opening Position:"
    ws[f"A{row}"].font = Font(bold=True)
    ws[f"B{row}"] = strategy.get("opening_position", "")
    ws.merge_cells(f"B{row}:C{row}")
    row += 1

    ws[f"A{row}"] = "Key Leverage Points:"
    ws[f"A{row}"].font = Font(bold=True)
    row += 1
    for point in strategy.get("key_leverage_points", []):
        ws[f"B{row}"] = f"• {point}"
        ws.merge_cells(f"B{row}:C{row}")
        row += 1

    row += 1
    ws[f"A{row}"] = "Potential Trade-offs:"
    ws[f"A{row}"].font = Font(bold=True)
    row += 1
    for trade in strategy.get("potential_trade_offs", []):
        ws[f"B{row}"] = f"• {trade}"
        ws.merge_cells(f"B{row}:C{row}")
        row += 1

    row += 1
    ws[f"A{row}"] = "Walk-Away Triggers:"
    ws[f"A{row}"].font = Font(bold=True)
    ws[f"A{row}"].fill = get_risk_fill("red")
    row += 1
    for trigger in strategy.get("walk_away_triggers", []):
        ws[f"B{row}"] = f"✗ {trigger}"
        ws.merge_cells(f"B{row}:C{row}")
        row += 1

    set_column_widths(ws, {"A": 25, "B": 50, "C": 30})


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
