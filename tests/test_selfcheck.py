"""Testes de execução para o script de autoavaliação (selfcheck.py)."""

import subprocess
import sys
from pathlib import Path


def test_selfcheck_execution():
    repo_root = Path(__file__).resolve().parent.parent
    script = repo_root / "scripts" / "selfcheck.py"
    assert script.exists(), "O script scripts/selfcheck.py deve existir"

    # Após as correções, as duas trilhas práticas devem passar na autoavaliação.
    res_n2 = subprocess.run(
        [sys.executable, str(script), "--nivel", "2"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert res_n2.returncode == 0, res_n2.stdout
    assert "F1" in res_n2.stdout
    assert "SUCESSO" in res_n2.stdout

    res_n3 = subprocess.run(
        [sys.executable, str(script), "--nivel", "3"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    assert res_n3.returncode == 0, res_n3.stdout
    assert "F3" in res_n3.stdout
    assert "F7" in res_n3.stdout
    assert "SUCESSO" in res_n3.stdout


if __name__ == "__main__":
    test_selfcheck_execution()
    print("ALL TESTS PASSED")
