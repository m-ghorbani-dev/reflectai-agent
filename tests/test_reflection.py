from unittest.mock import patch
import pytest
from reflectai.reflection.engine import ReflectionResult, run_reflection

def test_reflection_result_shape():
    result = ReflectionResult(answer="hello", rounds=1, review="APPROVED")
    assert result.answer == "hello"
    assert result.rounds == 1

def test_zero_rounds_only_generates():
    with patch("reflectai.reflection.engine.generate", return_value="answer") as generate:
        result = run_reflection("question", "ollama", "m", "ollama", "m", 0)
    assert result.answer == "answer"
    assert result.rounds == 0
    assert generate.call_count == 1

def test_empty_prompt_rejected():
    with pytest.raises(ValueError):
        run_reflection("  ", "ollama", "m", "ollama", "m")

def test_round_limit_is_bounded():
    with patch("reflectai.reflection.engine.generate", return_value="answer"):
        with pytest.raises(ValueError):
            run_reflection("q", "ollama", "m", "ollama", "m", 6)

def test_approved_review_stops_loop():
    with patch("reflectai.reflection.engine.generate", return_value="answer") as generate, \
         patch("reflectai.reflection.engine.evaluate_draft") as evaluate:
        evaluate.return_value.approved = True
        evaluate.return_value.feedback = "APPROVED: good"
        result = run_reflection("q", "ollama", "m", "ollama", "m", 3)
    assert result.rounds == 1
    assert result.review == "APPROVED: good"
    assert generate.call_count == 1

def test_unapproved_review_triggers_revision():
    with patch("reflectai.reflection.engine.generate", side_effect=["draft", "revised"]) as generate, \
         patch("reflectai.reflection.engine.evaluate_draft") as evaluate, \
         patch("reflectai.reflection.engine.revise_draft", return_value="revised") as revise:
        evaluate.return_value.approved = False
        evaluate.return_value.feedback = "Add an example."
        result = run_reflection("q", "ollama", "m", "ollama", "m", 1)
    assert result.answer == "revised"
    assert result.rounds == 1
    revise.assert_called_once()
