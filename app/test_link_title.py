"""link_title — unit testlar (tarmoq'siz + ixtiyoriy live)."""

from app.link_title import (
    _host_matches,
    clean_title,
    extract_urls_from_text,
    normalize_movie_hit,
    parse_yandex_cbir_hits,
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


def test_normalize_yandex_subtitle():
    assert normalize_movie_hit("Начало", "Inception, 2010 (18+)") == "Inception (2010)"


def test_parse_yandex_cbir_hits():
    html = (
        '&quot;cbirObjectResponses&quot;:{&quot;objectResponses&quot;:[{'
        '&quot;entityId&quot;:&quot;ruw1&quot;,'
        '&quot;title&quot;:&quot;Начало&quot;,'
        '&quot;subtitle&quot;:&quot;Inception, 2010 (18+)&quot;,'
        '&quot;description&quot;:&quot;plot&quot;}]}'
    )
    hits = parse_yandex_cbir_hits(html)
    assert hits
    assert hits[0]["title"] == "Inception (2010)"


def test_host_matches():
    assert _host_matches("www.tiktok.com", ("tiktok.com", "vm.tiktok.com"))
    assert _host_matches("instagram.com", ("instagram.com", "instagr.am"))
    assert not _host_matches("notinstagram.com", ("instagram.com",))


def test_caption_prose_is_not_used_as_page_title_fallback():
    # clean_title may keep short text, but looks_like_prose guards answers
    from app.link_title import looks_like_prose

    caption = (
        "Tonight, V stepped into the crowd, taking in live performances at "
        "Vogue World: Hollywood. Known for his own standout fashion moments."
    )
    assert looks_like_prose(caption)


def test_normalize_instagram_tracking_params():
    from app.link_title import normalize_media_url

    dirty = "https://www.instagram.com/reel/DbYLVjjsF2U/?igsh=MXhtN2Q4dWE4b2tj"
    assert normalize_media_url(dirty) == "https://www.instagram.com/reel/DbYLVjjsF2U/"


def test_extract_jpeg_frame_from_video():
    import subprocess
    import tempfile
    from pathlib import Path

    from app.link_title import extract_jpeg_frame_from_video

    with tempfile.TemporaryDirectory() as tmp:
        vid = Path(tmp) / "t.mp4"
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-f",
                "lavfi",
                "-i",
                "color=c=red:s=160x120:d=1",
                "-c:v",
                "libx264",
                "-t",
                "1",
                str(vid),
            ],
            capture_output=True,
            check=True,
        )
        frame = extract_jpeg_frame_from_video(vid.read_bytes(), 0.2)
        assert frame and frame[:2] == b"\xff\xd8"
