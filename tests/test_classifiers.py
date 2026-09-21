import os
import pytest
from syscohada_pipeline.core.config import get_base_config
from syscohada_pipeline.core.page_classifier import classify_page
from syscohada_pipeline.core.checkpoint_manager import (
    save_checkpoint, 
    load_checkpoint,
    _get_checkpoint_path
)

def test_base_config():
    config = get_base_config()
    assert "device" in config
    assert config["device"] in ["cuda", "cpu"]
    assert "checkpoint_dir" in config
    assert "log_level" in config

def test_checkpoint_lifecycle(tmp_path):
    doc_id = "test_doc_001"
    checkpoint_dir = str(tmp_path / "checkpoints")
    state = {"page": 2, "status": "processing"}
    
    # Test Save
    success = save_checkpoint(doc_id, state, checkpoint_dir)
    assert success is True
    
    # Verify file exists
    filepath = _get_checkpoint_path(doc_id, checkpoint_dir)
    assert filepath.exists()
    
    # Test Load
    loaded_state = load_checkpoint(doc_id, checkpoint_dir)
    assert loaded_state == state

def test_load_nonexistent_checkpoint(tmp_path):
    checkpoint_dir = str(tmp_path / "checkpoints")
    result = load_checkpoint("fake_doc", checkpoint_dir)
    assert result is None

def test_load_corrupted_checkpoint(tmp_path):
    doc_id = "bad_doc"
    checkpoint_dir = str(tmp_path / "checkpoints")
    
    # Create corrupted file
    os.makedirs(checkpoint_dir, exist_ok=True)
    filepath = _get_checkpoint_path(doc_id, checkpoint_dir)
    with open(filepath, 'w') as f:
        f.write("{bad_json: true")
        
    result = load_checkpoint(doc_id, checkpoint_dir)
    assert result is None

def test_classifier_handles_accents():
    assert classify_page([{"text": "tableau des flux de trésorerie"}]) == "tft"
