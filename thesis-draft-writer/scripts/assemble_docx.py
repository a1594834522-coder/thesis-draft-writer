#!/usr/bin/env python3
"""Assemble a profile-aware DOCX package with minimal OOXML parts."""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


XML_HEADER = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
NS_MAIN = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
FRONT_MATTER_HEADINGS = {
    "封面",
    "独创性声明",
    "论文使用授权说明",
    "摘要",
    "关键词",
    "ABSTRACT",
    "目录",
}


def assemble_docx(manifest_path: str | Path, output_path: str | Path) -> None:
    manifest_path = Path(manifest_path)
    output_path = Path(output_path)
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    package = build_package(payload)
    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in package.items():
            archive.writestr(name, content)


def build_package(payload: dict) -> dict[str, str]:
    title = payload.get("title", "Untitled Thesis")
    sections = payload.get("sections", [])
    front_sections, body_sections = split_front_matter_sections(sections)
    front_header = resolve_front_header_text(payload)
    package = {
        "[Content_Types].xml": content_types_xml(),
        "_rels/.rels": root_rels_xml(),
        "docProps/core.xml": core_xml(title),
        "docProps/app.xml": app_xml(),
        "word/document.xml": document_xml(title, front_sections, body_sections),
        "word/styles.xml": styles_xml(),
        "word/settings.xml": settings_xml(),
        "word/fontTable.xml": font_table_xml(),
        "word/webSettings.xml": web_settings_xml(),
        "word/_rels/document.xml.rels": document_rels_xml(),
        "word/header1.xml": header_xml(front_header),
        "word/header2.xml": header_xml(title),
        "word/footer1.xml": footer_xml(page_format="roman"),
        "word/footer2.xml": footer_xml(page_format="arabic"),
    }
    return package


def resolve_front_header_text(payload: dict) -> str:
    explicit = str(payload.get("front_header_text", "")).strip()
    if explicit:
        return explicit
    for section in payload.get("sections", []):
        if str(section.get("heading", "")).strip() != "封面":
            continue
        blocks = split_body(section.get("body", ""))
        if blocks:
            return blocks[0]
    return "硕士学位论文"


def content_types_xml() -> str:
    return f"""{XML_HEADER}
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/settings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.settings+xml"/>
  <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
  <Override PartName="/word/webSettings.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.webSettings+xml"/>
  <Override PartName="/word/header1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/header2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.header+xml"/>
  <Override PartName="/word/footer1.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
  <Override PartName="/word/footer2.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.footer+xml"/>
</Types>
"""


def root_rels_xml() -> str:
    return f"""{XML_HEADER}
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def core_xml(title: str) -> str:
    title = escape(title)
    return f"""{XML_HEADER}
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{title}</dc:title>
  <dc:creator>Academic Manuscript</dc:creator>
</cp:coreProperties>
"""


def app_xml() -> str:
    return f"""{XML_HEADER}
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>Academic Word Processor</Application>
</Properties>
"""


def document_rels_xml() -> str:
    return f"""{XML_HEADER}
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/settings" Target="settings.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
  <Relationship Id="rId4" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/webSettings" Target="webSettings.xml"/>
  <Relationship Id="rId5" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header1.xml"/>
  <Relationship Id="rId6" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/header" Target="header2.xml"/>
  <Relationship Id="rId7" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer1.xml"/>
  <Relationship Id="rId8" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/footer" Target="footer2.xml"/>
</Relationships>
"""


def styles_xml() -> str:
    return f"""{XML_HEADER}
