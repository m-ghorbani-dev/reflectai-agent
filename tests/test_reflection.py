from reflectai.reflection.engine import ReflectionResult

def test_reflection_result_shape():
    result = ReflectionResult(answer="hello", rounds=1, review="APPROVED")
    assert result.answer == "hello"
    assert result.rounds == 1
