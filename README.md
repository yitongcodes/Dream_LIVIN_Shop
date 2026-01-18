# Dream LIVIN Shop 🏠🚀

An AI-powered vision generator that helps users discover and refine their dream **modular mobile home** design for both **Earth and Mars**. Built with FastAPI and React.

![Earth & Mars](https://img.shields.io/badge/Environments-Earth%20%26%20Mars-blue)
![Python](https://img.shields.io/badge/Backend-FastAPI-green)
![React](https://img.shields.io/badge/Frontend-React%20%2B%20Vite-61dafb)

## ✨ Features

### Multi-Modal Input
- **Text Description**: Describe your dream living space
- **Voice Input**: Speak your vision with real-time waveform visualization
- **Reference Images**: Upload style inspiration photos
- **Environment Photos**: Show spaces you want to transform
- **Sketch Upload**: Share layout ideas through simple drawings

### Dual-Environment Generation
Each round generates **6 images** across two environments:

| Environment | Strategy | Focus |
|-------------|----------|-------|
| **Earth** | 2 Evolve + 1 Explore | Realistic, sustainable, harmonious |
| **Mars** | 1 Evolve + 2 Explore | Bold, futuristic, pioneering |

### LIVIN DNA System
- AI extracts up to **8 keywords** that define your design DNA
- **Interactive editing**: Select, remove, or add keywords
- DNA persists across rounds for iterative refinement
- Captures: spatial preferences, materials, colors, emotions

### Style Evolution
- **Rounds 1-2**: Hand-drawn architectural sketches, concept art style
- **Rounds 3+**: Cinematic photorealistic renders with lifestyle scenes

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Frontend**: React + Vite
- **AI Engine**: AI Builder Space Platform
  - Gemini 3 Flash (Planning with Thinking Mode)
  - Gemini 2.5 Flash Image (Image Generation)
  - Audio Transcription API
- **Styling**: Custom CSS with Earth/Mars themed design

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js & npm
- AI Builder Space API Token

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yitongcodes/Dream_LIVIN_Shop.git
   cd Dream_LIVIN_Shop
   ```

2. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your AI_BUILDER_TOKEN
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Build the frontend**
   ```bash
   cd frontend && npm install && cd ..
   ./scripts/build-frontend.sh
   ```

5. **Run the application**
   ```bash
   python3 main.py
   ```

6. **Open in browser**
   ```
   http://localhost:8003
   ```

## 📁 Project Structure

```
Dream_LIVIN_Shop/
├── main.py                 # FastAPI backend
├── services/
│   ├── ai_client.py        # AI Builder Space client
│   └── prompt_engine.py    # Prompt engineering module
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   ├── App.css         # Application styles
│   │   └── index.css       # Global styles
│   └── package.json
├── scripts/
│   └── build-frontend.sh
├── outputs/images/         # Generated images
├── static/                 # Built frontend
└── memory.md               # Project documentation
```

## 🎨 Design Philosophy

**Earth Visions**: Grounded, practical, sustainable. Modular homes that blend with natural landscapes and promote harmonious living.

**Mars Visions**: 
- **Exterior**: Wild, adventurous, inspired by *The Expanse*, *Dune*, *No Man's Sky*, *Starfield*
- **Interior**: Cozy Earth-like comfort — warm lighting, natural materials, human-centric design despite the alien exterior

## 🗺️ Roadmap

- [x] Multi-modal input (text, voice, images)
- [x] Dual-environment generation (Earth/Mars)
- [x] LIVIN DNA system with user editing
- [x] Style evolution across rounds
- [ ] Map integration (Leaflet + NASA Mars Trek)
- [ ] Image-to-image generation
- [ ] Export & sharing features

## 📄 License

MIT License - feel free to explore and build upon!

## 🙏 Acknowledgments

Inspired by [CarFinder](https://github.com/grapeot/CarFinder) - an AI-driven automotive design discovery engine.

---

*Dream your space. On Earth. On Mars. Anywhere.*
