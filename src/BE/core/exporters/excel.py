from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter
from openpyxl import Workbook

from ..utils import ensure_file_extension, create_default_stats, is_web_url
from typing import List, Dict, Any, Optional
from rich.console import Console
from datetime import datetime
from .styles.excel import *


console = Console()


def _render_title_banner(ws: Worksheet, generated_date: str) -> None:

    '''
    It renders the main report title, generation timestamp subtitle and spacing in the worksheet.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     generated_date:str
      The formatted timestamp string when the report was generated

    Outputs
    -------
     None
    '''

    # Row 1: Title
    ws.row_dimensions[ROW_INDEX_TITLE].height = ROW_HEIGHT_TITLE
    cell_title = ws.cell(row = ROW_INDEX_TITLE, column = 1, value = REPORT_TITLE)
    cell_title.font = FONT_TITLE
    cell_title.alignment = ALIGN_BANNER

    # Row 2: Subtitle
    ws.row_dimensions[ROW_INDEX_SUBTITLE].height = ROW_HEIGHT_SUBTITLE
    cell_sub = ws.cell(row = ROW_INDEX_SUBTITLE, column = 1, value = f"Generated: {generated_date}")
    cell_sub.font = FONT_SUBTITLE
    cell_sub.alignment = ALIGN_BANNER

    # Row 3: Spacer
    ws.row_dimensions[ROW_INDEX_SPACER_1].height = ROW_HEIGHT_SPACER_1


def _render_kpi_card(ws: Worksheet, col_idx: int, val: str, label: str, col_color: str) -> None:

    '''
    It renders an individual 2-row KPI card with numeric value and descriptive label.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     col_idx:int
      The 1-based column index where the card should be rendered

     val:str
      The numeric or string metric value to display

     label:str
      The descriptive label for the card (e.g. 'Following', 'Followers')

     col_color:str
      The hex color code for the numeric value font

    Outputs
    -------
     None
    '''

    c_val = ws.cell(row = ROW_INDEX_CARD_VAL, column = col_idx, value = val)
    c_val.font = Font(name = FONT_FAMILY, size = 18, bold = True, color = col_color)
    c_val.alignment = ALIGN_CENTER
    c_val.border = BORDER_CARD_TOP
    c_val.fill = FILL_WHITE

    c_lbl = ws.cell(row = ROW_INDEX_CARD_LBL, column = col_idx, value = label)
    c_lbl.font = FONT_CARD_LABEL
    c_lbl.alignment = ALIGN_CENTER
    c_lbl.border = BORDER_CARD_BOTTOM
    c_lbl.fill = FILL_WHITE


def _render_kpi_cards(ws: Worksheet, stats: Dict[str, Any], total_non_followers: int) -> None:

    '''
    It constructs the 4 KPI metric cards row (Following, Followers, Non-Followers, New Unfollowers).

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     stats:Dict[str, Any]
      Summary statistics dictionary containing account metrics

     total_non_followers:int
      Fallback count for non-followers if not present in stats

    Outputs
    -------
     None
    '''

    card_configs = [
                        (1, str(stats.get('following', 'N/A')), 'Following', COLOR_CARD_FOLLOWING),
                        (2, str(stats.get('followers', 'N/A')), 'Followers', COLOR_CARD_FOLLOWERS),
                        (3, str(stats.get('non_followers', total_non_followers)), 'Non-Followers', COLOR_CARD_NON_FOLLOWERS),
                        (4, str(stats.get('new_unfollowers', 0)), 'New Unfollowers', COLOR_CARD_NEW_UNFOLLOWERS),
                    ]

    ws.row_dimensions[ROW_INDEX_CARD_VAL].height = ROW_HEIGHT_CARD_VAL
    ws.row_dimensions[ROW_INDEX_CARD_LBL].height = ROW_HEIGHT_CARD_LBL

    for col_idx, val, label, col_color in card_configs:
        _render_kpi_card(ws, col_idx, val, label, col_color)


