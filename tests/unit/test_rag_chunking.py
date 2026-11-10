from app.rag.chunking import chunk_markdown

MD = "# T\n\n## Refund Policy\n\nPara one.\n\n## Late Delivery\n\nPara two.\n\nPara three.\n"


def test_chunk_by_heading():
    chunks = chunk_markdown(MD, "f.md")
    assert [c.id for c in chunks] == ["refund-policy-0", "late-delivery-0"]
    assert chunks[0].title == "Refund Policy"


def test_long_section_splits_by_paragraph():
    chunks = chunk_markdown(MD, "f.md", max_chars=15)
    assert [c.id for c in chunks] == ["refund-policy-0", "late-delivery-0", "late-delivery-1"]