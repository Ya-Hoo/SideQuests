"""
Audio Processing Module
=======================

Handles:
- WAV file I/O
- STFT (Short-Time Fourier Transform)
- Harmonic Product Spectrum (HPS)
- Peak picking and note extraction
"""

import wave
import numpy as np


def read_wav(filename):
    """
    Read a WAV file and return audio data, sample rate, and duration.
    
    Args:
        filename: path to WAV file
    
    Returns:
        audio_data: numpy array of samples (normalized to [-1, 1])
        sample_rate: samples per second (Hz)
        duration: length in seconds
    """
    with wave.open(filename, 'rb') as wav_file:
        n_channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        n_frames = wav_file.getnframes()
        
        audio_bytes = wav_file.readframes(n_frames)
        
        if sample_width == 2:
            dtype = np.int16
        elif sample_width == 4:
            dtype = np.int32
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")
        
        audio_data = np.frombuffer(audio_bytes, dtype=dtype)
        
        # Handle stereo: take first channel
        if n_channels > 1:
            audio_data = audio_data[::n_channels]
        
        # Normalize to [-1, 1]
        max_val = 2 ** (sample_width * 8 - 1)
        audio_data = audio_data.astype(np.float32) / max_val
        
        duration = n_frames / sample_rate
        
        return audio_data, sample_rate, duration


def hann_window(length):
    """Generate Hann window to reduce spectral leakage."""
    n = np.arange(length)
    window = 0.5 * (1 - np.cos(2 * np.pi * n / (length - 1)))
    return window


def stft(audio, window_size=2048, hop_size=512, sample_rate=44100):
    """
    Compute Short-Time Fourier Transform.
    
    Slides a window across the audio and computes FFT of each chunk,
    building a spectrogram (frequency vs time).
    
    Args:
        audio: numpy array of audio samples
        window_size: window length in samples (default 2048)
        hop_size: hop size in samples (default 512)
        sample_rate: sample rate in Hz
    
    Returns:
        spectrogram: 2D array of shape (n_freqs, n_frames)
        frequencies: 1D array of frequency values (Hz)
        times: 1D array of time values (seconds)
    """
    window = hann_window(window_size)
    n_samples = len(audio)
    n_frames = 1 + (n_samples - window_size) // hop_size
    
    spectrogram = np.zeros((window_size, n_frames), dtype=np.float32)
    
    for frame_idx in range(n_frames):
        start = frame_idx * hop_size
        end = start + window_size
        
        if end > n_samples:
            chunk = np.zeros(window_size)
            chunk[:n_samples - start] = audio[start:]
        else:
            chunk = audio[start:end]
        
        windowed_chunk = chunk * window
        X = np.fft.fft(windowed_chunk)
        spectrogram[:, frame_idx] = np.abs(X)
    
    frequencies = np.fft.fftfreq(window_size, d=1/sample_rate)
    times = np.arange(n_frames) * hop_size / sample_rate
    
    return spectrogram, frequencies, times


def harmonic_product_spectrum(spectrogram, harmonics=4):
    """
    Compute HPS to identify true note fundamentals.
    
    Multiplies magnitude at each frequency bin with magnitudes at its harmonics.
    True fundamentals have strong energy at all harmonics, so the product is large.
    Stray harmonic peaks (which don't have energy at 2x, 3x, etc.) get suppressed.
    
    Args:
        spectrogram: 2D array of shape (n_freqs, n_frames)
        harmonics: number of harmonics to include (default 4)
    
    Returns:
        hps: 2D array of same shape with harmonic product
    """
    n_freqs, n_frames = spectrogram.shape
    hps = np.ones_like(spectrogram, dtype=np.float32)
    
    for harmonic in range(1, harmonics + 1):
        downsampled = spectrogram[::harmonic, :]
        padded = np.zeros_like(spectrogram)
        padded[:downsampled.shape[0], :] = downsampled
        hps *= padded
    
    return hps


def find_peaks_per_frame(spectrum, min_magnitude=0.01, min_distance_bins=10):
    """
    Find peaks (local maxima) in a single spectrum frame.
    
    Args:
        spectrum: 1D array of magnitudes
        min_magnitude: threshold (relative to max), 0-1
        min_distance_bins: minimum separation between peaks
    
    Returns:
        peak_bins: indices of peaks
        peak_mags: magnitudes at peaks
    """
    max_mag = np.max(spectrum)
    threshold = min_magnitude * max_mag
    
    peak_bins = []
    
    for bin_idx in range(1, len(spectrum) - 1):
        if spectrum[bin_idx] > spectrum[bin_idx - 1] and spectrum[bin_idx] > spectrum[bin_idx + 1]:
            if spectrum[bin_idx] > threshold:
                too_close = False
                for existing_peak in peak_bins:
                    if abs(bin_idx - existing_peak) < min_distance_bins:
                        if spectrum[bin_idx] > spectrum[existing_peak]:
                            peak_bins.remove(existing_peak)
                        else:
                            too_close = True
                            break
                
                if not too_close:
                    peak_bins.append(bin_idx)
    
    peak_bins = np.array(peak_bins, dtype=int)
    peak_mags = spectrum[peak_bins] if len(peak_bins) > 0 else np.array([])
    
    return peak_bins, peak_mags


