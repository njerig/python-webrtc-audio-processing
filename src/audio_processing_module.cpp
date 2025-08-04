#include "audio_processing_module.h"

#include "webrtc/api/audio/audio_processing.h"
#include "webrtc/api/scoped_refptr.h"


AudioProcessor::AudioProcessor(bool enable_aec,
                               bool enable_ns,
                               bool enable_agc,
                               bool enable_vad) 
    : enable_aec_(enable_aec),
      enable_ns_(enable_ns),
      enable_agc_(enable_agc),
      enable_vad_(enable_vad),
      initialized_(false) {
    apm_ = webrtc::AudioProcessingBuilder().Create();

    // initialize echo cancelling
    config_.echo_canceller.enabled = enable_aec_;
    config_.echo_canceller.mobile_mode = false;

    // initialize noise suppression
    config_.noise_suppression.enabled = enable_ns_;
    config_.noise_suppression.level = webrtc::AudioProcessing::Config::NoiseSuppression::Level::kModerate;

    // initialize automatic gain control
    config_.gain_controller1.enabled = enable_agc_;
    config_.gain_controller1.mode = webrtc::AudioProcessing::Config::GainController1::Mode::kAdaptiveDigital;

    apm_->ApplyConfig(config_);

    processing_config_ = std::make_unique<webrtc::ProcessingConfig>();
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

    processing_config_->input_stream().set_sample_rate_hz(sample_rate_in);
    processing_config_->input_stream().set_num_channels(channel_count_in);
    // default to input sample rate and channel count if not specified
    if (sample_rate_out == -1) {
        sample_rate_out = sample_rate_in;
    }
    if (channel_count_out == -1) {
        channel_count_out = channel_count_in;
    }
    processing_config_->output_stream().set_sample_rate_hz(sample_rate_out);
    processing_config_->output_stream().set_num_channels(channel_count_out);

}

void AudioProcessor::set_reverse_stream_format(int sample_rate_in,
                                               int channel_count_in) {

    if (sample_rate_in < 8000 || sample_rate_in > 384000) {
        throw std::invalid_argument("Sample rate must be between 8000 and 384000 Hz.");
    }
    if (channel_count_in < 1) {
        throw std::invalid_argument("Number of channels must be at least 1.");
    }

    processing_config_->reverse_input_stream().set_sample_rate_hz(sample_rate_in);
    processing_config_->reverse_input_stream().set_num_channels(channel_count_in);
}

int AudioProcessor::get_sample_rate_in() const {
    if (processing_config_->input_stream().sample_rate_hz() > 0) {
        return processing_config_->input_stream().sample_rate_hz();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_channel_count_in() const {
    if (processing_config_->input_stream().num_channels() > 0) {
        return processing_config_->input_stream().num_channels();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_sample_rate_out() const {
    if (processing_config_->output_stream().sample_rate_hz() > 0) {
        return processing_config_->output_stream().sample_rate_hz();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_channel_count_out() const {
    if (processing_config_->output_stream().num_channels() > 0) {
        return processing_config_->output_stream().num_channels();
    } else {
        throw std::runtime_error("Stream format not set. Call set_stream_format() first.");
    }
}

int AudioProcessor::get_reverse_sample_rate_in() const {
    if (processing_config_->reverse_input_stream().sample_rate_hz() > 0) {
        return processing_config_->reverse_input_stream().sample_rate_hz();
    } else {
        throw std::runtime_error("Reverse stream format not set. Call set_reverse_stream_format() first.");
    }
}

int AudioProcessor::get_reverse_channel_count_in() const {
    if (processing_config_->reverse_input_stream().num_channels() > 0) {
        return processing_config_->reverse_input_stream().num_channels();
    } else {
        throw std::runtime_error("Reverse stream format not set. Call set_reverse_stream_format() first.");
    }
}

AudioProcessor::~AudioProcessor() {
}
