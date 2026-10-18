from .styles.pdf import (MARGIN, CARD_SPACING, CARD_WIDTH, CARD_HEIGHT_VAL, CARD_HEIGHT_LBL, TABLE_COL_WIDTHS,
                         SPACER_TITLE_SUBTITLE, SPACER_SUBTITLE_CARDS, SPACER_CARDS_TABLE, COLOR_BLUE, COLOR_GREEN, COLOR_RED,
                         COLOR_AMBER, REPORT_TITLE, TABLE_HEADERS, STYLE_TITLE, STYLE_SUBTITLE, STYLE_HEADER, STYLE_HEADER_CENTER,
                         STYLE_CELL, STYLE_CELL_CENTER, STYLE_URL, TABLE_STYLE_CARD, TABLE_STYLE_CARDS_ROW,
                         get_card_val_style, get_card_lbl_style, get_table_style)

from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer
from reportlab.lib.pagesizes import letter

from ..utils import ensure_file_extension, create_default_stats, is_web_url
from typing import List, Dict, Any, Optional
from rich.console import Console
from datetime import datetime



console = Console()


def _make_metric_card(value: Any, label: str, color_hex: str, width: float) -> Table:

    '''
    It constructs an individual metric card with a large colored numeric value,
    a subtle label underneath, rounded corners, and a light gray border.

    Parameters
    ----------
     value:Any
      The numeric or string metric count to display
     
     label:str
      The label for the card (e.g. 'Following', 'Followers')
     
     color_hex:str
      The hex color code for the numeric value font
     
     width:float
      The exact column width allocated for this card

    Outputs
    -------
     card:Table
      The styled ReportLab Table card flowable
    '''

    val_style = get_card_val_style(label, color_hex)
    lbl_style = get_card_lbl_style(label)

    card = Table(
                    data = [[Paragraph(str(value), val_style)], [Paragraph(label, lbl_style)]],
                    colWidths = [width],
                    rowHeights = [CARD_HEIGHT_VAL, CARD_HEIGHT_LBL]
                )
    card.setStyle(TABLE_STYLE_CARD)

    return card


def _build_cards_row(stats: Dict[str, Any], total_non_followers: int) -> Table:

    '''
    It constructs the horizontal 4-card KPI summary row (Following, Followers,
    Non-Followers, New Unfollowers).

    Parameters
    ----------
     stats:Dict[str, Any]
      Summary statistics dictionary containing account metrics
     
     total_non_followers:int
      Fallback count for non-followers if not present in stats

    Outputs
    -------
     cards_table:Table
      The styled ReportLab Table containing the 4 cards side by side
    '''

    following_val = stats.get('following', 'N/A')
    followers_val = stats.get('followers', 'N/A')
    non_followers_val = stats.get('non_followers', total_non_followers)
    new_unfollowers_val = stats.get('new_unfollowers', 0)

    cards = [
                _make_metric_card(following_val, 'Following', COLOR_BLUE, CARD_WIDTH),
                '',
                _make_metric_card(followers_val, 'Followers', COLOR_GREEN, CARD_WIDTH),
                '',
                _make_metric_card(non_followers_val, 'Non-Followers', COLOR_RED, CARD_WIDTH),
                '',
                _make_metric_card(new_unfollowers_val, 'New Unfollowers', COLOR_AMBER, CARD_WIDTH)
            ]

    col_widths = [CARD_WIDTH, CARD_SPACING, CARD_WIDTH, CARD_SPACING, CARD_WIDTH, CARD_SPACING, CARD_WIDTH]
    cards_table = Table([cards], colWidths = col_widths)
    cards_table.setStyle(TABLE_STYLE_CARDS_ROW)

    return cards_table


def _build_header(stats: Dict[str, Any], total_non_followers: int) -> List[Any]:

    '''
    It constructs the header flowable elements (title, generated timestamp, and 4 KPI cards).

    Parameters
    ----------
     stats:Dict[str, Any]
      Summary statistics dictionary containing account metrics
     
     total_non_followers:int
      The total number of detected non-followers

    Outputs
    -------
     elements:List[Any]
      The list of flowable header elements
    '''

    generated_date = stats.get('last_checked') or stats.get('generated') or datetime.now().strftime("%m/%d/%Y, %I:%M:%S %p")
    cards_row = _build_cards_row(stats, total_non_followers)

    return [
                Paragraph(REPORT_TITLE, STYLE_TITLE),
                Spacer(1, SPACER_TITLE_SUBTITLE),
                Paragraph(f"Generated: {generated_date}", STYLE_SUBTITLE),
                Spacer(1, SPACER_SUBTITLE_CARDS),
                cards_row,
                Spacer(1, SPACER_CARDS_TABLE)
            ]


