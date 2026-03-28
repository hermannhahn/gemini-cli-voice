import contextlib
import os
import platform
import shutil
import subprocess
import tempfile
from pathlib import Path

from gemini_voice.paths import BIN_DIR, get_bin_path


def run_speech_task(
    piper_exe: str,
    model_file: str,
    length_scale: float,
    text: str,
) -> str | None:
    """Executa o processo de sintetização e reprodução de áudio."""
    system = platform.system().lower()

    # Prepara o ambiente para carregar bibliotecas locais
    env = os.environ.copy()
    if system == "linux":
        linux_bin_dir = BIN_DIR / "linux"
        env["LD_LIBRARY_PATH"] = f"{linux_bin_dir}:{env.get('LD_LIBRARY_PATH', '')}"

    # Cria arquivo temporário para o WAV
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tf:
        temp_wav = Path(tf.name)

    try:
        # 1. Piper gera o WAV
        piper_cmd = [
            piper_exe,
            "-q",
            "--model",
            model_file,
            "--length_scale",
            str(length_scale),
            "--output_file",
            str(temp_wav),
        ]
        with subprocess.Popen(
            piper_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        ) as p:
            p.communicate(input=text.encode("utf-8"))

        if system == "linux":
            aplay_exe = get_bin_path("aplay")
            if not aplay_exe:
                aplay_exe = shutil.which("aplay")

            if aplay_exe:
                # 2. Toca o WAV de forma síncrona
                subprocess.run(
                    [aplay_exe, str(temp_wav)],
                    check=False,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

        elif system == "windows":
            # 2. PowerShell toca o WAV de forma síncrona
            ps_cmd = f"powershell -c \"(New-Object Media.SoundPlayer '{temp_wav}').PlaySync()\""
            subprocess.run(
                ps_cmd,
                shell=True,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

        return None
    except (subprocess.SubprocessError, OSError) as e:
        return str(e)
    finally:
        # 3. Limpa o arquivo temporário
        if temp_wav.exists():
            with contextlib.suppress(OSError):
                temp_wav.unlink()
