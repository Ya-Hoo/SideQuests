"""
Note Utilities Module
=====================

Handles:
- Frequency <-> MIDI note conversion
- Note naming (C4, D#3, etc.)
- Arduino sketch generation
"""

import numpy as np


# ============================================================================
# FREQUENCY <-> NOTE CONVERSION
# ============================================================================

def frequency_to_midi(frequency, a4_hz=440.0):
    """
    Convert frequency (Hz) to MIDI note number.
    
    Formula: midi_note = 69 + 12 * log2(frequency / 440)
    
    Args:
        frequency: frequency in Hz
        a4_hz: reference frequency for A4 (default 440 Hz)
    
    Returns:
        midi_note: MIDI note number (0-127)
    """
    if frequency <= 0:
        return None
    midi_note = 69 + 12 * np.log2(frequency / a4_hz)
    return midi_note


def midi_to_note_name(midi_note):
    """
    Convert MIDI note number to note name (e.g., 'C4', 'D#3').
    
    Args:
        midi_note: MIDI note number (integer)
    
    Returns:
        note_name: string like 'C4', 'D#3', etc.
    """
    note_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    octave = (midi_note // 12) - 1
    note_index = int(midi_note % 12)
    return f"{note_names[note_index]}{octave}"


def midi_to_frequency(midi_note, a4_hz=440.0):
    """
    Convert MIDI note number back to frequency in Hz.
    
    Args:
        midi_note: MIDI note number
        a4_hz: reference frequency for A4
    
    Returns:
        frequency: frequency in Hz
    """
    return a4_hz * (2 ** ((midi_note - 69) / 12))


# ============================================================================
# ARDUINO SKETCH GENERATION
# ============================================================================

def generate_arduino_sketch(notes, output_file="output_sketch.ino", num_motors=4):
    """
    Generate Arduino sketch with note arrays ready to play on stepper motors.
    
    Args:
        notes: list of (frequency_hz, start_time_s, duration_s) tuples
        output_file: output filename for the .ino sketch
        num_motors: number of stepper motors (default 4)
    
    Returns:
        output_file: path to generated sketch
    """
    # Quantize frequencies to nearest MIDI note
    quantized_notes = []
    for freq, start, dur in notes:
        midi = frequency_to_midi(freq)
        if midi:
            # Round to nearest semitone
            midi_rounded = round(midi)
            freq_quantized = midi_to_frequency(midi_rounded)
            note_name = midi_to_note_name(midi_rounded)
            duration_ms = int(dur * 1000)
            quantized_notes.append((freq_quantized, note_name, duration_ms))
    
    # Define pin assignments for up to 4 motors
    pin_config = {
        1: ("STEP_PIN_1", 3, "DIR_PIN_1", 4),
        2: ("STEP_PIN_2", 5, "DIR_PIN_2", 6),
        3: ("STEP_PIN_3", 9, "DIR_PIN_3", 10),
        4: ("STEP_PIN_4", 11, "DIR_PIN_4", 12),
    }
    
    # Build the Arduino sketch
    sketch = f'''// Auto-generated Arduino sketch for stepper motor music player
// NEMA 17 stepper motors controlled via A4988 drivers
// Generated for {num_motors} motors

'''
    
    # Add pin definitions
    for i in range(1, num_motors + 1):
        if i in pin_config:
            step_name, step_pin, dir_name, dir_pin = pin_config[i]
            sketch += f"#define {step_name} {step_pin}\n"
            sketch += f"#define {dir_name} {dir_pin}\n"
    
    sketch += f"\n// Melody frequencies (Hz) for motor 1\n"
    sketch += f"#define NOTE_COUNT {len(quantized_notes)}\n\n"
    
    # Generate frequency array
    sketch += "int melody[] = {\n"
    for i, (freq, note_name, _) in enumerate(quantized_notes):
        sketch += f"  {int(freq)},  // {note_name}\n"
    sketch += "};\n\n"
    
    # Generate duration array
    sketch += "int durations[] = {\n"
    for i, (_, note_name, dur_ms) in enumerate(quantized_notes):
        sketch += f"  {dur_ms},  // {note_name}\n"
    sketch += "};\n\n"
    
    # Generate setup and loop functions
    sketch += "void setup() {\n"
    for i in range(1, num_motors + 1):
        if i in pin_config:
            step_name, step_pin, dir_name, dir_pin = pin_config[i]
            sketch += f"  pinMode({step_name}, OUTPUT);\n"
            sketch += f"  pinMode({dir_name}, OUTPUT);\n"
    
    sketch += "\n  // Set direction (HIGH or LOW)\n"
    for i in range(1, num_motors + 1):
        if i in pin_config:
            _, _, dir_name, _ = pin_config[i]
            sketch += f"  digitalWrite({dir_name}, HIGH);\n"
    
    sketch += "}\n\n"
    
    sketch += '''void loop() {
  for (int i = 0; i < NOTE_COUNT; i++) {
    // Play note on motor 1
    tone(STEP_PIN_1, melody[i]);
    delay(durations[i]);
    noTone(STEP_PIN_1);
    delay(30);  // Small gap between notes
  }
  
  // Pause before repeating
  delay(2000);
}
'''
    
    with open(output_file, 'w') as f:
        f.write(sketch)
    
    return output_file