def bin_to_frequency(bin_idx, sample_rate, n_fft):
    """Convert FFT bin index to frequency in Hz."""
    return bin_idx * sample_rate / n_fft


def extract_notes_from_spectrogram(spectrogram, frequencies, times, sample_rate, n_fft=2048, num_motors=4):
    """
    Extract note sequences from spectrogram using HPS peak picking.
    
    Can extract either monophonic (1 melody) or polyphonic (multiple simultaneous notes).
    
    Args:
        spectrogram: 2D array from STFT
        frequencies: frequency array
        times: time array
        sample_rate: sample rate in Hz
        n_fft: FFT size (default 2048)
        num_motors: 1 for monophonic (strongest peak only), 
                    2-4 for polyphonic (top N peaks per frame)
    
    Returns:
        notes: if num_motors=1, returns list of (freq, start, duration) tuples
               if num_motors>1, returns list of lists: [[motor1_notes], [motor2_notes], ...]
    """
    print("  Computing Harmonic Product Spectrum...")
    hps = harmonic_product_spectrum(spectrogram, harmonics=4)
    
    print(f"  Finding peaks in each frame (top {num_motors} peaks per frame)...")
    
    # Store peaks for each frame: list of lists
    # all_frame_peaks[frame_idx] = [freq1, freq2, freq3, ...]
    all_frame_peaks = []
    all_frame_times = []
    
    for frame_idx in range(hps.shape[1]):
        spectrum = hps[:, frame_idx]
        peak_bins, peak_mags = find_peaks_per_frame(spectrum, min_magnitude=0.01, min_distance_bins=10)
        
        if len(peak_bins) > 0:
            # Sort peaks by magnitude (strongest first)
            sorted_indices = np.argsort(peak_mags)[::-1]
            top_bins = peak_bins[sorted_indices][:num_motors]  # Take top num_motors peaks
            
            frame_freqs = []
            for bin_idx in top_bins:
                freq = bin_to_frequency(bin_idx, sample_rate, n_fft)
                # Only keep frequencies in melodic range (80-2000 Hz)
                if 80 < freq < 2000:
                    frame_freqs.append(freq)
            
            if len(frame_freqs) > 0:
                all_frame_peaks.append(frame_freqs)
                all_frame_times.append(times[frame_idx])
    
    if len(all_frame_peaks) == 0:
        print("    ⚠ No peaks found!")
        return []
    
    # Pad frames so all have the same number of notes (for consistency)
    # Frames with fewer peaks get zeros/silence
    max_peaks = max(len(f) for f in all_frame_peaks)
    for frame_peaks in all_frame_peaks:
        while len(frame_peaks) < max_peaks:
            frame_peaks.append(0)  # 0 Hz = silence/no note
    
    print(f"  Clustering frames into discrete notes...")
    
    # Now cluster frames into notes, but track multiple notes simultaneously
    # Create one note list per motor
    notes_per_motor = [[] for _ in range(max_peaks)]
    
    for motor_idx in range(max_peaks):
        # Extract frequency sequence for this motor
        motor_freqs = [all_frame_peaks[frame_idx][motor_idx] for frame_idx in range(len(all_frame_peaks))]
        
        # Cluster into notes
        current_start = all_frame_times[0]
        freq_history = [motor_freqs[0]]
        
        for i in range(1, len(motor_freqs)):
            freq = motor_freqs[i]
            time = all_frame_times[i]
            
            # Skip silence frames
            if freq == 0:
                # If we have an active note, save it
                if any(f > 0 for f in freq_history):
                    note_freq = np.mean([f for f in freq_history if f > 0])
                    note_duration = time - current_start
                    if note_duration > 0.05:
                        notes_per_motor[motor_idx].append((note_freq, current_start, note_duration))
                
                # Reset for next note
                current_start = time
                freq_history = [freq]
                continue
            
            # Normal clustering
            active_freqs = [f for f in freq_history if f > 0]
            if len(active_freqs) == 0:
                # Starting a new note
                freq_history = [freq]
            else:
                avg_freq = np.mean(active_freqs)
                freq_threshold = max(25, avg_freq * 0.05)
                
                if abs(freq - avg_freq) < freq_threshold:
                    freq_history.append(freq)
                else:
                    # Save previous note
                    note_freq = np.mean([f for f in freq_history if f > 0])
                    note_duration = time - current_start
                    if note_duration > 0.05:
                        notes_per_motor[motor_idx].append((note_freq, current_start, note_duration))
                    
                    # Start new note
                    current_start = time
                    freq_history = [freq]
        
        # Last note
        if len(freq_history) > 0:
            active_freqs = [f for f in freq_history if f > 0]
            if len(active_freqs) > 0:
                note_freq = np.mean(active_freqs)
                note_duration = all_frame_times[-1] - current_start
                if note_duration > 0.05:
                    notes_per_motor[motor_idx].append((note_freq, current_start, note_duration))
    
    # If monophonic (num_motors=1), return flat list
    if num_motors == 1:
        return notes_per_motor[0]
    
    # If polyphonic, return per-motor lists
    return notes_per_motor