#!/usr/bin/env python3
"""
Converts WAV audio to Arduino sketch for playing on NEMA 17 stepper motors.

Pipeline:
1. Read WAV file (audio_processor.py)
2. Compute STFT → extract notes using HPS (audio_processor.py)
3. Generate Arduino sketch (note_utils.py)
4. Visualize results (visualizer.py)

Usage:
    python main.py input.wav [output.ino]

Example:
    python main.py happy_birthday.wav my_sketch.ino
"""

import sys
import os
from pathlib import Path

# Import our modules
from audio_processor import read_wav, stft, extract_notes_from_spectrogram
from note_utils import frequency_to_midi, midi_to_note_name, generate_arduino_sketch


def main():
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py input_file.wav [output_sketch.ino]")
        print("\nExample: python main.py happy_birthday.wav my_sketch.ino")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else "output_sketch.ino"
    
    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)
    
    # ========================================================================
    # 1. Read WAV file
    # ========================================================================
    print(f"\n[1/4] Reading audio file: {input_file}")
    try:
        audio, sample_rate, duration = read_wav(input_file)
        print(f"  Sample rate: {sample_rate} Hz")
        print(f"  Duration: {duration:.2f} seconds")
        print(f"  Samples: {len(audio)}")
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    # ========================================================================
    # 2. Compute STFT
    # ========================================================================
    print(f"\n[2/4] Computing STFT (windowed FFT)")
    try:
        spectrogram, frequencies, times = stft(
            audio, 
            window_size=2048, 
            hop_size=512, 
            sample_rate=sample_rate
        )
    except Exception as e:
        print(f"Error computing STFT: {e}")
        sys.exit(1)
    
    # ========================================================================
    # 3. Extract notes
    # ========================================================================
    print(f"\n[3/4] Extracting notes (HPS peak picking)")
    try:
        notes = extract_notes_from_spectrogram(
            spectrogram, 
            frequencies, 
            times, 
            sample_rate
        )
    except Exception as e:
        print(f"Error extracting notes: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ========================================================================
    # 4. Generate Arduino sketch
    # ========================================================================
    print(f"\n[4/4] Generating Arduino sketch")
    try:
        sketch_file = generate_arduino_sketch(notes, output_file)
    except Exception as e:
        print(f"Error generating sketch: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    print("\nComplete!")


if __name__ == "__main__":
    main()
