# Development

Install with `python -m pip install -e '.[dev]'`, then run tests with `python -m pytest -v`.

Useful checks:

```bash
python -m compileall -q src tests streamlit_app.py
python -m pytest -v
python -m reflectai --check-config
```

Keep provider calls mocked in unit tests so the suite does not need a live model server or credentials. Add tests for security-sensitive behavior whenever SQL or provider logic changes.
