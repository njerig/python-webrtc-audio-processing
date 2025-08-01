#include "audio_processing_module.h"

#include "webrtc/api/audio/audio_processing.h"
#include "webrtc/api/scoped_refptr.h"


AudioProcessor::AudioProcessor() {
    apm_ = webrtc::AudioProcessingBuilder().Create();

    initialized_ = false;
}

AudioProcessor::~AudioProcessor()
{
    delete config_;
}
