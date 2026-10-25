from reflectai.observability.usage import record_usage, usage_summary, reset_usage

def test_usage_counters():
    reset_usage()
    record_usage("ollama")
    record_usage("ollama", "error")
    assert usage_summary() == {"ollama:success": 1, "ollama:error": 1}
    reset_usage()
    assert usage_summary() == {}
