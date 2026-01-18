"""
Dream LIVIN Shop - AI-driven modular mobile home vision generator.
Helps users discover and refine their dream home design for Earth and Mars.
"""
import os
import asyncio
import json
import uuid
import base64
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from services.ai_client import AIClient
from services.prompt_engine import PromptEngine

load_dotenv()

app = FastAPI(title="Dream LIVIN Shop", version="1.0.0")

# Directory Setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
IMAGE_DIR = os.path.join(OUTPUT_DIR, "images")
STATIC_DIR = os.path.join(BASE_DIR, "static")
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Shared instances
ai_client = AIClient()
prompt_engine = PromptEngine()

# In-memory storage for generation status
active_tasks = {}

# Constants
MAX_IMAGE_COUNT = int(os.getenv("MAX_IMAGE_COUNT", "1000"))


# Request/Response Models
class FeedbackRequest(BaseModel):
    feedback: str
    state: dict  # LIVIN DNA state from frontend
    earth_location: Optional[str] = None
    mars_location: Optional[str] = None


class DNAUpdateRequest(BaseModel):
    state: dict
    updated_dna: List[str]  # User-modified DNA keywords


# --- Helper Functions ---

async def retry_with_backoff(func, *args, max_retries=3, initial_delay=2, **kwargs):
    """Retries an async function with exponential backoff on 503 errors."""
    delay = initial_delay
    for i in range(max_retries):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            err_str = str(e).lower()
            if "503" in err_str or "overloaded" in err_str or "unavailable" in err_str:
                if i == max_retries - 1:
                    raise e
                print(f"Model overloaded, retrying in {delay}s... (Attempt {i+1}/{max_retries})")
                await asyncio.sleep(delay)
                delay *= 2
            else:
                raise e


async def cleanup_images():
    """Removes oldest images if count exceeds MAX_IMAGE_COUNT."""
    files = [os.path.join(IMAGE_DIR, f) for f in os.listdir(IMAGE_DIR) 
             if os.path.isfile(os.path.join(IMAGE_DIR, f))]
    if len(files) <= MAX_IMAGE_COUNT:
        return
    
    files.sort(key=os.path.getctime)
    num_to_delete = len(files) - MAX_IMAGE_COUNT
    for i in range(num_to_delete):
        try:
            os.remove(files[i])
        except Exception as e:
            print(f"Error deleting {files[i]}: {e}")


def encode_image_to_base64(image_data: bytes) -> str:
    """Encode image bytes to base64 string."""
    return base64.b64encode(image_data).decode('utf-8')


async def generate_images_task(
    task_id: str, 
    feedback: str, 
    state: dict,
    uploaded_images: List[str] = None,  # Base64 encoded images
    earth_location: str = None,
    mars_location: str = None
):
    """Background task for generating LIVIN images."""
    active_tasks[task_id]["status"] = "Analyzing your vision..."
    
    try:
        # 1. Build planning prompt
        images_desc = None
        if uploaded_images:
            images_desc = f"{len(uploaded_images)} reference/sketch images provided by user"
        
        planning_prompt = prompt_engine.build_planning_prompt(
            feedback=feedback,
            state=state,
            user_images_description=images_desc
        )
        
        # 2. Call AI to generate plan
        active_tasks[task_id]["status"] = "Evolving your LIVIN DNA..."
        plan_data = await retry_with_backoff(
            ai_client.generate_plan,
            prompt=planning_prompt,
            state=state,
            images=uploaded_images
        )
        
        active_tasks[task_id]["status"] = "Generating Earth & Mars visions..."
        active_tasks[task_id]["updated_state"] = plan_data["updated_state"]
        active_tasks[task_id]["round"] = plan_data["updated_state"].get("round", 1)
        
        # 3. Get LIVIN DNA for image prompts
        livin_dna = plan_data["updated_state"].get("livin_dna", [])
        current_round = plan_data["updated_state"].get("round", 1)
        
        # 4. Generate images in parallel
        async def generate_single_image(index: int, item: dict):
            # Build full image prompt
            full_prompt = prompt_engine.build_image_prompt(
                design_prompt=item["prompt"],
                environment=item["environment"],
                view=item.get("view", "exterior"),
                round_num=current_round,
                livin_dna=livin_dna,
                location_description=earth_location if item["environment"] == "earth" else mars_location
            )
            
            # Generate image with retry
            image_data = await retry_with_backoff(
                ai_client.generate_image,
                prompt=full_prompt,
                size="1536x1024"
            )
            
            if image_data is None:
                print(f"Warning: Image generation failed for {item['name']}")
                return None
            
            # Save image
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{task_id}_{index}_{timestamp}.png"
            filepath = os.path.join(IMAGE_DIR, filename)
            with open(filepath, "wb") as f:
                f.write(image_data)
            
            return {
                "name": item["name"],
                "url": f"/api/images/{filename}",
                "prompt": item["prompt"],
                "type": item["type"],
                "environment": item["environment"],
                "view": item.get("view", "exterior")
            }
        
        # Generate all 6 images concurrently
        tasks = [generate_single_image(i, item) for i, item in enumerate(plan_data["plan"])]
        results = await asyncio.gather(*tasks)
        
        # Separate into Earth and Mars groups
        earth_images = [r for r in results if r and r["environment"] == "earth"]
        mars_images = [r for r in results if r and r["environment"] == "mars"]
        
        active_tasks[task_id]["earth_images"] = earth_images
        active_tasks[task_id]["mars_images"] = mars_images
        active_tasks[task_id]["status"] = "completed"
        
        await cleanup_images()
        
    except Exception as e:
        print(f"Error in generation task: {e}")
        active_tasks[task_id]["status"] = "failed"
        active_tasks[task_id]["error"] = str(e)


