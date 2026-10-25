# Resource management

ReflectAI does not start background model-generation loops. However, Streamlit's server process remains alive after a browser tab is closed, and Ollama may keep models loaded in RAM/VRAM for reuse.

## Recommended local launch

Activate the Conda environment, then run:

```bash
./run_reflectai.sh
```

When you finish, press `Ctrl+C` in that terminal. The launcher exits Streamlit and asks Ollama to unload models that are currently loaded. The Ollama service itself remains running.

You can also open **مدیریت منابع Ollama** in the Chat page and select **آزادسازی حافظهٔ مدل‌های Ollama** to unload loaded models while keeping the app/service running.

**Important:** closing only the browser tab does not reliably notify a Streamlit server that the user has left. For reliable cleanup, stop the app from its terminal with `Ctrl+C` or use the in-app unload button. The app cannot safely kill the shared Ollama service automatically because other applications may be using it.
