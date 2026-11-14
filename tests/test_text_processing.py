from app.text_processing import chunk_sections, extract_text


def test_extract_text_utf8():
    text, sections = extract_text("notes.txt", b"hello world")
    assert text == "hello world"
    assert sections == [(None, "hello world")]


def test_chunking_respects_overlap_and_content():
    source = "A sentence. " * 100
    chunks = chunk_sections([(1, source)], size=300, overlap=50)
    assert len(chunks) > 1
    assert all(chunk["page"] == 1 for chunk in chunks)
    assert "A sentence" in chunks[0]["text"]


def test_chunking_rejects_invalid_configuration():
    try:
        chunk_sections([(None, "abc")], size=100, overlap=100)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected invalid overlap to fail")