# --- API Endpoints ---

@app.post("/api/feedback")
async def handle_feedback(
    background_tasks: BackgroundTasks,
    feedback: str = Form(...),
    state: str = Form(...),  # JSON string
    earth_location: Optional[str] = Form(None),
    mars_location: Optional[str] = Form(None),
    reference_images: List[UploadFile] = File(default=[]),
    environment_image: Optional[UploadFile] = File(None),
    sketch_image: Optional[UploadFile] = File(None)
):
    """
    Handle user feedback and uploaded images.
    Triggers background generation of Earth and Mars visions.
    """
    # Parse state JSON
    try:
        state_dict = json.loads(state)
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid state JSON")
    
    # Process uploaded images
    uploaded_images = []
    
    for ref_img in reference_images:
        img_data = await ref_img.read()
        uploaded_images.append(encode_image_to_base64(img_data))
    
    if environment_image:
        img_data = await environment_image.read()
        uploaded_images.append(encode_image_to_base64(img_data))
    
    if sketch_image:
        img_data = await sketch_image.read()
        uploaded_images.append(encode_image_to_base64(img_data))
    
    # Create task
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {
        "id": task_id,
        "round": state_dict.get("round", 0),
        "status": "Initializing...",
        "earth_images": [],
        "mars_images": [],
        "updated_state": state_dict
    }
    
    # Start background task
    background_tasks.add_task(
        generate_images_task,
        task_id,
        feedback,
        state_dict,
        uploaded_images if uploaded_images else None,
        earth_location,
        mars_location
    )
    
    return {"task_id": task_id}


@app.post("/api/feedback/simple")
async def handle_simple_feedback(req: FeedbackRequest, background_tasks: BackgroundTasks):
    """
    Simple feedback endpoint without file uploads.
    For text/voice only input.
    """
    task_id = str(uuid.uuid4())
    active_tasks[task_id] = {
        "id": task_id,
        "round": req.state.get("round", 0),
        "status": "Initializing...",
        "earth_images": [],
        "mars_images": [],
        "updated_state": req.state
    }
    
    background_tasks.add_task(
        generate_images_task,
        task_id,
        req.feedback,
        req.state,
        None,
        req.earth_location,
        req.mars_location
    )
    
    return {"task_id": task_id}


@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Get the status of a generation task."""
    if task_id not in active_tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return active_tasks[task_id]


@app.get("/api/images/{filename}")
async def get_image(filename: str):
    """Serve generated images."""
    filepath = os.path.join(IMAGE_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Image not found")
    return FileResponse(filepath)


@app.post("/api/transcribe")
async def transcribe_audio(audio_file: UploadFile = File(...)):
    """Transcribe audio using AI Builder Space API."""
    try:
        audio_data = await audio_file.read()
        result = await ai_client.transcribe_audio(audio_data)
        
        return {
            "text": result.get("text", ""),
            "language": result.get("detected_language"),
            "confidence": result.get("confidence")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")


@app.post("/api/dna/update")
async def update_dna(req: DNAUpdateRequest):
    """
    Update LIVIN DNA based on user's manual edits.
    Allows users to select/unselect/modify DNA keywords.
    """
    updated_state = req.state.copy()
    updated_state["livin_dna"] = req.updated_dna[:8]  # Ensure max 8 keywords
    return {"updated_state": updated_state}


# Serve Frontend (Must be after API routes)
if os.path.exists(STATIC_DIR) and os.listdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="frontend")


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up AI client on shutdown."""
    await ai_client.close()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8003"))
    uvicorn.run(app, host="0.0.0.0", port=port)
