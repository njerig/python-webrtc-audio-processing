#include "audio_processing_module.h"

#include "webrtc/api/audio/audio_processing.h"
#include "webrtc/api/scoped_refptr.h"
#include <cstdint>


AudioProcessor::AudioProcessor(bool enable_aec,
                               bool enable_ns,
                               bool enable_agc) { 
    apm_ = webrtc::AudioProcessingBuilder().Create();

    // initialize echo cancelling
    config_.echo_canceller.enabled = enable_aec;
    config_.echo_canceller.mobile_mode = false;

    // initialize noise suppression
    config_.noise_suppression.enabled = enable_ns;
    config_.noise_suppression.level = webrtc::AudioProcessing::Config::NoiseSuppression::Level::kModerate;

    // initialize automatic gain control
    config_.gain_controller1.enabled = enable_agc;
    config_.gain_controller1.mode = webrtc::AudioProcessing::Config::GainController1::Mode::kAdaptiveDigital;
    
    apm_->ApplyConfig(config_);

    stream_config_in_ = std::make_unique<webrtc::StreamConfig>();
    stream_config_out_ = std::make_unique<webrtc::StreamConfig>();
    reverse_stream_config_in_ = std::make_unique<webrtc::StreamConfig>();
}

void AudioProcessor::set_stream_format(int sample_rate_in, 
                                       int channel_count_in, 
                                       int sample_rate_out,
                                       int channel_count_out) {

    if (sample_rate_in < 8000 || sample_rate_in > 384000) {
        throw std::invalid_argument("Sample rate must be between 8000 and 384000 Hz.");
    }
    if (channel_count_in < 1) {
        throw std::invalid_argument("Number of channels must be at least 1.");
    }

    stream_config_in_ = std::make_unique<webrtc::StreamConfig>(sample_rate_in, channel_count_in);
    // default to input sample rate and channel count if not specified
    if (sample_rate_out == -1) {
        sample_rate_out = sample_rate_in;
    }
    if (channel_count_out == -1) {
        channel_count_out = channel_count_in;
    }
    stream_config_out_ = std::make_unique<webrtc::StreamConfig>(sample_rate_out, channel_count_out);
}

void AudioProcessor::set_reverse_stream_format(int sample_rate_in,
                                               int channel_count_in) {

    if (sample_rate_in < 8000 || sample_rate_in > 384000) {
        throw std::invalid_argument("Sample rate must be between 8000 and 384000 Hz.");
    }
    if (channel_count_in < 1) {
        throw std::invalid_argument("Number of channels must be at least 1.");
    }

    reverse_stream_config_in_ = std::make_unique<webrtc::StreamConfig>(sample_rate_in, channel_count_in);
}

void AudioProcessor::set_stream_delay(int delay_ms) {
    if (delay_ms < 0) {
        throw std::invalid_argument("Delay must be greater than 0 ms.");
    }
    apm_->set_stream_delay_ms(delay_ms);
}

int AudioProcessor::get_sample_rate_in() const {
    if (stream_config_in_) {
        return stream_config_in_->sample_rate_hz();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_channel_count_in() const {
    if (stream_config_in_) {
        return stream_config_in_->num_channels();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_sample_rate_out() const {
    if (stream_config_out_) {
        return stream_config_out_->sample_rate_hz();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_channel_count_out() const {
    if (stream_config_out_) {
        return stream_config_out_->num_channels();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_reverse_sample_rate_in() const {
    if (reverse_stream_config_in_) {
        return reverse_stream_config_in_->sample_rate_hz();
    } else {
        throw std::runtime_error("Reverse stream format not set. Call set_reverse_stream_format() first.");
    }
}

int AudioProcessor::get_reverse_channel_count_in() const {
    if (reverse_stream_config_in_) {
        return reverse_stream_config_in_->num_channels();
    } else {
        throw std::runtime_error("Reverse stream format not set. Call set_reverse_stream_format() first.");
    }
}

int AudioProcessor::get_stream_delay() const {
    return apm_->stream_delay_ms();
}

bool AudioProcessor::aec_enabled() const {
    return config_.echo_canceller.enabled;
}

bool AudioProcessor::ns_enabled() const {
    return config_.noise_suppression.enabled;
}

bool AudioProcessor::agc_enabled() const {
    return config_.gain_controller1.enabled;
}

std::string AudioProcessor::process_stream(const std::string& input) {
    if (!stream_config_in_ || !stream_config_out_) {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
    if (input.empty()) {
        return std::string();
    }

    // calculate expected size
    int frame_size = get_frame_size();
    int total_samples = frame_size * stream_config_in_->num_channels();
    int expected_size = total_samples * sizeof(int16_t);

    if (input.size() != expected_size) {
        throw std::invalid_argument("Input size does not match the expected frame size.");
    }

    // convert string to raw data
    const int16_t* input_data = reinterpret_cast<const int16_t*>(input.data());

    // allocate output
    std::string output(expected_size, '\0');
    int16_t* output_data = reinterpret_cast<int16_t*>(&output[0]);

    // process audio
    int result = apm_->ProcessStream(input_data, *stream_config_in_, *stream_config_out_, output_data);

    if (result != webrtc::AudioProcessing::kNoError) {
        throw std::runtime_error("Error processing audio stream: " + std::to_string(result));
    }

    return output;
}

std::string AudioProcessor::process_reverse_stream(const std::string& input) {
    if (!reverse_stream_config_in_) {
        throw std::runtime_error("Reverse stream format not set. Call set_reverse_stream_format() first.");
    }
    if (input.empty()) {
        return std::string();
    }

    // calculate expected size
    int frame_size = get_frame_size();
    int total_samples = frame_size * reverse_stream_config_in_->num_channels();
    int expected_size = total_samples * sizeof(int16_t);
    if (input.size() != expected_size) {
        throw std::invalid_argument("Input size does not match the expected frame size.");
    }
    
    // convert string to raw data
    const int16_t* input_data = reinterpret_cast<const int16_t*>(input.data());
    
    // allocate output
    std::string output(expected_size, '\0');
    int16_t* output_data = reinterpret_cast<int16_t*>(&output[0]);
    
    // process reverse audio
    int result = apm_->ProcessReverseStream(input_data, *reverse_stream_config_in_, *stream_config_out_, output_data);
    if (result != webrtc::AudioProcessing::kNoError) {
        throw std::runtime_error("Error processing reverse audio stream: " + std::to_string(result));
    }
    
    return output;
}

int AudioProcessor::get_frame_size() const {
    if (!stream_config_in_) {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
    return webrtc::AudioProcessing::GetFrameSize(stream_config_in_->sample_rate_hz());
}

AudioProcessor::~AudioProcessor() {
}
