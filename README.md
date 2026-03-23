# PPT to Video Service

A backend pipeline service that automates the conversion of PowerPoint presentations (`.pptx`) into full videos. It extracts slide content, generates voiceover scripts, creates Text-to-Speech (TTS) audio, and renders each slide individually before stitching them all together into a final output video.

## Architecture

The project is built around a FastAPI entry point with several worker scripts executing the pipeline steps.

### Components
- **API (`api/`)**: Built using FastAPI. Manages file uploads, initiates the video creation job, and interacts with pipeline workers.
- **Workers (`workers/`)**: Contains the modules carrying out the core pipeline tasks.
   - `extractor.py`: Extracts text and metadata from uploaded PowerPoint slides.
   - `script_gen.py`: Generates a spoken narrative script based on slide text.
   - `tts.py`: Simulates Text-To-Speech (TTS) generation (creates audio elements).
   - `renderer.py`: Uses `moviepy`/`ffmpeg` to turn slide frames and audio into individual MP4 files.
   - `stitcher.py`: Combines the rendered slides into a single, seamless video.
   - `consumer.py`: A placeholder for an async queue consumer (e.g., Kafka) to process tasks in the background.
- **Infrastructure (`infra/`)**: Contains Dockerfile and configurations.
- **Root**: `docker-compose.yml` orchestrates the services.

## Prerequisites

- Python 3.9+
- [Docker](https://docs.docker.com/get-docker/) & [Docker Compose](https://docs.docker.com/compose/install/)
- ffmpeg installed on your host system (if running outside Docker)

## Installation & Setup

### Running with Docker (Recommended)

To start the API server and worker services via Docker Compose:

```bash
docker-compose up --build
```

The API will be available at `http://localhost:8000`.

### Running locally

1. Create a virtual environment and activate it:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```bash
   uvicorn api.main:app --reload
   ```

## Usage

### 1. Check API Health
```bash
curl http://localhost:8000/health
```

### 2. Upload and Convert a PPTX
Send a `POST` request to the `/upload` endpoint with your PowerPoint presentation.

```bash
curl -X POST -F "file=@/path/to/your/presentation.pptx" http://localhost:8000/upload
```

The API will return a `job_id` and the designated path for the generated `final.mp4` video. By default, completed files will output to the local `storage/` directory, mapped under your current `job_id`.

## Future Enhancements
- Hooking up the `aiokafka` consumer logic to stream jobs efficiently.
- Adding PostgreSQL (via `sqlalchemy`/`psycopg2`) for tracking queued and completed jobs.
- Visualizing observability metrics with Prometheus and OpenTelemetry.
