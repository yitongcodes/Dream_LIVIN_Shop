"""
Prompt Engine for Dream LIVIN Shop.
Handles planning prompts and image generation prompts for Earth and Mars environments.
"""
from typing import Dict, Any, List, Optional
import json


class PromptEngine:
    """
    Manages prompt generation for the Dream LIVIN Shop application.
    Implements the dual-environment (Earth/Mars) strategy with style evolution.
    """
    
    # Style evolution based on round number
    STYLE_EVOLUTION = {
        "early": {  # Rounds 1-2
            "primary": "hand-drawn architectural sketch, sci-fi novel illustration style, concept art with visible pencil strokes",
            "secondary": "soft 3D render with artistic touches",
            "ratio": "70% sketch / 30% render",
            "include_characters": False
        },
        "mature": {  # Rounds 3+
            "primary": "cinematic scene render, photorealistic visualization, movie-quality lighting",
            "secondary": "lifestyle scene with human figures in natural poses",
            "ratio": "30% sketch / 70% render",
            "include_characters": True
        }
    }
    
    # Base visual templates
    EARTH_BASE_TEMPLATE = """A {style} of an affordable, flexible, aesthetic modular mobile home on Earth.
Location context: {location_description}
Environment: Realistic Earth setting with natural lighting, familiar landscapes, sustainable integration with nature.
Architecture: Modular, mobile, adaptable design that balances affordability with aesthetic beauty.
Mood: Grounded, practical yet inspiring, harmonious with Earth's environment.
"""

    MARS_OUTDOOR_TEMPLATE = """A {style} of a modular mobile habitat on Mars - EXTERIOR VIEW.
Location context: {location_description}
Environment: Wild Martian landscape - rust-red terrain, dramatic rock formations, pink-orange sky with visible stars, dust storms in distance, alien yet majestic.
Architecture: Bold futuristic design inspired by interstellar exploration games and sci-fi novels. Floating platforms, geodesic domes, bioluminescent accents, adaptive structures.
Mood: Adventurous, awe-inspiring, pioneering spirit, untamed frontier.
Style inspiration: The Expanse, Dune, No Man's Sky, Starfield, Mars colony concept art.
"""

    MARS_INDOOR_TEMPLATE = """A {style} of a modular mobile habitat on Mars - INTERIOR VIEW.
Location context: {location_description}
Exterior visible through windows: Martian landscape with red rocks, alien sky, dust particles catching light.
Interior: Cozy, earth-like living space designed for human comfort. Warm lighting, natural materials (wood tones, soft fabrics), minimal but elegant furniture, plants in hydroponic systems.
Architecture: Smart modular design that feels like home despite being on another planet.
Mood: Safe haven, warmth within the wild, human resilience, comfortable minimalism with design sensibility.
"""

    def __init__(self):
        pass
    
    def get_style_phase(self, round_num: int) -> str:
        """Determine style phase based on round number."""
        return "early" if round_num <= 2 else "mature"
    
    def build_planning_prompt(
        self,
        feedback: str,
        state: Dict[str, Any],
        user_images_description: Optional[str] = None
    ) -> str:
        """
        Build the planning prompt for the LIVIN DNA Manager.
        
        Args:
            feedback: User's current feedback/input
            state: Current LIVIN DNA state
            user_images_description: Optional description of uploaded images
            
        Returns:
            Complete planning prompt string
        """
        current_round = state.get('round', 0) + 1
        style_phase = self.get_style_phase(current_round)
        style_config = self.STYLE_EVOLUTION[style_phase]
        
        # Build history context
        history_context = ""
        if state.get('feedback_history'):
            history_context = "Previous user inputs:\n" + "\n".join(
                [f"- Round {i+1}: {h}" for i, h in enumerate(state.get('feedback_history', [])[-5:])]
            )
        
        prompt = f"""You are the 'LIVIN Genome Architect' - an AI that helps users discover and refine their dream modular mobile home design for both Earth and Mars.

Current LIVIN DNA State:
{json.dumps(state, indent=2, ensure_ascii=False)}

{history_context}

User's New Input: "{feedback}"

{f"User uploaded images showing: {user_images_description}" if user_images_description else ""}

Current Round: {current_round}
Style Phase: {style_phase} ({style_config['ratio']})
Include Human Characters: {style_config['include_characters']}

=== YOUR TASKS ===

1. **UPDATE LIVIN DNA** (Maximum 8 keywords):
   Extract and refine keywords that capture the user's dream home DNA across these dimensions:
   - Spatial preferences (open/cozy, high ceilings, flow)
   - Material preferences (wood, glass, metal, fabric)
   - Color palette tendencies
   - Functional priorities (workspace, relaxation, social)
   - Aesthetic style (minimalist, organic, industrial, futuristic)
   - Emotional qualities (peaceful, adventurous, warm, bold)
   
   Rules:
   - CONSOLIDATE similar concepts
   - PRIORITIZE new feedback over old if contradictory
   - Keep total keywords ≤ 8
   - Each keyword should be 1-3 words

2. **GENERATE DESIGN SUMMARY**:
   Write a 2-3 sentence narrative summarizing the user's "LIVIN Persona" in Markdown.

3. **PLAN 6 IMAGE PROMPTS** using the dual-environment strategy:

   **EARTH GROUP (3 images):**
   - 2 EXPLOITATION prompts: Precise evolution based on confirmed DNA preferences
   - 1 EXPLORATION prompt: Test a new direction the user hasn't considered
   
   **MARS GROUP (3 images):**
   - 1 EXPLOITATION prompt: Adapt Earth preferences to Mars context
   - 2 EXPLORATION prompts: Bold, wild, futuristic concepts pushing boundaries
   
   For each prompt, specify:
   - name: unique identifier
   - prompt: detailed design description
   - type: "exploitation" or "exploration"
   - environment: "earth" or "mars"
   - view: "exterior", "interior", or "both"

4. **STYLE INSTRUCTIONS FOR THIS ROUND**:
   {"Focus on hand-drawn architectural sketches and sci-fi illustration styles. Minimal photorealistic rendering." if style_phase == "early" else "Focus on cinematic, photorealistic renders. Include human figures in natural living scenarios where appropriate."}

=== OUTPUT FORMAT ===
Respond ONLY with valid JSON:

{{
  "updated_state": {{
    "round": {current_round},
    "design_summary": "Markdown narrative of user's LIVIN Persona...",
    "livin_dna": ["keyword1", "keyword2", ...],  // Max 8 keywords
    "confirmed_preferences": ["specific preference 1", "preference 2"],
    "rejected_elements": ["rejected element 1", ...],
    "feedback_history": [...previous + current feedback...]
  }},
  "plan": [
    {{
      "name": "earth_exploit_1",
      "prompt": "Detailed design description...",
      "type": "exploitation",
      "environment": "earth",
      "view": "exterior"
    }},
    // ... 5 more entries (3 earth + 3 mars total)
  ]
}}
"""
        return prompt
    
    def build_image_prompt(
        self,
        design_prompt: str,
        environment: str,
        view: str,
        round_num: int,
        livin_dna: List[str],
        location_description: str = ""
    ) -> str:
        """
        Build the final image generation prompt.
        
        Args:
            design_prompt: AI-generated design description
            environment: "earth" or "mars"
            view: "exterior", "interior", or "both"
            round_num: Current round number
            livin_dna: List of DNA keywords
            location_description: Optional location context
            
        Returns:
            Complete image generation prompt
        """
        style_phase = self.get_style_phase(round_num)
        style_config = self.STYLE_EVOLUTION[style_phase]
        
        # Choose style based on phase
        if style_phase == "early":
            style = "hand-drawn architectural concept sketch with soft watercolor touches"
        else:
            if style_config['include_characters']:
                style = "cinematic photorealistic render with natural human figures in a lifestyle scene"
            else:
                style = "cinematic photorealistic architectural visualization"
        
        # Default location if not provided
        if not location_description:
            location_description = "a scenic location perfect for modular living" if environment == "earth" else "Jezero Crater region, Mars"
        
        # Build base template
        if environment == "earth":
            base = self.EARTH_BASE_TEMPLATE.format(
                style=style,
                location_description=location_description
            )
        else:  # mars
            if view == "interior":
                base = self.MARS_INDOOR_TEMPLATE.format(
                    style=style,
                    location_description=location_description
                )
            else:
                base = self.MARS_OUTDOOR_TEMPLATE.format(
                    style=style,
                    location_description=location_description
                )
        
        # Combine with design prompt and DNA
        dna_string = ", ".join(livin_dna) if livin_dna else "modern, flexible, aesthetic"
        
        full_prompt = f"""{base}

Design Specifications: {design_prompt}

LIVIN DNA Keywords: {dna_string}

Technical Requirements:
- High quality, detailed visualization
- Consistent modular architecture language
- {"Sketch-like artistic style with visible strokes" if style_phase == "early" else "Photorealistic with cinematic lighting"}
- 16:9 aspect ratio composition
- No text, logos, or watermarks
"""
        return full_prompt
