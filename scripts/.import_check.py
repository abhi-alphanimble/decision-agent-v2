import importlib, traceback
modules=[
    "app",
    "app.main",
    "app.handlers.decision_handlers",
    "app.crud",
    "app.slack_client",
    "app.ai.ai_client",
    "app.logging_config",
    "database.base",
]
for m in modules:
    try:
        importlib.invalidate_caches()
        importlib.import_module(m)
        print(f"OK: Imported {m}")
    except Exception as e:
        print(f"ERR: Importing {m} -> {e}")
        traceback.print_exc()
        break
