import os
import json
import mimetypes
import cv2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from google.cloud import vision, speech

from moviepy.editor import VideoFileClip
from pydub import AudioSegment
import numpy as np
import librosa
import soundfile as sf
import fitz  # PyMuPDF for PDF
import docx  # python-docx for DOCX

# Initialize clients    
vision_client = vision.ImageAnnotatorClient()
speech_client = speech.SpeechClient()

def process_image(image_path):
    with open(image_path, "rb") as f:
        content = f.read()
    image = vision.Image(content=content)
    response = vision_client.text_detection(image=image)
    texts = response.text_annotations
    results = {"image_text": texts[0].description if texts else ""}
    return results


def process_video(video_path):
    results = {"video_frames": [], "video_audio_transcript": ""}

    # --- Process frames with OpenCV ---
    cap = cv2.VideoCapture(video_path)
    frame_rate = 1  # 1 frame per second
    frame_id = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if frame_id % int(cap.get(cv2.CAP_PROP_FPS) * frame_rate) == 0:
            _, buffer = cv2.imencode('.jpg', frame)
            image = vision.Image(content=buffer.tobytes())
            response = vision_client.text_detection(image=image)
            texts = response.text_annotations
            if texts:
                results["video_frames"].append({
                    "frame_id": frame_id,
                    "text": texts[0].description
                })
        frame_id += 1

    cap.release()  # ✅ release OpenCV video

    # --- Extract Audio with MoviePy ---
    print("Extracting audio from video...")
    clip = VideoFileClip(video_path)
    try:
        temp_audio_path = "temp_audio_original.wav"
        clip.audio.write_audiofile(temp_audio_path, codec="pcm_s16le")  # write original audio

        # Convert to mono + 16kHz using pydub
        audio = AudioSegment.from_file(temp_audio_path)
        audio = audio.set_channels(1)   # mono
        audio = audio.set_frame_rate(16000)
        final_audio_path = "temp_audio.wav"
        audio.export(final_audio_path, format="wav")

        with open(final_audio_path, "rb") as f:
            content = f.read()

        audio_proto = speech.RecognitionAudio(content=content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code="en-US"
        )
        response = speech_client.recognize(config=config, audio=audio_proto)
        transcript = " ".join([result.alternatives[0].transcript for result in response.results])
        results["video_audio_transcript"] = transcript
    finally:
        # ✅ Ensure resources are released and temp files removed
        clip.close()
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)
        if os.path.exists(final_audio_path):
            os.remove(final_audio_path)

    return results



def process_audio(audio_path):
    # Load audio using librosa (mono, 16kHz)
    data, sr = librosa.load(audio_path, sr=16000, mono=True)

    # Convert float32 audio (-1.0 to 1.0) to 16-bit PCM
    int16_audio = (data * 32767).astype(np.int16)

    # Save to temporary WAV file
    temp_audio_path = "temp_audio.wav"
    sf.write(temp_audio_path, int16_audio, 16000, subtype='PCM_16')

    with open(temp_audio_path, "rb") as f:
        content = f.read()

    audio_proto = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US"
    )

    response = speech_client.recognize(config=config, audio=audio_proto)
    transcript = " ".join([result.alternatives[0].transcript for result in response.results])

    os.remove(temp_audio_path)
    return {"audio_transcript": transcript}


def process_document(file_path):
    results = {"document_text": ""}
    if file_path.lower().endswith(".pdf"):
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        results["document_text"] = text.strip()
    elif file_path.lower().endswith(".docx"):
        doc = docx.Document(file_path)
        text = "\n".join([para.text for para in doc.paragraphs])
        results["document_text"] = text.strip()
    else:
        results["document_text"] = "Unsupported document format"
    return results


def main(file_path):
    # Convert path to lowercase for extension checking
    lower_path = file_path.lower()
    output = {}

    # ✅ Force handle .pdf and .docx regardless of mimetype
    if lower_path.endswith(".pdf") or lower_path.endswith(".docx"):
        output = process_document(file_path)
    else:
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if mime_type.startswith("image"):
                output = process_image(file_path)
            elif mime_type.startswith("video"):
                output = process_video(file_path)
            elif mime_type.startswith("audio"):
                output = process_audio(file_path)
            else:
                print(f"Unsupported file type: {mime_type}")
                return {"error": f"Unsupported file type: {mime_type}"}
        else:
          print("Could not detect file type")
          return {"error": "Could not detect file type"}

    with open("output.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)
    return output
    print("\n✅ Results saved to output.json")
    print(json.dumps(output, indent=4))


if __name__ == "__main__":
    file_path = input("Enter file path: ")
    main(file_path)
