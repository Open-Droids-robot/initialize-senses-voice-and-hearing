#!/usr/bin/env python3
"""
Jetson-friendly speaker diagnostic helper.

This script isolates the audio-playback path that `VoiceHandler` uses (PyAudio +
pygame) so you can test speaker output without the rest of the stack.
"""

import argparse
import os
import sys
import tempfile
import time
from typing import Dict, List, Optional

from dotenv import load_dotenv
import numpy as np
import pygame
import pyaudio
import wave

# Load environment variables from .env if present
load_dotenv()


def list_output_devices() -> List[Dict[str, str]]:
    """Return a list of PyAudio output devices."""
    audio = pyaudio.PyAudio()
    devices = []
    try:
        for index in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(index)
            if info.get("maxOutputChannels", 0) > 0:
                devices.append(
                    {
                        "index": index,
                        "name": info.get("name", "unknown"),
                        "host_api": audio.get_host_api_info_by_index(
                            info.get("hostApi", 0)
                        ).get("name", "unknown"),
                        "sample_rate": info.get("defaultSampleRate", "n/a"),
                    }
                )
    finally:
        audio.terminate()
    return devices


def _init_mixer(sample_rate: int, channels: int) -> None:
    """Initialize pygame mixer with helpful logging."""
    pygame.mixer.quit()
    pygame.mixer.init(frequency=sample_rate, size=-16, channels=channels)
    print(
        f"[diagnose] pygame.mixer initialized "
        f"(rate={sample_rate}, channels={channels})"
    )


def _play_temp_file(path: str, timeout: float) -> None:
    """Play a file through pygame and wait for completion or timeout."""
    pygame.mixer.music.load(path)
    pygame.mixer.music.play()
    start = time.time()
    while pygame.mixer.music.get_busy() and (time.time() - start) < timeout:
        time.sleep(0.05)
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
        print("[diagnose] playback timed out, stopping mixer")
    else:
        print("[diagnose] playback finished")


def play_sine(
    sample_rate: int = 44100,
    duration: float = 2.0,
    frequency: float = 440.0,
    channels: int = 1,
) -> None:
    """Generate a temporary sine wave and play it through pygame."""
    print(
        f"[diagnose] playing sine @ {frequency}Hz for {duration}s "
        f"(sample_rate={sample_rate})"
    )
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * frequency * t)
    tone = (tone * 32767).astype(np.int16)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp:
        temp_path = temp.name
        with wave.open(temp_path, "wb") as wav_file:
            wav_file.setnchannels(channels)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(tone.tobytes())

    try:
        _play_temp_file(temp_path, timeout=duration + 1.0)
    finally:
        os.unlink(temp_path)


def play_audio_file(file_path: str, timeout: float = 15.0) -> None:
    """Play an arbitrary audio file through pygame."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(file_path)
    print(f"[diagnose] playing '{file_path}'")
    _play_temp_file(file_path, timeout=timeout)


def _generate_elevenlabs_clip(
    text: str,
    voice_id: Optional[str],
    api_key: Optional[str],
    model_id: str = "eleven_multilingual_v2",
) -> str:
    """Fetch speech from ElevenLabs and return a temp file path."""
    api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
    voice_id = voice_id or os.getenv("VOICE_ID") or "21m00Tcm4TlvDq8ikWAM"

    if not api_key:
        raise RuntimeError(
            "ELEVENLABS_API_KEY not provided (use env var or --elevenlabs-api-key)."
        )

    try:
        from elevenlabs import ElevenLabs
        from elevenlabs.core.api_error import ApiError as ElevenLabsApiError
    except ImportError as exc:
        raise RuntimeError("Install elevenlabs: pip install elevenlabs") from exc

    client = ElevenLabs(api_key=api_key)
    try:
        audio_stream = client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            output_format="mp3_44100_64",
            model_id=model_id,
            voice_settings={
                "stability": 0.5,
                "similarity_boost": 0.5,
            },
        )
    except ElevenLabsApiError as exc:
        body = getattr(exc, "body", {})
        detail = body.get("detail") if isinstance(body, dict) else None
        detail_msg = ""
        if isinstance(detail, dict):
            detail_msg = detail.get("message") or detail.get("status") or ""
        status_code = getattr(exc, "status_code", "unknown")
        raise RuntimeError(
            f"ElevenLabs API error (status={status_code}): {detail_msg or exc}"
        ) from exc

    audio_bytes = b"".join(audio_stream)
    temp = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp.write(audio_bytes)
    temp.flush()
    temp.close()
    print(
        f"[diagnose] ElevenLabs clip ready ({len(audio_bytes)} bytes) "
        f"voice_id={voice_id}"
    )
    return temp.name


def main():
    parser = argparse.ArgumentParser(
        description="Diagnose speaker output using pygame."
    )
    parser.add_argument(
        "--sample-rate", type=int, default=44100, help="Mixer sample rate"
    )
    parser.add_argument(
        "--channels", type=int, default=1, choices=[1, 2], help="Number of channels"
    )
    parser.add_argument(
        "--duration", type=float, default=2.0, help="Diagnostic tone duration"
    )
    parser.add_argument(
        "--frequency", type=float, default=440.0, help="Diagnostic tone frequency"
    )
    parser.add_argument(
        "--file", type=str, help="Path to an audio file to play instead of a tone"
    )
    parser.add_argument(
        "--elevenlabs-text",
        type=str,
        help="If set, fetch fresh audio from ElevenLabs for this text",
    )
    parser.add_argument(
        "--elevenlabs-api-key",
        type=str,
        help="Explicit ElevenLabs API key (otherwise env var is used)",
    )
    parser.add_argument(
        "--voice-id",
        type=str,
        help="Override ElevenLabs voice ID",
    )
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="Only list output devices and exit",
    )

    args = parser.parse_args()

    if args.list_devices:
        devices = list_output_devices()
        if not devices:
            print("[diagnose] no output devices found via PyAudio")
            return 1
        print("[diagnose] available output devices:")
        for device in devices:
            print(
                f"  #{device['index']:02d} {device['name']} "
                f"(host={device['host_api']}, rate={device['sample_rate']})"
            )
        return 0

    _init_mixer(args.sample_rate, args.channels)

    temp_path = None

    try:
        if args.elevenlabs_text:
            temp_path = _generate_elevenlabs_clip(
                text=args.elevenlabs_text,
                voice_id=args.voice_id,
                api_key=args.elevenlabs_api_key,
            )
            play_audio_file(temp_path)
        elif args.file:
            play_audio_file(args.file)
        else:
            play_sine(
                sample_rate=args.sample_rate,
                duration=args.duration,
                frequency=args.frequency,
                channels=args.channels,
            )
    finally:
        pygame.mixer.quit()
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())

