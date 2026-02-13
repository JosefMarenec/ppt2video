from fastapi import APIRouter, UploadFile
import uuid
import os
from workers.extractor import extract_slides
from workers.script_gen import generate_script
from workers.renderer import render_video
from workers.stitcher import stitch_videos

router = APIRouter()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_ppt(file: UploadFile):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    ppt_path = os.path.join(job_dir, "input.pptx")

    # Save uploaded PPT
    with open(ppt_path, "wb") as f:
        f.write(await file.read())

    # Step 1: Extract slides
    slides = extract_slides(ppt_path)

    slide_videos = []

    # Step 2: Process each slide
    for slide in slides:
        slide_number = slide["slide_number"]
        slide_text = slide["text"]

        # Generate script
        script = generate_script(slide_text)

        # Create dummy audio file
        audio_path = os.path.join(job_dir, f"slide_{slide_number}.mp3")
        with open(audio_path, "wb") as f:
            f.write(b"\x00\x00")  # placeholder audio

        # Create dummy image (simple black frame)
        image_path = os.path.join(job_dir, f"slide_{slide_number}.png")
        os.system(f"ffmpeg -f lavfi -i color=c=black:s=1280x720:d=3 -frames:v 1 {image_path}")

        # Render video
        video_path = os.path.join(job_dir, f"slide_{slide_number}.mp4")
        render_video(image_path, audio_path, video_path)

        slide_videos.append(video_path)

    # Step 3: Stitch slides
    final_video_path = os.path.join(job_dir, "final.mp4")
    stitch_videos(slide_videos, final_video_path)

    return {
        "job_id": job_id,
        "video_path": final_video_path
    }