def _build_table_headers() -> List[Paragraph]:

    '''
    It constructs the header row for the non-followers table with styled column titles.

    Parameters
    ----------
     None

    Outputs
    -------
     headers:List[Paragraph]
      The list of styled header cell paragraphs
    '''

    return [
                Paragraph(TABLE_HEADERS[0], STYLE_HEADER_CENTER),
                Paragraph(TABLE_HEADERS[1], STYLE_HEADER),
                Paragraph(TABLE_HEADERS[2], STYLE_HEADER),
                Paragraph(TABLE_HEADERS[3], STYLE_HEADER_CENTER)
            ]


def _format_url_cell(raw_url: str) -> Paragraph:

    '''
    It creates a styled ReportLab paragraph for the profile URL, converting web URLs
    into clickable hyperlinks.

    Parameters
    ----------
     raw_url:str
      The profile URL address

    Outputs
    -------
     paragraph:Paragraph
      The styled URL cell paragraph
    '''

    if is_web_url(raw_url):
        return Paragraph(f'<link href="{raw_url}">{raw_url}</link>', STYLE_URL)

    return Paragraph(raw_url, STYLE_CELL)


def _build_table_row(idx: int, item: Dict[str, Any]) -> List[Paragraph]:

    '''
    It formats and constructs a single row of cells for a non-follower entry.

    Parameters
    ----------
     idx:int
      The 1-based index number of the row
     
     item:Dict[str, Any]
      Dictionary containing user details (username, url, unfollow_date)

    Outputs
    -------
     row:List[Paragraph]
      The list of 4 styled flowable cell elements
    '''

    username = str(item.get('username', 'N/A'))
    raw_url = str(item.get('url', 'N/A'))
    unfollow_date = str(item.get('unfollow_date', 'N/A'))

    return [
                Paragraph(str(idx), STYLE_CELL_CENTER),
                Paragraph(username, STYLE_CELL),
                _format_url_cell(raw_url),
                Paragraph(unfollow_date, STYLE_CELL_CENTER)
            ]


def _build_table(data: List[Dict]) -> Table:

    '''
    It converts the non-followers data into a formatted ReportLab Table with 4 columns
    (#, Username, Profile URL, Unfollow Date), light borders, and rounded corners.

    Parameters
    ----------
     data:List[Dict]
      The list of dictionaries containing user details and unfollow dates

    Outputs
    -------
     table:Table
      The styled ReportLab Table flowable element
    '''

    table_rows: List[List[Any]] = [_build_table_headers()]

    for idx, item in enumerate(data, start = 1):
        table_rows.append(_build_table_row(idx, item))

    table = Table(table_rows, colWidths = TABLE_COL_WIDTHS, repeatRows = 1)
    table.setStyle(get_table_style(bool(data)))

    return table


def export_to_pdf(data: List[Dict], filename: str = "non_followers_report", stats: Optional[Dict[str, Any]] = None) -> None:

    '''
    It generates a PDF report containing the non-followers list in a structured table.

    Parameters
    ----------
     data:List[Dict]
      The list of dictionaries containing user details and unfollow dates

     filename:str
      The output PDF file path or name (default: 'non_followers_report')

     stats:Optional[Dict[str, Any]]
      Summary statistics dictionary containing following, followers, non_followers, new_unfollowers counts

    Outputs
    -------
     None
    '''

    filename = ensure_file_extension(filename, ".pdf")

    if stats is None:
        stats = create_default_stats(data)

    doc = SimpleDocTemplate(
                                filename,
                                pagesize = letter,
                                leftMargin = MARGIN,
                                rightMargin = MARGIN,
                                topMargin = 40,
                                bottomMargin = 40
                            )

    elements = [*_build_header(stats, len(data)), _build_table(data)]

    doc.build(elements)
    console.print(f"[bold green]✓[/] Report successfully saved to [cyan]{filename}[/cyan]")