<w:styles xmlns:w="{NS_MAIN}">
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:spacing w:line="420" w:lineRule="auto"/>
      <w:jc w:val="left"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="BodyText">
    <w:name w:val="BodyText"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:jc w:val="left"/>
      <w:spacing w:line="420" w:lineRule="auto" w:before="0" w:after="0"/>
      <w:ind w:firstLine="480"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Title">
    <w:name w:val="Title"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:jc w:val="center"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="32"/><w:szCs w:val="32"/></w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="CoverTitle">
    <w:name w:val="CoverTitle"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:before="320" w:after="320"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
      <w:b/>
      <w:sz w:val="36"/>
      <w:szCs w:val="36"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="FrontHeading">
    <w:name w:val="FrontHeading"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:jc w:val="center"/><w:spacing w:before="240" w:after="240"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="黑体" w:hAnsi="Times New Roman"/>
      <w:b/>
      <w:sz w:val="32"/>
      <w:szCs w:val="32"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="CoverMeta">
    <w:name w:val="CoverMeta"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:jc w:val="left"/>
      <w:spacing w:before="120" w:after="120"/>
      <w:ind w:left="1440"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
      <w:sz w:val="28"/>
      <w:szCs w:val="28"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Signature">
    <w:name w:val="Signature"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr><w:jc w:val="right"/><w:spacing w:before="120" w:after="120"/></w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
      <w:sz w:val="24"/>
      <w:szCs w:val="24"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="FigureCaption">
    <w:name w:val="FigureCaption"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:jc w:val="center"/>
      <w:spacing w:before="120" w:after="120"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
      <w:sz w:val="22"/>
      <w:szCs w:val="22"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="TableCaption">
    <w:name w:val="TableCaption"/>
    <w:basedOn w:val="Normal"/>
    <w:qFormat/>
    <w:pPr>
      <w:jc w:val="center"/>
      <w:spacing w:before="120" w:after="120"/>
    </w:pPr>
    <w:rPr>
      <w:rFonts w:ascii="Times New Roman" w:eastAsia="宋体" w:hAnsi="Times New Roman"/>
      <w:sz w:val="22"/>
      <w:szCs w:val="22"/>
    </w:rPr>
  </w:style>
  <w:style w:type="paragraph" w:styleId="Heading1">
    <w:name w:val="heading 1"/>
    <w:basedOn w:val="BodyText"/>
    <w:qFormat/>
    <w:pPr><w:outlineLvl w:val="0"/></w:pPr>
    <w:rPr><w:b/><w:sz w:val="28"/><w:szCs w:val="28"/></w:rPr>
  </w:style>
</w:styles>
"""


def settings_xml() -> str:
    return f"""{XML_HEADER}
<w:settings xmlns:w="{NS_MAIN}">
  <w:evenAndOddHeaders/>
</w:settings>
"""


def font_table_xml() -> str:
    return f"""{XML_HEADER}
<w:fonts xmlns:w="{NS_MAIN}">
  <w:font w:name="Times New Roman"/>
  <w:font w:name="宋体"/>
</w:fonts>
"""


def web_settings_xml() -> str:
    return f"""{XML_HEADER}
<w:webSettings xmlns:w="{NS_MAIN}"/>
"""


def header_xml(text: str) -> str:
    return f"""{XML_HEADER}
<w:hdr xmlns:w="{NS_MAIN}">
  <w:p>
    <w:pPr><w:jc w:val="center"/></w:pPr>
    <w:r><w:t>{escape(text)}</w:t></w:r>
  </w:p>
</w:hdr>
"""


def footer_xml(page_format: str) -> str:
    if page_format == "roman":
        page_instr = " PAGE \\\\* ROMAN "
    else:
        page_instr = " PAGE "
    return f"""{XML_HEADER}
<w:ftr xmlns:w="{NS_MAIN}">
  <w:p>
    <w:pPr><w:jc w:val="center"/></w:pPr>
    <w:r><w:fldChar w:fldCharType="begin"/></w:r>
    <w:r><w:instrText xml:space="preserve">{page_instr}</w:instrText></w:r>
    <w:r><w:fldChar w:fldCharType="end"/></w:r>
  </w:p>
