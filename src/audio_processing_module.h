
#ifndef __AUDIO_PROCESSOR_MODULE_H__
#define __AUDIO_PROCESSOR_MODULE_H__

#include "webrtc/api/scoped_refptr.h"

namespace webrtc {
    class AudioProcessing;
    class ProcessingConfig;
    class StreamConfig;
    template <typename T> class ChannelBuffer;
}

using namespace std;
using namespace webrtc;

class AudioProcessor {
public:
    /**
     * @brief Create an AudioProcessor instance.
     * Instantiated with default settings that can be changed later.
     */
    AudioProcessor();

    ~AudioProcessor();

private:
    webrtc::scoped_refptr<webrtc::AudioProcessing> apm_;
    webrtc::ProcessingConfig *config_;
    bool initialized_;
};


#endif // __AUDIO_PROCESSOR_H__
