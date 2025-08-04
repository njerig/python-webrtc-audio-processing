from webrtc_audio_processing import AudioProcessor as AP
import pytest

def test_constructor():
    ap = AP(enable_aec=True, enable_ns=True, enable_agc=True)
    assert ap is not None, "AudioProcessor instance should not be None"

def test_set_stream_format():
    ap = AP(enable_aec=True, enable_ns=True, enable_agc=True)

    ap.set_stream_format(48000, 1)
    assert ap.get_sample_rate_in() == 48000, "Sample rate should be set to 48000"
    assert ap.get_channel_count_in() == 1, "Number of channels should be set to 1"
    assert ap.get_sample_rate_out() == 48000, "Output sample rate should match input sample rate"
    assert ap.get_channel_count_out() == 1, "Output channel count should match input channel count"

    ap.set_stream_format(32000, 2, 30000, 1)
    assert ap.get_sample_rate_in() == 32000, "Sample rate should be set to 32000"
    assert ap.get_channel_count_in() == 2, "Number of channels should be set to 2"
    assert ap.get_sample_rate_out() == 30000, "Output sample rate should be set to 30000"
    assert ap.get_channel_count_out() == 1, "Output channel count should be set to 1"
    
    with pytest.raises(RuntimeError):
        ap.set_stream_format(0, 1), "Setting sample rate to 0 should raise ValueError"
    with pytest.raises(RuntimeError):
        ap.set_stream_format(48000, 0), "Setting channel count to 0 should raise ValueError"


def test_set_reverse_stream_format():
    ap = AP(enable_aec=True, enable_ns=True, enable_agc=True)
    
    ap.set_reverse_stream_format(48000, 1)
    assert ap.get_reverse_sample_rate_in() == 48000, "Reverse sample rate should be set to 48000"
    assert ap.get_reverse_channel_count_in() == 1, "Reverse channel count should be set to 1"
    
    with pytest.raises(RuntimeError):
        ap.set_reverse_stream_format(0, 1), "Setting reverse sample rate to 0 should raise ValueError"
    with pytest.raises(RuntimeError):
        ap.set_reverse_stream_format(48000, 0), "Setting reverse channel count to 0 should raise ValueError"