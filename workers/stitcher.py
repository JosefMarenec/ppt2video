import subprocess
import os

def stitch_videos(video_list, output_path):
    job_dir = os.path.dirname(output_path)
    txt_path = os.path.join(job_dir, "videos.txt")

    with open(txt_path, "w") as f:
        for video in video_list:
            f.write(f"file '{os.path.basename(video)}'\n")

    subprocess.run([
        "ffmpeg",
        "-y",
        "-nostdin",
        "-f", "concat",
        "-safe", "0",
        "-i", txt_path,
        "-c", "copy",
        output_path
    ])
