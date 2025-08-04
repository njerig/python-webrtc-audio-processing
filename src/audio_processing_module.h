
#ifndef __AUDIO_PROCESSING_MODULE_H__
#define __AUDIO_PROCESSING_MODULE_H__

#include "webrtc/api/scoped_refptr.h"
#include "webrtc/api/audio/audio_processing.h"
#include <memory>

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
    AudioProcessor(bool enable_aec = true,
                   bool enable_ns = true,
                   bool enable_agc = true,
                   bool enable_vad = true);
    
    /**
     * @brief Set the forward stream format.
     * This method must be called before processing audio.
        * @param sample_rate_in Input sample rate in Hz.
        * @param channel_count_in Number of input audio channels.
        * @param sample_rate_out Output sample rate in Hz.
        * @param channel_count_out Number of output audio channels.
     */
    void set_stream_format(int sample_rate_in = 32000,
                           int channel_count_in = 1,
                           int sample_rate_out = -1,
                           int channel_count_out = -1);

    /**
     * @brief Set the reverse stream format. The reverse stream is
     * typically used for echo cancellation.
     * This method must be called before processing audio.
        * @param sample_rate_in Reverse input sample rate in Hz.
        * @param channel_count_in Number of reverse input audio channels.
     */
    void set_reverse_stream_format(int sample_rate_in = 32000, 
                                   int channel_count_in = 1);

    /**
     * @brief Get the sample rate of the input stream.
        * @return Sample rate in Hz.
     */
    int get_sample_rate_in() const;

    /**
     * @brief Get the sample rate of the output stream.
        * @return Sample rate in Hz.
     */
    int get_sample_rate_out() const;

    /**
     * @brief Get the number of channels in the input stream.
        * @return Number of channels.
     */
    int get_channel_count_in() const;

    /**
     * @brief Get the number of channels in the output stream.
        * @return Number of channels.
     */
    int get_channel_count_out() const;

    /**
     * @brief Get the sample rate of the reverse input stream.
        * @return Sample rate in Hz.
     */
    int get_reverse_sample_rate_in() const;

    /**
     * @brief Get the number of channels in the reverse input stream.
        * @return Number of channels.
     */
    int get_reverse_channel_count_in() const;

    ~AudioProcessor();

private:
    webrtc::scoped_refptr<webrtc::AudioProcessing> apm_;
    std::unique_ptr<webrtc::ProcessingConfig> processing_config_;
    std::unique_ptr<webrtc::StreamConfig> stream_config_;
    std::unique_ptr<webrtc::StreamConfig> reverse_stream_config_;
    webrtc::AudioProcessing::Config config_;

    bool enable_aec_;
    bool enable_ns_;
    bool enable_agc_;
    bool enable_vad_;

    bool initialized_;
};


#endif // __AUDIO_PROCESSING_H__
