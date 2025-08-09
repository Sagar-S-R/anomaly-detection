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
    visual_summary = " | ".join(captions) if captions else "No captions."
    scene_summary = f"Highest visual anomaly probability: {visual_anomaly_max:.2f}"
    prompt = (
        f"Fuse the following Tier 2 data with Tier 1 details to give a final anomaly verdict for fall/crawl detection. "
        f"Estimate scores based on the data (higher for anomaly indications).\n"
        f"Output strictly a valid JSON object with these exact keys (no extra text):\n"
        f'{{"visual_score": float between 0 and 1, "audio_score": float between 0 and 1, "text_alignment_score": float between 0 and 1, '
        f'"multimodal_agreement": float between 0 and 1, "reasoning_summary": "brief string summary", "threat_severity_index": float between 0 and 1}}\n\n'
        f"Tier 1: {tier1_details}\n"
        f"Full Audio Transcript: {audio_transcript}\n"
        f"Image Captions: {visual_summary}\n"
        f"Visual Anomaly Prob: {scene_summary}"
    )
    response = groq_client.chat.completions.create(
        messages=[{"role": "user", "content": prompt}],
        model="llama3-70b-8192",
    )
    output = response.choices[0].message.content.strip()
    try:
        result = json.loads(output)
    except json.JSONDecodeError:
        # Fallback in case LLM doesn't output valid JSON
        result = {
            "visual_score": 0.5,
            "audio_score": 0.5,
            "text_alignment_score": 0.5,
            "multimodal_agreement": 0.5,
            "reasoning_summary": "Error in fusion; default values used.",
            "threat_severity_index": 0.5
        }
    return result