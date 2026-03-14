from pathlib import Path
import subprocess
import sys


def main():
    project_dir = Path(__file__).parent
    app_file = project_dir / "app/ui/streamlit_app.py"
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_file),
        "--server.headless=false",
        "--browser.gatherUsageStats=false",
    ]

    subprocess.run(cmd, cwd=project_dir, check=True)


if __name__ == "__main__":
    main()