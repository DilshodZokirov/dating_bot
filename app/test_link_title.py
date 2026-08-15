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
    assert normalize_media_url(dirty) == "https://instagram.com/reel/DbYLVjjsF2U/"
    # Bir xil reel — tracking farq qilsa ham bir xil kalit
    a = normalize_media_url(
        "https://www.instagram.com/reel/Db09RZOCSG-/?igsh=aaa"
    )
    b = normalize_media_url(
        "https://instagram.com/reel/Db09RZOCSG-/?igsh=bbb&igsi=ccc"
    )
    assert a == b == "https://instagram.com/reel/Db09RZOCSG-/"


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


def test_yt_dlp_fetch_returns_dict_on_failure():
    from app.link_title import yt_dlp_fetch_for_identify

    out = yt_dlp_fetch_for_identify("https://www.instagram.com/reel/NOTAREALID999/")
    assert isinstance(out, dict)
    assert "thumbnail_url" in out and "video_bytes" in out and "error" in out


def test_extract_movie_from_ocr_uzbek_title():
    from app.link_title import extract_movie_from_ocr_text

    text = "Osmondan tushgan fil 2023 — o'zbekcha nom. Multfilm kodi: 833"
    got = extract_movie_from_ocr_text(text)
    assert "Osmondan tushgan fil" in got
    assert "2023" in got


def test_parse_gemini_movie_json():
    from app.link_title import _parse_gemini_movie_json

    raw = (
        '```json\n{"found":true,"title":"Osmondan tushgan fil (2023)",'
        '"summary":"Fil fil haqida ertak."}\n```'
    )
    parsed = _parse_gemini_movie_json(raw)
    assert parsed and parsed["found"] is True
    assert "Osmondan tushgan fil" in parsed["title"]
    assert "ertak" in parsed["summary"]

    assert _parse_gemini_movie_json('{"found":false}') == {"found": False}


def test_link_found_i18n_has_summary_not_source():
    from app.i18n import t

    msg = t(
        "uz",
        "link_found",
        title="Osmondan tushgan fil (2023)",
        summary="Sehrgarning fili haqida multfilm.",
    )
    assert "Osmondan tushgan fil" in msg
    assert "Sehrgarning" in msg
    assert "Manba" not in msg
    assert "source" not in msg.lower()
    assert "yuborilmaydi" not in msg


def test_link_progress_i18n_steps():
    from app.i18n import TRANSLATIONS, t

    for step in (
        "download",
        "preview",
        "auto_dl",
        "frame",
        "ai",
        "search",
        "localize",
    ):
        key = f"link_progress_{step}"
        assert key in TRANSLATIONS
        uz = t("uz", key)
        assert uz and uz != key
        assert "…" in uz or "..." in uz


def test_movie_cache_key_stable_for_same_reel():
    from app.link_title import _movie_cache_key, normalize_media_url

    u1 = "https://www.instagram.com/reel/Db09RZOCSG-/?igsh=aaa"
    u2 = "https://instagram.com/reel/Db09RZOCSG-/?igsh=bbb"
    assert normalize_media_url(u1) == normalize_media_url(u2)
    assert _movie_cache_key(u1, "uz") == _movie_cache_key(u2, "uz")
    assert _movie_cache_key(u1, "uz") != _movie_cache_key(u1, "ru")
    from app.link_title import titles_same_movie

    assert titles_same_movie("Inception (2010)", "Inception (2010)")
    assert titles_same_movie("Osmondan tushgan fil (2023)", "Osmondan tushgan fil 2023")
    # Boshqa film — yil farq
    assert not titles_same_movie("Inception (2010)", "Interstellar (2014)")
    # Boshqa nom, bir xil yozuv, umumiy so‘z yo‘q
    assert not titles_same_movie(
        "Osmondan tushgan fil (2023)", "Frozen (2013)"
    )
    # Tarjima (kirill) + bir xil yil
    assert titles_same_movie("Inception (2010)", "Начало (2010)")


def test_parse_gemini_keeps_title_raw():
    from app.link_title import _parse_gemini_movie_json

    raw = (
        '{"found":true,"title_raw":"Osmondan tushgan fil (2023)",'
        '"title":"The Magician\'s Elephant (2023)",'
        '"summary":"Fil haqida."}'
    )
    parsed = _parse_gemini_movie_json(raw)
    assert parsed["title_raw"].startswith("Osmondan")
    assert "Magician" in parsed["title"] or "Elephant" in parsed["title"]


def test_parse_gemini_candidates_mode():
    from app.link_title import _parse_gemini_movie_json, uncertain_movie_result

    raw = (
        '{"mode":"candidates","candidates":['
        '"Orzular jamoasi (2012)","Shaharadagi badaviy (2011)",'
        '"Halal polisi (2011)","Les Seigneurs (2012)","Intouchables (2011)"]}'
    )
    parsed = _parse_gemini_movie_json(raw)
    assert parsed and parsed.get("uncertain") is True
    assert len(parsed["candidates"]) >= 4

    result = uncertain_movie_result(parsed["candidates"])
    assert result["ok"] and result["uncertain"]
    assert not result["title"]
    assert 2 <= len(result["candidates"]) <= 6


def test_link_found_uncertain_i18n():
    from app.i18n import t
    from app.link_title import format_candidates_list

    listing = format_candidates_list(
        ["Orzular jamoasi (2012)", "Shaharadagi badaviy (2011)"]
    )
    msg = t("uz", "link_found_uncertain", list=listing)
    assert "Kechirasiz" in msg
    assert "1) Orzular jamoasi" in msg
    assert "2) Shaharadagi" in msg


def test_titles_same_movie_billu_local():
    from app.link_title import titles_same_movie

    assert titles_same_movie("Billu (2009)", "Sartarosh Billu (2009)")
    assert titles_same_movie("Billu Barber (2009)", "Sartarosh Billu (2009)")
