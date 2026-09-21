import pytest
from syscohada_pipeline.core.page_classifier import classify_page
from syscohada_pipeline.groups.group_c import vote_majority

def test_page_classifier():
    assert classify_page([{"text": "bilan actif"}]) == "bilan"
    assert classify_page([{"text": "compte de resultat"}]) == "cr"
    assert classify_page([{"text": "flux de tresorerie"}]) == "tft"
    assert classify_page([{"text": "notes annexes"}]) == "notes"
    assert classify_page([{"text": "etat supplementaire"}]) == "esdgi"
    assert classify_page([{"text": "random text"}]) == "unknown"

def test_group_c_vote():
    assert vote_majority([]) == {"value": None, "confidence": "aucune donnée"}
    assert vote_majority([100, 100, 101]) == {"value": 100, "confidence": "majorité"}
    assert vote_majority([100, 101])["confidence"] == "conflit"
