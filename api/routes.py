from fastapi import APIRouter, UploadFile, BackgroundTasks
import uuid
import os
from PIL import Image, ImageDraw, ImageFont
import subprocess

from workers.extractor import extract_slides
from workers.script_gen import generate_script
from workers.renderer import render_video
from workers.stitcher import stitch_videos
from workers.tts import generate_audio

router = APIRouter()

UPLOAD_DIR = "storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def process_job_pipeline(job_id: str, job_dir: str, ppt_path: str):
    try:
        print(f"[{job_id}] Starting pipeline...")
        # Step 1: Extract slides
        slides = extract_slides(ppt_path)

        slide_videos = []

        # Step 2: Process each slide
        for slide in slides:
            slide_number = slide["slide_number"]
            slide_text = slide["text"]

            # Generate script
            script = generate_script(slide_text)

            # Create audio file using TTS
            audio_path = os.path.join(job_dir, f"slide_{slide_number}.mp3")
            generate_audio(script, audio_path)

            # Create image using Pillow
            image_path = os.path.join(job_dir, f"slide_{slide_number}.png")
            
            # Simple 1280x720 blue background
            img = Image.new('RGB', (1280, 720), color=(10, 30, 80))
            draw = ImageDraw.Draw(img)
            
            # We don't have a specific font loaded, so we use default font, 
            # but scale the drawing by rendering text block
            import textwrap
            wrapped_text = "\\n".join(textwrap.wrap(slide_text, width=60))
            if not wrapped_text:
                wrapped_text = f"Slide {slide_number}"
                
            draw.text((100, 300), wrapped_text, fill=(255, 255, 255), align="center")
            img.save(image_path)

            # Render video
            video_path = os.path.join(job_dir, f"slide_{slide_number}.mp4")
            render_video(image_path, audio_path, video_path)

            slide_videos.append(video_path)

        # Step 3: Stitch slides
        final_video_path = os.path.join(job_dir, "final.mp4")
        stitch_videos(slide_videos, final_video_path)
        print(f"[{job_id}] Pipeline complete! Video saved to {final_video_path}")
        
    except Exception as e:
        print(f"[{job_id}] Pipeline failed: {str(e)}")


@router.post("/upload")
async def upload_ppt(file: UploadFile, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    job_dir = os.path.join(UPLOAD_DIR, job_id)
    os.makedirs(job_dir, exist_ok=True)

    ppt_path = os.path.join(job_dir, "input.pptx")

    # Save uploaded PPT
    with open(ppt_path, "wb") as f:
        f.write(await file.read())

    # Send work to background task
    background_tasks.add_task(process_job_pipeline, job_id, job_dir, ppt_path)

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Video creation started in the background"
    }
