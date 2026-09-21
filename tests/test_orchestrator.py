from syscohada_pipeline.core import orchestrator


def test_document_checkpoint_resume(tmp_path, monkeypatch):
    pdf_path = str(tmp_path / "sample.pdf")
    output_dir = str(tmp_path / "output")
    checkpoint_dir = str(tmp_path / "checkpoints")
    monkeypatch.setattr(orchestrator, "convert_pdf_to_images", lambda *args, **kwargs: ["page.jpg"])
    monkeypatch.setattr(
        "syscohada_pipeline.extractors.heuristic_engine.init_heuristic_engine",
        lambda device: None,
    )

    def process_pages(pages):
        assert pages[0]["type"] == "unknown"
        return {"bilan": {}, "cr": {}, "tft": {}, "notes": [], "esdgi": []}

    config = {"checkpoint_dir": checkpoint_dir, "device": "cpu"}
    first = orchestrator._process_single_pdf(pdf_path, output_dir, process_pages, config)
    assert first["source_file"] == "sample.pdf"

    def should_not_run(_pages):
        raise AssertionError("checkpoint non utilisé")

    second = orchestrator._process_single_pdf(pdf_path, output_dir, should_not_run, config)
    assert second == first
