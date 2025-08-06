# WebRTC Audio Processing for Python

Python bindings for WebRTC Audio Processing. This is a downstream version of [this repo](https://github.com/xiongyihui/python-webrtc-audio-processing.git)'s work with the most recent 7 years of work on WebRTC as well as a slightly different interface. 

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
pip install webrtc_audio_processing
```

## Usage
```python
from webrtc_audio_processing import AudioProcessingModule as AP

ap = AP(enable_vad=True, enable_ns=True)
ap.set_stream_format(16000, 1)      # set sample rate and channels
ap.set_ns_level(1)                  # NS level from 0 to 3
ap.set_vad_level(1)                 # VAD level from 0 to 3

audio_10ms = '\0' * 160 * 2         # 10ms, 16000 sample rate, 16 bits, 1 channel

# only support processing 10ms audio data each time
audio_out = ap.process_stream(audio_10ms)
print('voice: {}'.format(ap.has_voice()))
```
