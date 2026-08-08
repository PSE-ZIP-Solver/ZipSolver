import importlib
import sys

packages_to_check = [
    "pickle",       # stdlib
    "random",       # stdlib
    "pathlib",      # stdlib
    "gymnasium",
    "stable_baselines3",
    "backend.puzzle_logic",
    "backend.rl_components",
    "offline_training.board_generator",
    "offline_training.training_result",
]

print(f"Python: {sys.version}\n")

for pkg in packages_to_check:
    try:
        module = importlib.import_module(pkg)
        version = getattr(module, "__version__", "n/a (kein __version__ Attribut)")
        print(f"✅ {pkg:<40} version={version}")
    except ImportError as e:
        print(f"❌ {pkg:<40} FEHLT: {e}")