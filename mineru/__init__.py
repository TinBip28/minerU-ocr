# Copyright (c) Opendatalab. All rights reserved.
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .parser import (
        DocumentParser,
        DocxParser,
        HtmlParser,
        MinerUApiParser,
        ParseResult,
        PdfFlashParser,
        PdfHybridParser,
        PdfPipelineParser,
        PdfVlmParser,
        PptxParser,
        XlsxParser,
        parse,
    )
    from .types import Block, Line, PageInfo, Span

__all__ = [
    "Block",
    "DocumentParser",
    "DocxParser",
    "HtmlParser",
    "Line",
    "MinerUApiParser",
    "PageInfo",
    "ParseResult",
    "PdfFlashParser",
    "PdfHybridParser",
    "PdfPipelineParser",
    "PdfVlmParser",
    "PptxParser",
    "Span",
    "XlsxParser",
    "parse",
]


def __getattr__(name: str):
    if name in {
        "DocumentParser",
        "DocxParser",
        "HtmlParser",
        "MinerUApiParser",
        "ParseResult",
        "PdfFlashParser",
        "PdfHybridParser",
        "PdfPipelineParser",
        "PdfVlmParser",
        "PptxParser",
        "XlsxParser",
        "parse",
    }:
        from . import parser

        return getattr(parser, name)
    if name in {"Block", "Line", "PageInfo", "Span"}:
        from . import types

        return getattr(types, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
