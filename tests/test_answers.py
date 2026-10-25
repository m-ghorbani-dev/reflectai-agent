from pathlib import Path

from reflectai.storage import answers


def test_save_final_answer_creates_markdown_with_prompt_and_answer(tmp_path, monkeypatch):
    monkeypatch.setattr(answers, "ROOT_DIR", tmp_path)
    path = answers.save_final_answer(
        "Explain context length",
        "Context length controls the token window.",
        {"generation_model": "llama3.2", "rounds": 1},
    )
    assert path.is_file()
    assert path.suffix == ".md"
    content = path.read_text(encoding="utf-8")
    assert "Explain context length" in content
    assert "Context length controls the token window." in content
    assert "llama3.2" in content
