

SWIG := swig

# Detect OS
UNAME_S := $(shell uname -s)

# Set library file based on OS
ifeq ($(UNAME_S),Darwin)
    WEBRTCLIBFILE = ../webrtc-audio-processing/install/lib/libwebrtc-audio-processing-2.dylib
else
    WEBRTCLIBFILE = ../webrtc-audio-processing/install/lib/libwebrtc-audio-processing-2.so
endif

CXXFLAGS := -fPIC -std=c++17 -I. -I../webrtc-audio-processing -I../webrtc-audio-processing/webrtc -I../webrtc-audio-processing/subprojects/abseil-cpp-20240722.0  $(shell python-config --cflags) -DWEBRTC_AUDIO_PROCESSING_ONLY_BUILD -DWEBRTC_NS_FLOAT

# Set platform-specific linking flags
ifeq ($(UNAME_S),Darwin)
    # macOS
    LDFLAGS := -bundle -undefined dynamic_lookup $(shell python-config --ldflags) -lpthread
else
    # Linux and others
    LDFLAGS := -shared $(shell python-config --ldflags) -lpthread
endif
CXX := g++


all: _webrtc_audio_processing.so

webrtc_audio_processing_wrap.cpp: webrtc_audio_processing.i
	$(SWIG) -I. -c++ -python -o $@ $^

_webrtc_audio_processing.so: webrtc_audio_processing_wrap.o audio_processing_module.o
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^ $(WEBRTCLIBFILE)

clean:
	-rm -f webrtc_audio_processing_wrap.cpp *.o _webrtc_audio_processing.so webrtc_audio_processing.py *.pyc 
