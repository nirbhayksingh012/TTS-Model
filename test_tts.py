import os
import json
import argparse
import sys
import time
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser(description="Test tryorato/orato-tts-hindi-v1 model locally")
    parser.add_argument("--text", type=str, default="नमस्ते! आप कैसे हैं? ओराटो टीटीएस का हिंदी संस्करण परीक्षण के लिए तैयार है।", help="Hindi/Hinglish text to synthesize")
    parser.add_argument("--voice", type=str, default="female", choices=["female", "male"], help="Voice gender to use for cloning (female or male)")
    parser.add_argument("--output", type=str, default="output.wav", help="Path to save the generated WAV file")
    parser.add_argument("--device", type=str, default=None, choices=["cuda", "cpu"], help="Device to run on (cuda or cpu)")
    return parser.parse_args()

def main():
    # Force stdout/stderr to use UTF-8 encoding (fixes Windows console printing Hindi)
    if hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
    if hasattr(sys.stderr, "reconfigure"):
        try:
            sys.stderr.reconfigure(encoding="utf-8")
        except Exception:
            pass

    args = parse_args()
    
    # Check dependencies
    try:
        # pyrefly: ignore [missing-import]
        import torch
        # pyrefly: ignore [missing-import]
        from huggingface_hub import snapshot_download
        
        # Monkeypatch f5-tts to load the checkpoint using float32 on CUDA.
        # F5-TTS's default float16 precision causes numerical instability (silence/NaNs) 
        # pyrefly: ignore [missing-import]
        import f5_tts.infer.utils_infer as utils_infer
        original_load_checkpoint = utils_infer.load_checkpoint
        
        def patched_load_checkpoint(model, ckpt_path, device, dtype=None, use_ema=True):
            print("[*] Patched load_checkpoint: forcing float32 precision for model weights...")
            return original_load_checkpoint(model, ckpt_path, device, dtype=torch.float32, use_ema=use_ema)
            
        utils_infer.load_checkpoint = patched_load_checkpoint
        
        # pyrefly: ignore [missing-import]
        from f5_tts.api import F5TTS
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Please run setup_env.bat to install all required libraries first.")
        sys.exit(1)

    # Determine device
    if args.device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    else:
        device = args.device

    print(f"[*] Target device set to: {device.upper()}")

    # 1. Download Model Repository from Hugging Face
    repo_id = "tryorato/orato-tts-hindi-v1"
    print(f"[*] Downloading '{repo_id}' repository from Hugging Face...")
    try:
        snap = Path(snapshot_download(repo_id))
        print(f"[+] Download complete. Cache directory: {snap}")
    except Exception as e:
        print(f"\n[ERROR] Failed to download model: {e}")
        print("-------------------------------------------------------------------")
        print("This model is GATED. Please follow these steps:")
        print(f"1. Open https://huggingface.co/{repo_id} in your browser.")
        print("2. Log in to your HF account and click 'Accept' to request access.")
        print("3. Authenticate locally by running 'huggingface-cli login' in your shell.")
        print("-------------------------------------------------------------------")
        sys.exit(1)

    # 2. Check and Load Configuration
    voices_json_path = snap / "voices.json"
    ckpt = snap / "model.pt"
    vocab = snap / "vocab.txt"

    if not voices_json_path.exists():
        print(f"[ERROR] voices.json not found in repository snapshot at: {voices_json_path}")
        sys.exit(1)
    if not ckpt.exists():
        print(f"[ERROR] model.pt not found in repository snapshot at: {ckpt}")
        sys.exit(1)
    if not vocab.exists():
        print(f"[ERROR] vocab.txt not found in repository snapshot at: {vocab}")
        sys.exit(1)

    # Load voices configuration
    try:
        with open(voices_json_path, "r", encoding="utf-8") as f:
            voices = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to parse voices.json: {e}")
        sys.exit(1)

    if args.voice not in voices:
        print(f"[ERROR] Selected voice '{args.voice}' not found in voices.json. Available: {list(voices.keys())}")
        sys.exit(1)

    # Get voice-specific parameters
    ref_wav_rel = voices[args.voice]["wav"]
    ref_wav = snap / ref_wav_rel
    
    # Try 'ref_text' first, then fallback to 'text'
    ref_text = voices[args.voice].get("ref_text", voices[args.voice].get("text"))

    if not ref_wav.exists():
        print(f"[ERROR] Reference audio file not found at: {ref_wav}")
        sys.exit(1)

    if not ref_text:
        print(f"[ERROR] Reference text not found for voice '{args.voice}' in voices.json")
        sys.exit(1)

    # 3. Initialize F5-TTS with custom checkpoint and vocabulary
    print("[*] Initializing F5-TTS model with Orato checkpoint...")
    model_load_start = time.time()
    try:
        f5tts = F5TTS(
            model="F5TTS_v1_Base",
            ckpt_file=str(ckpt),
            vocab_file=str(vocab),
            use_ema=False,
            device=device
        )
        print(f"[+] Model initialized successfully in {time.time() - model_load_start:.2f} seconds.")
    except Exception as e:
        print(f"[ERROR] Failed to initialize F5-TTS model: {e}")
        sys.exit(1)

    # 4. Generate Hindi Speech
    print(f"[*] Starting Text-to-Speech synthesis:")
    print(f"    - Input Hindi text: '{args.text}'")
    print(f"    - Using voice pack: {args.voice}")
    print(f"    - Reference WAV: {ref_wav.name}")
    print(f"    - Reference transcript: '{ref_text}'")

    infer_start = time.time()
    try:
        # F5-TTS infer method accepts file_wave parameter to save the output file directly
        wav, sr, spec = f5tts.infer(
            ref_file=str(ref_wav),
            ref_text=ref_text,
            gen_text=args.text,
            file_wave=args.output,
            file_spec=None,
            seed=None
        )
        duration = time.time() - infer_start
        print(f"\n[+] Synthesis completed in {duration:.2f} seconds.")
        print(f"[+] Output file saved to: {args.output}")
        print("========================================================")
        print("[*] Successfully generated Hindi TTS audio!")
        print("========================================================")
    except Exception as e:
        print(f"[ERROR] Speech synthesis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
