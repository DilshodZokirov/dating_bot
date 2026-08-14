"""link_title — tarmoq'siz unit testlar."""

from app.link_title import (
    _host_matches,
    _pick_best_title,
    clean_title,
    extract_movie_name,
    extract_urls_from_text,
)


def test_extract_urls():
    text = "Ko‘ring: https://www.youtube.com/watch?v=abc123 va yana https://imdb.com/title/tt1/"
    urls = extract_urls_from_text(text)
    assert len(urls) == 2
    assert urls[0].startswith("https://www.youtube.com")


def test_extract_urls_trims_punctuation():
    urls = extract_urls_from_text("Link: https://youtu.be/abc).")
    assert urls == ["https://youtu.be/abc"]


def test_extract_social_urls():
    text = "IG https://www.instagram.com/reel/ABC123/ TT https://vm.tiktok.com/ZMabc/"
    urls = extract_urls_from_text(text)
    assert any("instagram.com" in u for u in urls)
    assert any("tiktok.com" in u for u in urls)


def test_clean_title_strips_junk():
    assert "Inception" in clean_title("Watch Inception (2010) Full Movie HD | Free Online")
    assert clean_title("Dune: Part Two - YouTube").startswith("Dune")
    assert clean_title("") == ""
    assert "Побег" in clean_title("Смотреть Побег из Шоушенка онлайн")


def test_clean_instagram_caption_form():
    raw = 'kino_uz on Instagram: "Interstellar (2014) — ko‘ring"'
    assert "Interstellar" in clean_title(raw)


def test_generic_platform_titles_empty():
    assert clean_title("Instagram") == ""
    assert clean_title("TikTok") == ""
    assert clean_title("TikTok - Make Your Day") == ""


def test_extract_tiktok_desc_helper():
    from app.link_title import _extract_tiktok_desc_from_html

    html = '''<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__">{"a":{"item":{"id":"1","desc":"Inception (2010) trailer","stats":{}}}}</script>'''
    assert "Inception" in _extract_tiktok_desc_from_html(html)


def test_extract_instagram_caption_helper():
    from app.link_title import _extract_instagram_caption_from_html

    html = r'{"caption":{"text":"Interstellar (2014) film"}}'
    assert "Interstellar" in _extract_instagram_caption_from_html(html)


def test_host_matches():
    assert _host_matches("www.tiktok.com", ("tiktok.com", "vm.tiktok.com"))
    assert _host_matches("vm.tiktok.com", ("tiktok.com", "vm.tiktok.com"))
    assert _host_matches("instagram.com", ("instagram.com", "instagr.am"))
    assert not _host_matches("notinstagram.com", ("instagram.com",))


def test_rejects_instagram_prose_caption():
    caption = (
        "Tonight, V stepped into the crowd, taking in live performances at "
        "Vogue World: Hollywood. Known for his own standout fashion moments, "
        "he kept it effortlessly stylish in a look worthy of the runway."
    )
    assert extract_movie_name(caption) == ""
    assert _pick_best_title(caption, social=True) == ""


def test_extracts_movie_from_caption_with_year():
    caption = "🎬 Inception (2010)\nTonight, V stepped into the crowd at the premiere."
    assert extract_movie_name(caption) == "Inception (2010)"


def test_extracts_labeled_movie_name():
    assert "Interstellar" in extract_movie_name("Kino: Interstellar (2014)\nTomosha qiling")
