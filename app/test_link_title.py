"""link_title — tarmoq'siz unit testlar."""

from app.link_title import clean_title, extract_urls_from_text


def test_extract_urls():
    text = "Ko‘ring: https://www.youtube.com/watch?v=abc123 va yana https://imdb.com/title/tt1/"
    urls = extract_urls_from_text(text)
    assert len(urls) == 2
    assert urls[0].startswith("https://www.youtube.com")


def test_extract_urls_trims_punctuation():
    urls = extract_urls_from_text("Link: https://youtu.be/abc).")
    assert urls == ["https://youtu.be/abc"]


def test_clean_title_strips_junk():
    assert "Inception" in clean_title("Watch Inception (2010) Full Movie HD | Free Online")
    assert clean_title("Dune: Part Two - YouTube").startswith("Dune")
    assert clean_title("") == ""
    assert "Побег" in clean_title("Смотреть Побег из Шоушенка онлайн")