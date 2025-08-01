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

%{
#include "audio_processing_module.h"
%}

%include "audio_processing_module.h"

