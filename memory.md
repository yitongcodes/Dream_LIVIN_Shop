# Dream LIVIN Shop - Project Memory

## Project Overview

**Name**: Dream LIVIN Shop  
**Folder**: `Dream_LIVIN_Shop`  
**Purpose**: AI-driven modular mobile home vision generator for Earth and Mars  
**Status**: MVP Completed ✅  
**Running at**: http://localhost:8003

---

## User Requirements Summary

### Core Concept
A tool that allows users to visualize their dream **affordable, flexible, aesthetic modular mobile home** for both Earth and Mars through multi-modal input and iterative refinement.

### Input Methods (User Specified)
1. **Text description** - Dream home vision
2. **Voice input** - Speech-to-text transcription
3. **Reference images** - Dream home style references
4. **Environment images** - Original space to transform
5. **Sketch images** - Simple layout drawings (upload only, no built-in drawing tool)
6. **Location selection** - Earth and Mars map positioning (deferred to later phase)

### Image Generation Strategy (User Specified)
**Per Round: 6 images total**

| Group | Exploitation | Exploration | Focus |
|-------|-------------|-------------|-------|
| Earth | 2 | 1 | Realistic, grounded |
| Mars | 1 | 2 | Bold, futuristic |

### Visual Style Evolution (User Specified)
- **Rounds 1-2**: Hand-drawn architectural sketches, sci-fi novel illustrations (70% sketch / 30% render)
- **Rounds 3+**: Cinematic scene renders with human figures (30% sketch / 70% render)

### LIVIN DNA System (User Specified)
- AI extracts keywords automatically
- **Maximum 8 keywords**
- Users can **select/unselect/replace** keywords in frontend
- DNA maintains continuity across rounds
- Subsequent prompts include DNA + user history
- Keywords represent: spatial preferences, materials, colors, functions, aesthetics, emotions

### Earth vs Mars Differentiation (User Specified)
| Aspect | Earth | Mars |
|--------|-------|------|
| Overall | Realistic, practical | Bold, futuristic |
| Outdoor | Natural landscapes | Wild, alien terrain (inspired by interstellar games/novels) |
| Indoor | Sustainable, harmonious | Cozy, simple, design-focused (earth-like comfort) |
| Style | Grounded | The Expanse, Dune, No Man's Sky, Starfield inspired |

---

## Work Completed ✅

### 1. Project Structure
- Created `Dream_LIVIN_Shop` folder at same level as `CarFinder-master`
- Set up directory structure: services, frontend, outputs, static, scripts

### 2. Backend Implementation

**`services/ai_client.py`**
- AI Builder Space API integration
- Multimodal support (text + images)
- Image generation with Gemini 2.5 Flash
- Audio transcription API
- Exponential backoff retry logic

**`services/prompt_engine.py`**
- Planning prompt builder for LIVIN DNA Manager
- Earth/Mars dual-environment prompts
- Style evolution logic (early vs mature rounds)
- Base templates for Earth, Mars outdoor, Mars indoor

**`main.py`**
- FastAPI application with endpoints:
  - `POST /api/feedback` - Multimodal input with file uploads
  - `POST /api/feedback/simple` - Text-only input
  - `GET /api/status/{task_id}` - Generation status polling
  - `GET /api/images/{filename}` - Image serving
  - `POST /api/transcribe` - Audio transcription
  - `POST /api/dna/update` - Manual DNA editing
- Background task processing
- Image cleanup (FIFO, max count limit)

### 3. Frontend Implementation

**`frontend/src/App.jsx`**
- Dual-panel layout (Earth group + Mars group)
- LIVIN DNA panel with edit functionality
- History panel for round archives
- Multi-file upload (reference, environment, sketch)
- Voice recording with waveform visualization
- Status overlay during generation
- LocalStorage persistence

**`frontend/src/App.css` & `index.css`**
- Dark theme with Earth (green) and Mars (orange/red) accents
- Responsive grid layout
- DNA keyword tags with edit mode
- Image cards with type badges (exploitation/exploration)
- Upload preview thumbnails
- Animated loader and status indicators