def _build_header_section(ws: Worksheet, stats: Dict[str, Any], total_non_followers: int) -> int:

    '''
    It renders the title, generated timestamp, and 4 KPI cards in the worksheet.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet
     
     stats:Dict[str, Any]
      Summary statistics dictionary containing account metrics
     
     total_non_followers:int
      The total number of detected non-followers

    Outputs
    -------
     next_row:int
      The starting row index for table headers
    '''

    generated_date = stats.get('last_checked') or stats.get('generated') or datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")

    _render_title_banner(ws, generated_date)
    _render_kpi_cards(ws, stats, total_non_followers)

    # Row 6: Spacer
    ws.row_dimensions[ROW_INDEX_SPACER_2].height = ROW_HEIGHT_SPACER_2

    return ROW_INDEX_HEADER


def _build_table_headers(ws: Worksheet, row: int) -> None:

    '''
    It creates and styles the column headers row for the non-followers table.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     row:int
      The row number where headers should be placed

    Outputs
    -------
     None
    '''

    ws.row_dimensions[row].height = ROW_HEIGHT_HEADER

    for col_idx, header_text in enumerate(TABLE_HEADERS, start = 1):

        cell = ws.cell(row = row, column = col_idx, value = header_text)
        cell.font = FONT_HEADER
        cell.fill = FILL_HEADER
        cell.alignment = ALIGN_CENTER if col_idx in (1, 4) else ALIGN_LEFT
        cell.border = BORDER_HEADER


def _render_index_cell(ws: Worksheet, row: int, idx: int, fill: PatternFill) -> None:

    '''
    It creates and formats the index sequence cell with centered alignment and subtle text color.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     row:int
      The row index where the cell should be placed

     idx:int
      The 1-based index number of the row

     fill:PatternFill
      The background fill pattern for alternating rows

    Outputs
    -------
     None
    '''

    cell = ws.cell(row = row, column = 1, value = idx)
    cell.font = FONT_INDEX
    cell.alignment = ALIGN_CENTER
    cell.fill = fill
    cell.border = BORDER_DATA_CELL


def _render_username_cell(ws: Worksheet, row: int, username: str, fill: PatternFill) -> None:

    '''
    It creates and formats the username cell with left alignment and primary text color.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     row:int
      The row index where the cell should be placed

     username:str
      The target account username

     fill:PatternFill
      The background fill pattern for alternating rows

    Outputs
    -------
     None
    '''

    cell = ws.cell(row = row, column = 2, value = username)
    cell.font = FONT_USERNAME
    cell.alignment = ALIGN_LEFT
    cell.fill = fill
    cell.border = BORDER_DATA_CELL


def _render_url_cell(ws: Worksheet, row: int, url: str, fill: PatternFill) -> None:

    '''
    It creates and formats the profile URL cell, configuring hyperlinks for web URLs.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     row:int
      The row index where the cell should be placed

     url:str
      The profile URL address

     fill:PatternFill
      The background fill pattern for alternating rows

    Outputs
    -------
     None
    '''

    cell = ws.cell(row = row, column = 3, value = url)
    cell.alignment = ALIGN_LEFT
    cell.fill = fill
    cell.border = BORDER_DATA_CELL

    if is_web_url(url):
        cell.hyperlink = url
        cell.font = FONT_URL
        
    else:
        cell.font = FONT_URL_DEFAULT


def _render_date_cell(ws: Worksheet, row: int, date_str: str, fill: PatternFill) -> None:

    '''
    It creates and formats the unfollow date cell with centered alignment and secondary text color.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     row:int
      The row index where the cell should be placed

     date_str:str
      The recorded unfollow date or history status string

     fill:PatternFill
      The background fill pattern for alternating rows

    Outputs
    -------
     None
    '''

    cell = ws.cell(row = row, column = 4, value = date_str)
    cell.font = FONT_DATE
    cell.alignment = ALIGN_CENTER
    cell.fill = fill
    cell.border = BORDER_DATA_CELL