</w:ftr>
"""


def document_xml(title: str, front_sections: list[dict], body_sections: list[dict]) -> str:
    parts = [f'{XML_HEADER}\n<w:document xmlns:w="{NS_MAIN}" xmlns:r="{NS_REL}"><w:body>']
    has_toc_heading = any(section.get("heading") == "目录" for section in front_sections + body_sections)
    inserted_toc = False
    for index, section in enumerate(front_sections):
        if index > 0:
            parts.append(page_break())
        parts.append(render_section(section, front_matter=True))
        if section.get("heading") == "目录":
            parts.append(toc_field_paragraph())
            inserted_toc = True
    if front_sections and not has_toc_heading:
        parts.append(page_break())
        parts.append(toc_field_paragraph())
        inserted_toc = True
    if front_sections and body_sections:
        parts.append(section_break("front"))
    for index, section in enumerate(body_sections):
        if index > 0:
            parts.append(page_break())
        parts.append(render_section(section, front_matter=False))
        if section.get("heading") == "目录" and not inserted_toc:
            parts.append(toc_field_paragraph())
            inserted_toc = True
    parts.append(final_section_properties())
    parts.append("</w:body></w:document>")
    return "".join(parts)


def split_front_matter_sections(sections: list[dict]) -> tuple[list[dict], list[dict]]:
    split_index = 0
    for index, section in enumerate(sections):
        heading = str(section.get("heading", "")).strip()
        if heading in FRONT_MATTER_HEADINGS:
            split_index = index + 1
            continue
        break
    if split_index == 0:
        return [], sections
    return sections[:split_index], sections[split_index:]


def render_section(section: dict, front_matter: bool = False) -> str:
    heading = section.get("heading", "")
    body = section.get("body", "")
    if heading == "封面":
        return render_cover_section(section)
    heading_style = "FrontHeading" if front_matter else "Heading1"
    xml = [paragraph(heading, style=heading_style)]
    for block in split_body(body):
        body_style = body_style_for_block(heading, block, front_matter=front_matter)
        xml.append(paragraph(block, style=body_style))
    return "".join(xml)


def render_cover_section(section: dict) -> str:
    blocks = split_body(section.get("body", ""))
    cover_heading = blocks[0] if blocks else "硕士学位论文"
    xml = [paragraph(cover_heading, style="FrontHeading")]
    for index, block in enumerate(blocks):
        if block == cover_heading:
            continue
        if index <= 1:
            xml.append(paragraph(block, style="CoverTitle"))
        else:
            xml.append(paragraph(block, style="CoverMeta"))
    return "".join(xml)


def body_style_for_block(heading: str, block: str, front_matter: bool = False) -> str:
    if is_signature_block(heading, block, front_matter=front_matter):
        return "Signature"
    if is_figure_caption_block(block):
        return "FigureCaption"
    if is_table_caption_block(block):
        return "TableCaption"
    if front_matter and heading in {"摘要", "ABSTRACT"}:
        return "BodyText"
    if heading == "关键词":
        return "CoverMeta"
    if front_matter:
        return "BodyText"
    return "BodyText"


def is_signature_block(heading: str, block: str, front_matter: bool = False) -> bool:
    if not front_matter:
        return False
    if heading not in {"独创性声明", "论文使用授权说明"}:
        return False
    return "签名" in block or block.startswith("日期：")


def is_figure_caption_block(block: str) -> bool:
    return bool(re.match(r"^(图|Figure)\s*\d+", block.strip(), flags=re.IGNORECASE))


def is_table_caption_block(block: str) -> bool:
    return bool(re.match(r"^(表|Table)\s*\d+", block.strip(), flags=re.IGNORECASE))


def split_body(body: str) -> list[str]:
    chunks = [item.strip() for item in str(body).split("\n") if item.strip()]
    return chunks or [""]


def paragraph(text: str, style: str = "Normal") -> str:
    safe = escape(text)
    if not safe:
        return f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr></w:p>'
    return (
        f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
        f'<w:r><w:t xml:space="preserve">{safe}</w:t></w:r></w:p>'
    )


def toc_field_paragraph() -> str:
    return (
        '<w:p><w:pPr><w:pStyle w:val="Normal"/></w:pPr>'
        '<w:r><w:fldChar w:fldCharType="begin"/></w:r>'
        '<w:r><w:instrText xml:space="preserve">TOC \\\\o "1-3" \\\\h \\\\z \\\\u</w:instrText></w:r>'
        '<w:r><w:fldChar w:fldCharType="separate"/></w:r>'
        '<w:r><w:t xml:space="preserve"></w:t></w:r>'
        '<w:r><w:fldChar w:fldCharType="end"/></w:r>'
        '</w:p>'
    )


def page_break() -> str:
    return '<w:p><w:r><w:br w:type="page"/></w:r></w:p>'


def section_break(kind: str) -> str:
    if kind == "front":
        return (
            '<w:p><w:pPr><w:sectPr>'
            '<w:headerReference w:type="default" r:id="rId5"/>'
            '<w:headerReference w:type="even" r:id="rId6"/>'
            '<w:footerReference w:type="default" r:id="rId7"/>'
            '<w:footerReference w:type="even" r:id="rId7"/>'
            '<w:titlePg/>'
            '<w:pgNumType w:fmt="upperRoman" w:start="1"/>'
            '<w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1701" w:right="1417" w:bottom="1417" w:left="1701" w:header="1134" w:footer="1134" w:gutter="0"/>'
            '<w:type w:val="nextPage"/>'
            '</w:sectPr></w:pPr></w:p>'
        )
    raise ValueError(f"Unknown section kind: {kind}")


def final_section_properties() -> str:
    return (
        '<w:sectPr>'
        '<w:headerReference w:type="default" r:id="rId5"/>'
        '<w:headerReference w:type="even" r:id="rId6"/>'
        '<w:footerReference w:type="default" r:id="rId8"/>'
        '<w:footerReference w:type="even" r:id="rId8"/>'
        '<w:pgNumType w:start="1"/>'
        '<w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1701" w:right="1417" w:bottom="1417" w:left="1701" w:header="1134" w:footer="1134" w:gutter="0"/>'
        '</w:sectPr>'
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest_path")
    parser.add_argument("output_path")
    args = parser.parse_args()
    assemble_docx(args.manifest_path, args.output_path)


if __name__ == "__main__":
    main()
