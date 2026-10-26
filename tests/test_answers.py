from pathlib import Path

def test_save_answer_creates_markdown(tmp_path, monkeypatch):
    from reflectai.storage import answers
    monkeypatch.setattr(answers, "ANSWERS_DIR", tmp_path)
    path = answers.save_answer("Test prompt", "Final response", {
        "generation_model": "test-gen", "reflection_model": "test-ref", "rounds": 2,
        "duration_seconds": 1.25,
    })
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "Test prompt" in content
    assert "Final response" in content
    assert "test-gen" in content
