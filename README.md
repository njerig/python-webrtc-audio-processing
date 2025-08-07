# WebRTC Audio Processing for Python

Python bindings for WebRTC Audio Processing. This is a downstream version of [this repo](https://github.com/xiongyihui/python-webrtc-audio-processing.git)'s work with the most recent 7 years of work on WebRTC as well as a slightly different interface. 

## Features

- **Acoustic Echo Cancellation (AEC)**: Removes echo from audio streams
- **Noise Suppression (NS)**: Reduces background noise
- **Automatic Gain Control (AGC)**: Automatically adjusts audio levels
- **Voice Activity Detection (VAD)**: Detects when speech is present in audio

## Requirements
+ swig
+ meson
+ compile toolchain
+ python3

## Build
```bash
git clone https://github.com/njerig/python-webrtc-audio-processing.git
cd python-webrtc-audio-processing
git submodule init && git submodule update
pip install ./webrtc_audio_processing
```

## Basic Usage

### Simple Audio Processing
```python
from webrtc_audio_processing import AudioProcessor

# Initialize with all features enabled
ap = AudioProcessor(enable_aec=True, enable_ns=True, enable_agc=True, enable_vad=True)
ap.set_stream_format(16000, 1)      # 16kHz mono

# Process 10ms of audio data
audio_10ms = b'\0' * 160 * 2        # 10ms, 16000 sample rate, 16 bits, 1 channel
audio_out = ap.process_stream(audio_10ms)

# Check if voice was detected
if ap.has_voice():
    print("Voice detected!")
```

### Configuration Options

```python
from webrtc_audio_processing import AudioProcessor

# Initialize with specific features
ap = AudioProcessor(
    enable_aec=True,    # Echo cancellation
    enable_ns=True,     # Noise suppression  
    enable_agc=True,    # Automatic gain control
    enable_vad=True     # Voice activity detection
)

# Set audio format
ap.set_stream_format(
    sample_rate_in=16000,      # Input sample rate (Hz)
    channel_count_in=1,        # Input channels
    sample_rate_out=16000,     # Output sample rate (Hz) 
    channel_count_out=1        # Output channels
)

# Set reverse stream for echo cancellation
ap.set_reverse_stream_format(16000, 1)

# Set stream delay for echo cancellation
ap.set_stream_delay(50)  # 50ms delay

# Set VAD aggressiveness
ap.set_vad_aggressiveness(1)  # 0-3

# Check feature status
print(f"AEC enabled: {ap.aec_enabled()}")
print(f"NS enabled: {ap.ns_enabled()}")
print(f"AGC enabled: {ap.agc_enabled()}")
print(f"VAD enabled: {ap.vad_enabled()}")
```