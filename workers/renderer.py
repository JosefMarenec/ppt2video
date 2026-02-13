import subprocess

def render_video(image_path, audio_path, output_path):
    cmd = [
        "ffmpeg",
        "-loop", "1",
        "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]
    subprocess.run(cmd)
