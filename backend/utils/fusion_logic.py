from groq import Groq
import json
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env file
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))



def tier1_fusion(pose_summary, audio_summary, scene_summary):
    prompt = (
        f"Based on the following data from a video stream, determine if there is a suspected anomaly such as a fall or crawl. "
        f"Respond with 'Yes' or 'No' followed by a brief justification.\n\n"
        f"Pose: {pose_summary}\n"
        f"Audio: {audio_summary}\n"
        f"Scene: {scene_summary}"
    )
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-8b-8192",
    )
    verdict = response.choices[0].message.content.strip()
    return "Suspected Anomaly" if verdict.startswith("Yes") else "Normal", verdict

def tier2_fusion(audio_transcript, captions, visual_anomaly_max, tier1_details):
    try:
        visual_summary = " | ".join(captions) if captions else "No captions."
        scene_summary = f"Highest visual anomaly probability: {visual_anomaly_max:.2f}"
        prompt = (
            f"Analyze the following anomaly detection data and provide scores. "
            f"Return ONLY a valid JSON object with no additional text or formatting.\n\n"
            f"Data:\n"
            f"- Tier 1 Analysis: {tier1_details}\n"
            f"- Audio Transcript: {audio_transcript or 'No audio'}\n"
            f"- Image Captions: {visual_summary}\n"
            f"- Visual Anomaly Score: {visual_anomaly_max:.2f}\n\n"
            f"Return JSON with these exact keys:\n"
            f'{{"visual_score": <0-1 float>, "audio_score": <0-1 float>, "text_alignment_score": <0-1 float>, '
            f'"multimodal_agreement": <0-1 float>, "reasoning_summary": "<brief explanation>", "threat_severity_index": <0-1 float>}}'
        )
        
        print(f"Tier 2 fusion prompt: {prompt}")  # Debug logging
        
        response = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-70b-8192",
            temperature=0.1  # Lower temperature for more consistent JSON output
        )
        output = response.choices[0].message.content.strip()
        print(f"Tier 2 fusion raw response: {output}")  # Debug logging
        
        # Clean up the response to extract JSON
        if "```json" in output:
            output = output.split("```json")[1].split("```")[0].strip()
        elif "```" in output:
            output = output.split("```")[1].split("```")[0].strip()
        
        # Try to parse JSON
        result = json.loads(output)
        
        # Validate required keys
        required_keys = ["visual_score", "audio_score", "text_alignment_score", 
                        "multimodal_agreement", "reasoning_summary", "threat_severity_index"]
        
        for key in required_keys:
            if key not in result:
                raise KeyError(f"Missing required key: {key}")
        
        # Validate score ranges
        for score_key in ["visual_score", "audio_score", "text_alignment_score", 
                         "multimodal_agreement", "threat_severity_index"]:
            if not (0 <= result[score_key] <= 1):
                result[score_key] = max(0, min(1, result[score_key]))  # Clamp to 0-1
        
        print(f"Tier 2 fusion successful: {result}")  # Debug logging
        return result
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error in tier2_fusion: {e}")
        print(f"Raw output: {output}")
    except Exception as e:
        print(f"Error in tier2_fusion: {e}")
    
    # Enhanced fallback with actual data-based scoring
    fallback_visual_score = min(1.0, visual_anomaly_max * 2)  # Scale up the visual score
    fallback_audio_score = 0.3 if audio_transcript and len(audio_transcript.strip()) > 0 else 0.1
    fallback_threat = (fallback_visual_score + fallback_audio_score) / 2
    
    result = {
        "visual_score": fallback_visual_score,
        "audio_score": fallback_audio_score,
        "text_alignment_score": 0.4,
        "multimodal_agreement": 0.4,
        "reasoning_summary": f"Fallback analysis: Visual anomaly {visual_anomaly_max:.2f}, Audio available: {bool(audio_transcript)}",
        "threat_severity_index": fallback_threat
    }
    print(f"Using fallback tier2 result: {result}")
    return result