from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.platypus import TableStyle
from reportlab.lib import colors

# Dimensions & Layout
PAGE_WIDTH, _ = letter
MARGIN = 40
PRINTABLE_WIDTH = PAGE_WIDTH - (2 * MARGIN)

CARD_SPACING = 14
CARD_WIDTH = (PRINTABLE_WIDTH - (3 * CARD_SPACING)) / 4
CARD_HEIGHT_VAL = 32
CARD_HEIGHT_LBL = 22

COL_WIDTH_INDEX = 36
COL_WIDTH_USERNAME = 120
COL_WIDTH_URL = 240
COL_WIDTH_DATE = 136
TABLE_COL_WIDTHS = [COL_WIDTH_INDEX, COL_WIDTH_USERNAME, COL_WIDTH_URL, COL_WIDTH_DATE]

SPACER_TITLE_SUBTITLE = 4
SPACER_SUBTITLE_CARDS = 16
SPACER_CARDS_TABLE = 16

# Palette & Colors
COLOR_TITLE = "#111827"
COLOR_SUBTITLE = "#6B7280"
COLOR_CARD_BORDER = "#D1D5DB"
COLOR_TABLE_BORDER = "#D1D5DB"
COLOR_TABLE_INNERGRID = "#E5E7EB"
COLOR_HEADER_BG = "#F9FAFB"
COLOR_HEADER_TEXT = "#374151"
COLOR_ROW_BG_WHITE = "#FFFFFF"
COLOR_ROW_BG_LIGHT = "#F9FAFB"
COLOR_CELL_TEXT = "#4B5563"
COLOR_LINK = "#2563EB"

COLOR_BLUE = "#2563EB"
COLOR_GREEN = "#16A34A"
COLOR_RED = "#DC2626"
COLOR_AMBER = "#D97706"

# Content & Labels
REPORT_TITLE = "Who is the Mole? The Full Non-Followers Report"
TABLE_HEADERS = ["#", "Username", "Profile URL", "Unfollow Date"]

# Typography & Paragraph Styles
STYLE_TITLE = ParagraphStyle(
                                name = 'ReportTitle',
                                fontName = 'Helvetica-Bold',
                                fontSize = 18,
                                leading = 22,
                                textColor = colors.HexColor(COLOR_TITLE)
                            )

STYLE_SUBTITLE = ParagraphStyle(
                                    name = 'ReportSubtitle',
                                    fontName = 'Helvetica',
                                    fontSize = 9,
                                    leading = 12,
                                    textColor = colors.HexColor(COLOR_SUBTITLE)
                                )

STYLE_HEADER = ParagraphStyle(
                                name = 'TableHeader',
                                fontName = 'Helvetica-Bold',
                                fontSize = 9,
                                leading = 11,
                                textColor = colors.HexColor(COLOR_HEADER_TEXT)
                            )

STYLE_HEADER_CENTER = ParagraphStyle(
                                        name = 'TableHeaderCenter',
                                        parent = STYLE_HEADER,
                                        alignment = 1
                                    )

STYLE_CELL = ParagraphStyle(
                                name = 'TableCell',
                                fontName = 'Helvetica',
                                fontSize = 9,
                                leading = 11,
                                textColor = colors.HexColor(COLOR_CELL_TEXT)
                            )

STYLE_CELL_CENTER = ParagraphStyle(
                                        name = 'TableCellCenter',
                                        parent = STYLE_CELL,
                                        alignment = 1
                                    )

STYLE_URL = ParagraphStyle(
                                name = 'TableUrl',
                                fontName = 'Helvetica',
                                fontSize = 9,
                                leading = 11,
                                textColor = colors.HexColor(COLOR_LINK)
                            )


def get_card_val_style(label: str, color_hex: str) -> ParagraphStyle:

    '''
    It returns a ParagraphStyle for a card's numeric metric value.

    Parameters
    ----------
     label:str
      The label identifying the metric card

     color_hex:str
      The hex color code for the value font

    Outputs
    -------
     style:ParagraphStyle
      The configured ParagraphStyle for the card value
    '''

    return ParagraphStyle(
                            name = f'CardVal_{label}',
                            fontName = 'Helvetica-Bold',
                            fontSize = 20,
                            leading = 22,
                            alignment = 1,
                            textColor = colors.HexColor(color_hex)
                        )


def get_card_lbl_style(label: str) -> ParagraphStyle:

    '''
    It returns a ParagraphStyle for a card's text label.

    Parameters
    ----------
     label:str
      The label identifying the metric card

    Outputs
    -------
     style:ParagraphStyle
      The configured ParagraphStyle for the card label
    '''

    return ParagraphStyle(
                            name = f'CardLbl_{label}',
                            fontName = 'Helvetica',
                            fontSize = 9,
                            leading = 11,
                            alignment = 1,
                            textColor = colors.HexColor(COLOR_SUBTITLE)
                        )


# Table Styles
TABLE_STYLE_CARD = TableStyle([
                                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(COLOR_CARD_BORDER)),
                                        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                                        ('TOPPADDING', (0, 0), (-1, 0), 8),
                                        ('BOTTOMPADDING', (0, 0), (-1, 0), 1),
                                        ('TOPPADDING', (0, 1), (-1, 1), 1),
                                        ('BOTTOMPADDING', (0, 1), (-1, 1), 8),
                                        ('LEFTPADDING', (0, 0), (-1, -1), 4),
                                        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
                                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                        ('BACKGROUND', (0, 0), (-1, -1), colors.white)
                                    ])

TABLE_STYLE_CARDS_ROW = TableStyle([
                            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                            ('LEFTPADDING', (0, 0), (-1, -1), 0),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                            ('TOPPADDING', (0, 0), (-1, -1), 0),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
                        ])


def get_table_style(has_data: bool = True) -> TableStyle:

    '''
    It constructs the TableStyle for the main non-followers table, including header
    background and alternating row fills when data is present.

    Parameters
    ----------
     has_data:bool
      Whether data rows exist to apply alternating row backgrounds

    Outputs
    -------
     style:TableStyle
      The configured TableStyle instance
    '''

    table_style = [
                        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(COLOR_TABLE_BORDER)),
                        ('ROUNDEDCORNERS', [6, 6, 6, 6]),
                        ('LINEBELOW', (0, 0), (-1, 0), 1, colors.HexColor(COLOR_TABLE_BORDER)),
                        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor(COLOR_TABLE_INNERGRID)),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(COLOR_HEADER_BG)),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]

    if has_data:
        table_style.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor(COLOR_ROW_BG_WHITE), colors.HexColor(COLOR_ROW_BG_LIGHT)]))

    return TableStyle(table_style)