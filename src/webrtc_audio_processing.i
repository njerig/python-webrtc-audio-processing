// webrtc_audio_processing.i

%module webrtc_audio_processing

%begin %{
#define SWIG_PYTHON_STRICT_BYTE_CHAR
%}

%pythonbegin %{
import warnings
# Suppress SWIG internal type warnings
warnings.filterwarnings("ignore", message="builtin type SwigPyPacked has no __module__ attribute")
warnings.filterwarnings("ignore", message="builtin type SwigPyObject has no __module__ attribute")
warnings.filterwarnings("ignore", message="builtin type swigvarlink has no __module__ attribute")
%}

%include "std_string.i"
%include "exception.i"

// Exception handling
%exception {
    try {
        $action
    } catch (const std::exception& e) {
        SWIG_exception(SWIG_RuntimeError, e.what());
    } catch (...) {
        SWIG_exception(SWIG_RuntimeError, "Unknown error");
    }
}

%{
#include "audio_processing_module.h"
%}

// Make sure SWIG knows about default arguments
%feature("autodoc", "1");

%include "audio_processing_module.h"

// Python-specific extensions
%pythoncode %{
# Convenience alias
AP = AudioProcessor

# Add a more Pythonic interface
class AudioProcessingModule(AudioProcessor):
    """
    Enhanced Python interface for WebRTC Audio Processing.
    
    Example:
        # Create processor with AEC, NS, and AGC enabled
        apm = AudioProcessingModule(enable_aec=True, enable_ns=True, enable_agc=True)
        
        # Set stream format (16kHz, mono)
        apm.set_stream_format(16000, 1)
        
        # Configure noise suppression
        apm.set_ns_level(2)  # 0-3: low to very high
        
        # Configure AGC
        apm.set_agc_mode(2)  # Adaptive Digital
        apm.set_agc_target(3)  # Target level in dBFS
        
        # Process audio
        # For echo cancellation, first feed the reverse stream (speaker audio)
        apm.process_reverse_stream(speaker_data)
        
        # Then process the microphone stream
        processed = apm.process_stream(mic_data)
        
        # Check if voice was detected
        if apm.has_voice():
            print("Voice detected!")
    """
    
    # AGC mode constants
    AGC_MODE_FIXED_DIGITAL = 0
    AGC_MODE_ADAPTIVE_ANALOG = 1
    AGC_MODE_ADAPTIVE_DIGITAL = 2
    
    # NS level constants
    NS_LEVEL_LOW = 0
    NS_LEVEL_MODERATE = 1
    NS_LEVEL_HIGH = 2
    NS_LEVEL_VERY_HIGH = 3
    
    # AEC suppression level constants
    AEC_SUPPRESSION_LOW = 0
    AEC_SUPPRESSION_MODERATE = 1
    AEC_SUPPRESSION_HIGH = 2
    
    def __init__(self, **kwargs):
        # Handle both old-style and new-style arguments
        enable_aec = kwargs.get('enable_aec', False)
        enable_ns = kwargs.get('enable_ns', False)
        enable_agc = kwargs.get('enable_agc', False)
        enable_vad = kwargs.get('enable_vad', False)
        
        super().__init__(enable_aec, enable_ns, enable_agc, enable_vad)

# For backward compatibility
AudioProcessor = AudioProcessingModule
%}