from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from reportlab.lib.styles import getSampleStyleSheet, StyleSheet1, ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

from typing import List, Dict, Any

from rich.console import Console


console = Console()


PAGE_WIDTH, _ = letter
MARGIN = 72
PRINTABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)

COL_WIDTH_USERNAME = PRINTABLE_WIDTH * 0.28
COL_WIDTH_URL = PRINTABLE_WIDTH * 0.47
COL_WIDTH_DATE = PRINTABLE_WIDTH * 0.25

SPACER_WIDTH = 1
SPACER_HEIGHT = 20


def _build_header(total_count: int, styles: StyleSheet1) -> List[Any]:

    '''
    It constructs the header flowable elements (title, count summary, and vertical spacing).

    Parameters
    ----------
     total_count:int
      The total number of detected non-followers

     styles:StyleSheet1
      The ReportLab sample stylesheet collection

    Outputs
    -------
     elements:List[Any]
      The list of flowable header elements
    '''

    return [
                Paragraph("Non-Followers Report", styles['Title']), 
                Spacer(SPACER_WIDTH, SPACER_HEIGHT),
                
                Paragraph(f'<font color="red"><b>Total Non-Followers: {total_count}</b></font>', styles['Normal']), 
                Spacer(SPACER_WIDTH, SPACER_HEIGHT)
            ]


def _build_table_style(num_rows: int) -> TableStyle:

    '''
    It constructs and returns the TableStyle configuration with centered header titles,
    an elegant slate palette, subtle borders, and alternating row backgrounds.

    Parameters
    ----------
     num_rows:int
      The total number of rows in the table (including the header row)

    Outputs
    -------
     TableStyle
      The configured TableStyle instance
    '''

    style_commands = [
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E293B')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('TOPPADDING', (0, 0), (-1, 0), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 9),

                        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                        ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
                        ('TOPPADDING', (0, 1), (-1, -1), 7),
                        ('BOTTOMPADDING', (0, 1), (-1, -1), 7),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),

                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94A3B8')),
                    ]

    for i in range(1, num_rows):

        bg_color = colors.HexColor('#FFFFFF') if i % 2 == 1 else colors.HexColor('#F8FAFC')
        style_commands.append(('BACKGROUND', (0, i), (-1, i), bg_color))


    return TableStyle(style_commands)


def _build_cell_styles(styles: StyleSheet1) -> tuple[ParagraphStyle, ParagraphStyle]:

    '''
    It constructs and returns the ParagraphStyle objects for regular table cells and date cells.

    Parameters
    ----------
     styles:StyleSheet1
      The ReportLab sample stylesheet collection

    Outputs
    -------
     tuple[ParagraphStyle, ParagraphStyle]
      A tuple containing (cell_style, date_style)
    '''

    cell_style = ParagraphStyle('ElegantCell', parent = styles['Normal'], fontName = 'Helvetica', fontSize = 9.5, leading = 13,
                                textColor = colors.HexColor('#334155'))
    date_style = ParagraphStyle('ElegantDate', parent = cell_style, alignment = 1, textColor = colors.HexColor('#64748B'))

    return cell_style, date_style


def _build_table(data: List[Dict], styles: StyleSheet1) -> Table:

    '''
    It converts the non-followers data into a formatted and styled ReportLab Table.

    Parameters
    ----------
     data:List[Dict]
      The list of dictionaries containing user details and unfollow dates

     styles:StyleSheet1
      The ReportLab sample stylesheet collection

    Outputs
    -------
     table:Table
      The styled ReportLab Table flowable element
    '''

    cell_style, date_style = _build_cell_styles(styles)

    table_data: List[List[Any]] = [["Username", "Profile URL", "Unfollow Date"]]

    for item in data:

        table_data.append([
                                    Paragraph(str(item.get('username', 'N/A')), cell_style),
                                    Paragraph(str(item.get('url', 'N/A')), cell_style),
                                    Paragraph(str(item.get('unfollow_date', 'N/A')), date_style)
                                ])

    table = Table(data = table_data, colWidths = [COL_WIDTH_USERNAME, COL_WIDTH_URL, COL_WIDTH_DATE], hAlign = 'LEFT')
    table.setStyle(_build_table_style(len(table_data)))

    return table


def export_to_pdf(data: List[Dict], filename: str = "non_followers_report.pdf") -> None:

    '''
    It generates a PDF report containing the non-followers list in a structured table.

    Parameters
    ----------
     data:List[Dict]
      The list of dictionaries containing user details and unfollow dates

     filename:str
      The output PDF file path or name (default: 'non_followers_report.pdf')

    Outputs
    -------
     None
    '''

    doc = SimpleDocTemplate(filename, pagesize = letter, leftMargin = MARGIN, rightMargin = MARGIN)
    styles = getSampleStyleSheet()

    elements = [*_build_header(len(data), styles), _build_table(data, styles)]

    doc.build(elements)
    console.print(f"[bold green]✓[/] Report successfully saved to [cyan]{filename}[/cyan]")