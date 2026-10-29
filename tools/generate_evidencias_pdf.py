from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "aluno" / "TEMPLATE_EVIDENCIAS.md"
OUTPUT = ROOT / "aluno" / "EVIDENCIAS_PIPELINE.pdf"

NAVY = colors.HexColor("#102A43")
BLUE = colors.HexColor("#1677A7")
CYAN = colors.HexColor("#28A9C7")
PALE = colors.HexColor("#EAF5F8")
LIGHT = colors.HexColor("#F4F7FA")
MID = colors.HexColor("#D7E2EA")
INK = colors.HexColor("#243B53")
MUTED = colors.HexColor("#627D98")
GREEN = colors.HexColor("#198754")


def register_fonts() -> tuple[str, str, str]:
    font_dir = Path("C:/Windows/Fonts")
    choices = [
        ("Aptos", "aptos.ttf", "aptosb.ttf", "aptosmono.ttf"),
        ("SegoeUI", "segoeui.ttf", "segoeuib.ttf", "consola.ttf"),
        ("DejaVuSans", "DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSansMono.ttf"),
    ]
    for family, regular, bold, mono in choices:
        paths = [font_dir / regular, font_dir / bold, font_dir / mono]
        if all(path.exists() for path in paths):
            pdfmetrics.registerFont(TTFont(family, str(paths[0])))
            pdfmetrics.registerFont(TTFont(f"{family}-Bold", str(paths[1])))
            pdfmetrics.registerFont(TTFont(f"{family}-Mono", str(paths[2])))
            return family, f"{family}-Bold", f"{family}-Mono"
    return "Helvetica", "Helvetica-Bold", "Courier"


FONT, FONT_BOLD, FONT_MONO = register_fonts()


def ascii_punctuation(text: str) -> str:
    replacements = {
        "\u2010": "-",
        "\u2011": "-",
        "\u2012": "-",
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return unicodedata.normalize("NFC", text)


def inline_markup(text: str) -> str:
    text = ascii_punctuation(text)
    tokens: dict[str, str] = {}

    def stash(value: str) -> str:
        key = f"@@TOKEN{len(tokens)}@@"
        tokens[key] = value
        return key

    text = re.sub(
        r"<((?:https?://)[^>]+)>",
        lambda m: stash(f'<link href="{escape(m.group(1))}" color="#1677A7">{escape(m.group(1))}</link>'),
        text,
    )
    text = re.sub(
        r"`([^`]+)`",
        lambda m: stash(f'<font name="{FONT_MONO}" size="7.5" color="#102A43">{escape(m.group(1))}</font>'),
        text,
    )
    text = escape(text)
    text = re.sub(r"\*\*([^*]+)\*\*", rf'<font name="{FONT_BOLD}">\1</font>', text)
    for key, value in tokens.items():
        text = text.replace(key, value)
    return text


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        "TitleCustom",
        parent=styles["Title"],
        fontName=FONT_BOLD,
        fontSize=23,
        leading=28,
        textColor=NAVY,
        alignment=TA_LEFT,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        "SubtitleCustom",
        parent=styles["Normal"],
        fontName=FONT,
        fontSize=10.5,
        leading=14,
        textColor=BLUE,
        spaceAfter=18,
    )
)
styles.add(
    ParagraphStyle(
        "H1Custom",
        parent=styles["Heading1"],
        fontName=FONT_BOLD,
        fontSize=16,
        leading=20,
        textColor=NAVY,
        spaceBefore=8,
        spaceAfter=9,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "H2Custom",
        parent=styles["Heading2"],
        fontName=FONT_BOLD,
        fontSize=12.5,
        leading=16,
        textColor=BLUE,
        spaceBefore=8,
        spaceAfter=6,
        keepWithNext=True,
    )
)
styles.add(
    ParagraphStyle(
        "BodyCustom",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=9.2,
        leading=13.2,
        textColor=INK,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        "BulletCustom",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=9,
        leading=12.5,
        leftIndent=13,
        firstLineIndent=-7,
        bulletIndent=4,
        textColor=INK,
        spaceAfter=3,
    )
)
styles.add(
    ParagraphStyle(
        "MetaCustom",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=9.3,
        leading=13,
        textColor=INK,
        spaceAfter=4,
    )
)
styles.add(
    ParagraphStyle(
        "CaptionCustom",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=7.5,
        leading=10,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        "TableHeader",
        parent=styles["BodyText"],
        fontName=FONT_BOLD,
        fontSize=7.1,
        leading=9.2,
        textColor=colors.white,
    )
)
styles.add(
    ParagraphStyle(
        "TableCell",
        parent=styles["BodyText"],
        fontName=FONT,
        fontSize=6.8,
        leading=9.1,
        textColor=INK,
    )
)