def _render_row(ws: Worksheet, row: int, idx: int, item: Dict, fill: PatternFill) -> None:

    '''
    It formats and populates a single data row with index number, username, profile URL and unfollow date.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     row:int
      The row number to populate

     idx:int
      The 1-based index number of the row

     item:Dict
      The dictionary containing non-follower user details

     fill:PatternFill
      The background fill pattern for alternating rows

    Outputs
    -------
     None
    '''

    ws.row_dimensions[row].height = ROW_HEIGHT_DATA

    _render_index_cell(ws, row, idx, fill)
    _render_username_cell(ws, row, item.get('username', 'N/A'), fill)
    _render_url_cell(ws, row, item.get('url', 'N/A'), fill)
    _render_date_cell(ws, row, item.get('unfollow_date', 'N/A'), fill)


def _populate_data_rows(ws: Worksheet, data: List[Dict], start_row: int) -> None:

    '''
    It populates the worksheet with formatted user data rows, alternating backgrounds and hyperlinks.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

     data:List[Dict]
      The list of non-followers data dictionaries

     start_row:int
      The starting row number for data rows

    Outputs
    -------
     None
    '''

    for idx, item in enumerate(data, start = 1):

        current_row = start_row + idx - 1
        row_fill = FILL_LIGHT if (idx % 2 == 0) else FILL_WHITE
        _render_row(ws, current_row, idx, item, row_fill)


def _apply_column_widths(ws: Worksheet) -> None:

    '''
    It sets predefined column widths for the table columns.

    Parameters
    ----------
     ws:Worksheet
      The active openpyxl worksheet

    Outputs
    -------
     None
    '''

    for col_idx, width in COL_WIDTHS.items():

        col_letter = get_column_letter(col_idx)
        col_dim = ws.column_dimensions[col_letter]

        if col_dim is not None:
            col_dim.width = float(width)


def _setup_workbook(title: str = DEFAULT_SHEET_TITLE) -> tuple[Workbook, Worksheet]:

    '''
    It initializes the workbook and configures the active worksheet with title and view settings.

    Parameters
    ----------
     title:str
      The title to assign to the main worksheet (default: 'Non-Followers')

    Outputs
    -------
     tuple[Workbook, Worksheet]
      The initialized Workbook instance and its configured active Worksheet
    '''

    wb = Workbook()
    ws = wb.active

    if ws is None:
        ws = wb.create_sheet(title = title)
    else:
        ws.title = title

    # Ensure grid lines are not visible
    ws.views.sheetView[0].showGridLines = False

    return wb, ws


def export_to_excel(data: List[Dict], filename: str = DEFAULT_REPORT_FILENAME, stats: Optional[Dict[str, Any]] = None) -> None:

    '''
    It generates an Excel spreadsheet report styled to match the GUI dashboard with KPI metric cards
    and a structured 4-column table.

    Parameters
    ----------
     data:List[Dict]
      The list of dictionaries containing user details and unfollow dates

     filename:str
      The output Excel file path or name (default: 'non_followers_report')

     stats:Optional[Dict[str, Any]]
      Summary statistics dictionary containing following, followers, non_followers, new_unfollowers counts

    Outputs
    -------
     None
    '''

    filename = ensure_file_extension(filename, ".xlsx")

    if stats is None:
        stats = create_default_stats(data)

    wb, ws = _setup_workbook(DEFAULT_SHEET_TITLE)

    header_row = _build_header_section(ws, stats, len(data))
    _build_table_headers(ws, header_row)
    _populate_data_rows(ws, data, header_row + 1)
    _apply_column_widths(ws)

    # Freeze panes below table header
    ws.freeze_panes = f"A{header_row + 1}"

    wb.save(filename)
    console.print(f"[bold green]✓[/] Report successfully saved to [cyan]{filename}[/cyan]")