from importlib.util import find_spec
missing = [name for name in ("fastapi", "uvicorn") if find_spec(name) is None]
print("Missing Python packages: " + ", ".join(missing) if missing else "Python API prerequisites: OK")
print("Node/npm are required for the optional React workbench UI.")