class ReportDoc(BaseDocTemplate):
    def __init__(self, filename: str):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=18 * mm,
            rightMargin=18 * mm,
            topMargin=18 * mm,
            bottomMargin=18 * mm,
            title="Relatorio de Evidencias Tecnicas - Clube Aurora",
            author="Gustavo Duarte Lepesteur da Costa",
            subject="Projeto Final DevSecOps 1746 - Trilha 3",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="content",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates(PageTemplate(id="report", frames=[frame], onPage=self.draw_page))

    def draw_page(self, canvas, doc):
        canvas.saveState()
        width, height = A4
        canvas.setFillColor(NAVY)
        canvas.rect(0, height - 7 * mm, width, 7 * mm, stroke=0, fill=1)
        canvas.setStrokeColor(MID)
        canvas.line(doc.leftMargin, 12 * mm, width - doc.rightMargin, 12 * mm)
        canvas.setFont(FONT, 7.2)
        canvas.setFillColor(MUTED)
        canvas.drawString(doc.leftMargin, 7.5 * mm, "Gustavo Duarte Lepesteur da Costa | DevSecOps 1746")
        canvas.drawRightString(width - doc.rightMargin, 7.5 * mm, f"Pagina {doc.page}")
        canvas.restoreState()


def table_from_rows(rows: list[list[str]], column_count: int) -> Table:
    widths = {
        3: [28 * mm, 47 * mm, 99 * mm],
        4: [22 * mm, 52 * mm, 38 * mm, 62 * mm],
    }[column_count]
    converted = []
    for row_index, row in enumerate(rows):
        style = styles["TableHeader"] if row_index == 0 else styles["TableCell"]
        converted.append([Paragraph(inline_markup(cell), style) for cell in row])
    table = Table(converted, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, MID),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
            ]
        )
    )
    return table


def scaled_image(path: Path, max_width: float, max_height: float) -> Image:
    image = Image(str(path))
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale
    image.hAlign = "CENTER"
    return image


def caption_for(filename: str) -> str:
    captions = {
        "pipeline-inicial-falha.png": "Figura 1 - Pipeline inicial com os Quality Gates reprovados.",
        "pipeline-final-sucesso.png": "Figura 2 - Pipeline final com os Quality Gates aprovados.",
        "branch-protection-pr.png": "Figura 3 - Regra de protecao exigindo Pull Request para a main.",
        "branch-protection-checks.png": "Figura 4 - Quality Gates obrigatorios e configuracoes da protecao.",
    }
    return captions[filename]


def parse_markdown() -> list:
    lines = SOURCE.read_text(encoding="utf-8").splitlines()
    story: list = []
    paragraph_lines: list[str] = []
    index = 0

    def flush_paragraph() -> None:
        if paragraph_lines:
            text = " ".join(line.strip() for line in paragraph_lines)
            story.append(Paragraph(inline_markup(text), styles["BodyCustom"]))
            paragraph_lines.clear()

    while index < len(lines):
        line = lines[index].strip()
        if not line or line == "---":
            flush_paragraph()
            if line == "---":
                story.append(Spacer(1, 3 * mm))
            index += 1
            continue

        if line.startswith("# "):
            flush_paragraph()
            title = line[2:].strip()
            if "(" in title:
                main, remainder = title.split("(", 1)
                story.append(Paragraph(inline_markup(main.strip()), styles["TitleCustom"]))
                story.append(Paragraph(inline_markup("(" + remainder), styles["SubtitleCustom"]))
            else:
                story.append(Paragraph(inline_markup(title), styles["TitleCustom"]))
            index += 1
            continue

        if line.startswith("## "):
            flush_paragraph()
            if story:
                story.append(Spacer(1, 1.5 * mm))
            story.append(Paragraph(inline_markup(line[3:]), styles["H1Custom"]))
            index += 1
            continue

        if line.startswith("### "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[4:]), styles["H2Custom"]))
            index += 1
            continue

        if line.startswith("!["):
            flush_paragraph()
            match = re.match(r"!\[([^]]*)\]\(([^)]+)\)", line)
            if not match:
                raise ValueError(f"Imagem invalida: {line}")
            image_path = SOURCE.parent / match.group(2)
            filename = image_path.name
            image = scaled_image(image_path, 174 * mm, 116 * mm)
            caption = Paragraph(inline_markup(caption_for(filename)), styles["CaptionCustom"])
            story.append(KeepTogether([image, caption]))
            index += 1
            continue

        if line.startswith("| "):
            flush_paragraph()
            table_rows: list[list[str]] = []
            while index < len(lines) and lines[index].strip().startswith("|"):
                raw = lines[index].strip()
                cells = [cell.strip() for cell in raw.strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
                    table_rows.append(cells)
                index += 1
            story.append(table_from_rows(table_rows, len(table_rows[0])))
            story.append(Spacer(1, 3 * mm))
            continue

        if line.startswith("- "):
            flush_paragraph()
            story.append(Paragraph(inline_markup(line[2:]), styles["BulletCustom"], bulletText="-"))
            index += 1
            continue

        if line.startswith("**") and ":**" in line:
            flush_paragraph()
            story.append(Paragraph(inline_markup(line), styles["MetaCustom"]))
            index += 1
            continue

        paragraph_lines.append(line)
        index += 1

    flush_paragraph()
    return story


def main() -> None:
    if not SOURCE.exists():
        raise FileNotFoundError(SOURCE)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = ReportDoc(str(OUTPUT))
    story = parse_markdown()
    doc.build(story)
    print(OUTPUT)


if __name__ == "__main__":
    main()