### 4. Configuration
- `.env` with AI_BUILDER_TOKEN
- `requirements.txt` for Python dependencies
- `package.json` for frontend dependencies
- `scripts/build-frontend.sh` for production build

### 5. Testing
- Frontend built successfully
- Backend running on port 8003
- API endpoints verified via OpenAPI

---

## Work Deferred / Future Enhancements 📋

### High Priority

1. **Map Integration**
   - Earth: Leaflet.js + OpenStreetMap
   - Mars: NASA Mars Trek tiles
   - Allow users to drag and locate their living area
   - Pass location context to prompts

2. **Image-to-Image Generation**
   - Use uploaded environment/sketch images as generation input
   - Reference image style transfer

### Medium Priority

3. **Enhanced DNA Interaction**
   - Drag-and-drop keyword reordering
   - Keyword category grouping (spatial, material, color, etc.)
   - DNA comparison across rounds

4. **Image Selection Feedback**
   - Click to favorite/reject specific images
   - Feed selection back into DNA refinement

5. **Character Integration**
   - Toggle to include/exclude human figures
   - Character style preferences

### Low Priority / Nice-to-Have

6. **Export Features**
   - Download generated images
   - Export DNA profile
   - Share vision boards

7. **Advanced Prompts**
   - Custom prompt templates
   - Style presets (minimalist, industrial, organic, etc.)
   - Time-of-day lighting options

8. **3D Visualization**
   - Basic 3D model generation
   - VR preview mode

---

## Technical Notes

### API Token
Using AI Builder Space: `AI_BUILDER_TOKEN` in `.env`

### Models Used
- **Planning**: `gemini-3-flash-preview` (Thinking Mode HIGH)
- **Image Generation**: `gemini-2.5-flash-image` (1536x1024, 16:9)
- **Transcription**: AI Builder Space audio API

### Port Configuration
- Dream LIVIN Shop: **8003**
- CarFinder (reference): 8002

### Key Prompt Templates

**Earth Base**:
```
A {style} of an affordable, flexible, aesthetic modular mobile home on Earth.
Location context: {location}
Environment: Realistic Earth setting with natural lighting, sustainable integration.
Architecture: Modular, mobile, adaptable design balancing affordability with beauty.
```

**Mars Outdoor**:
```
Wild Martian landscape - rust-red terrain, dramatic rock formations, pink-orange sky.
Architecture: Bold futuristic design inspired by interstellar exploration games.
Style: The Expanse, Dune, No Man's Sky, Starfield.
```

**Mars Indoor**:
```
Cozy, earth-like living space for human comfort.
Warm lighting, natural materials, minimal elegant furniture.
Safe haven, warmth within the wild.
```

---

## Commands Reference

### Start the project
```bash
cd "/Users/heyitong/Documents YD/GitHub/Personal/Dream_LIVIN_Shop"
python3 main.py
```

### Rebuild frontend
```bash
cd "/Users/heyitong/Documents YD/GitHub/Personal/Dream_LIVIN_Shop"
./scripts/build-frontend.sh
```

### Stop server
```bash
pkill -f "Dream_LIVIN_Shop.*main.py"
```

---

## Session Log

**Date**: January 18, 2026

1. User ran CarFinder-master locally (port 8002)
2. User requested new project: Dream LIVIN Shop
3. Discussed requirements:
   - Multi-modal input (text, voice, images, sketch)
   - Dual environment (Earth + Mars)
   - 6 images per round (Earth 2+1, Mars 1+2)
   - Style evolution (sketch → render)
   - LIVIN DNA system (max 8 keywords, user editable)
4. Created project structure
5. Implemented backend (AI client, prompt engine, API)
6. Implemented frontend (React, dual panels, DNA editing)
7. Built and tested successfully
8. Deferred map integration to later phase

---

*Last updated: January 18, 2026*
