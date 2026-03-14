import subprocess

def speech(text: str):
    """
    Converts the provided text into spoken audio using the Piper text-to-speech engine.
    """
    if not text.strip():
        return "Error: Empty text provided for speech synthesis."

    # The piper command expects the text on stdin.
    command = '/home/hermann/piper/piper/piper -q --model /home/hermann/piper/miro_pt-BR.onnx --length_scale 1.2 --output-raw | aplay -r 22050 -f S16_LE -t raw 2>/dev/null'

    try:
        # Use subprocess.run with input to pass the text to piper's stdin
        process = subprocess.run(
            command,
            input=text.encode('utf-8'), # Encode text to bytes for stdin
            shell=True,
            capture_output=True, # Capture stdout and stderr
            check=True # Raise CalledProcessError for non-zero exit codes
        )
        return "Speech synthesis and playback completed successfully."
    except subprocess.CalledProcessError as e:
        error_msg = f"Error executing speech command: {e.stderr.decode('utf-8') if e.stderr else str(e)}"
        print(error_msg) # Still log for the user/debugging
        return f"Failed to perform speech synthesis: {error_msg}"
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        print(error_msg)
        return f"Failed to perform speech synthesis: {error_msg}"

