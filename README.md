# Orato Hindi TTS Testing

This repository provides setup scripts and a testing script to run the fine-tuned Hindi Text-to-Speech (TTS) model **tryorato/orato-tts-hindi-v1** locally.

The model is based on the **F5-TTS** architecture and fine-tuned on Hindi/Hinglish calling-domain speech. It supports voice cloning via reference conditioning (using male and female voices included in the voice pack).

## Prerequisites

1. **Hugging Face Model Access**:
   The model is gated. You must log in to your Hugging Face account, visit the [tryorato/orato-tts-hindi-v1](https://huggingface.co/tryorato/orato-tts-hindi-v1) page, and accept the conditions to request access.
   
2. **Local Authentication**:
   Authenticate your local environment with Hugging Face so that the script can download the gated model:
   ```bash
   huggingface-cli login
   ```
   Provide your Hugging Face Access Token when prompted.

---

## Installation

Run the setup batch script to create a virtual environment (`.venv`) and install PyTorch (with CUDA support) along with the `f5-tts` library:

```bash
setup_env.bat
```

---

## Usage

Activate the virtual environment:
```bash
.venv\Scripts\activate
```

Run the `test_tts.py` script:

```bash
# Generate speech with default female voice and default text
python test_tts.py

# Generate speech with custom text and male voice
python test_tts.py --text "नमस्ते, ओराटो कस्टमर केयर में आपका स्वागत है। मैं आपकी क्या सहायता कर सकता हूँ?" --voice male --output customer_care_male.wav

# Specify running on CPU (default will use CUDA if available)
python test_tts.py --text "कृपया अपना ओटीपी किसी के साथ साझा न करें।" --device cpu --output otp_warning.wav
```

### Options
* `--text`: The Hindi/Hinglish text to synthesize (Devanagari script is highly recommended for best results).
* `--voice`: The reference voice to use (`female` or `male`).
* `--output`: Path to save the synthesized WAV file (default is `output.wav`).
* `--device`: Force execution device (`cuda` or `cpu`).
