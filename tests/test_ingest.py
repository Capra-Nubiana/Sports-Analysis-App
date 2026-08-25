"""
Test data ingestion parsers (fitdecode error handling)
"""

from src.ingest.wearable.fit_parser import FITParser


def test_fit_parser_invalid_file():
    p = FITParser(fit_filepath="does_not_exist.fit")
    assert not p.open()


def test_fit_parser_iter_not_open():
    p = FITParser(fit_filepath="does_not_exist.fit")
    try:
        next(p.iter_frames())
        assert False
    except RuntimeError:
        assert True
