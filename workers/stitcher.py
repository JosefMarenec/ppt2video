import subprocess

def stitch_videos(video_list, output_path):
    with open("videos.txt", "w") as f:
        for video in video_list:
            f.write(f"file '{video}'\n")

    subprocess.run([
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", "videos.txt",
        "-c", "copy",
        output_path
    ])
