"""Tests for Pydantic models."""
import pytest
from pydantic import ValidationError

from src.models import StreamConfig, PathsConfig, AuthConfig, RTSPConfig


class TestStreamConfig:
    """Tests for StreamConfig model."""
    
    def test_valid_source_stream(self):
        """Test creating a valid source-based stream."""
        config = StreamConfig(
            source="rtsp://192.168.1.1:554/stream",
            rtspTransport="tcp",
            sourceOnDemand=True
        )
        assert config.source == "rtsp://192.168.1.1:554/stream"
        assert config.rtspTransport == "tcp"
        assert config.sourceOnDemand is True
    
    def test_valid_run_on_demand_stream(self):
        """Test creating a valid runOnDemand stream."""
        config = StreamConfig(
            runOnDemand="ffmpeg -i input output",
            runOnDemandRestart=True,
            runOnDemandStartTimeout="10s"
        )
        assert config.runOnDemand == "ffmpeg -i input output"
        assert config.runOnDemandRestart is True
        assert config.runOnDemandStartTimeout == "10s"
    
    def test_invalid_timeout_format(self):
        """Test that invalid timeout format raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StreamConfig(
                runOnDemand="ffmpeg",
                runOnDemandStartTimeout="invalid"
            )
        assert "Timeout must be in format" in str(exc_info.value)
    
    def test_valid_timeout_formats(self):
        """Test valid timeout formats."""
        for timeout in ["10s", "5m", "1h", "999s"]:
            config = StreamConfig(runOnDemandStartTimeout=timeout)
            assert config.runOnDemandStartTimeout == timeout
    
    def test_invalid_source_url(self):
        """Test that invalid source URL raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            StreamConfig(source="invalid-url")
        assert "valid RTSP/RTMP/HTTP URL" in str(exc_info.value)
    
    def test_valid_source_urls(self):
        """Test valid source URL formats."""
        valid_urls = [
            "rtsp://example.com",
            "rtmp://example.com",
            "rtsps://example.com",
            "rtmps://example.com",
            "http://example.com",
            "https://example.com"
        ]
        for url in valid_urls:
            config = StreamConfig(source=url)
            assert config.source == url
    
    def test_invalid_rtsp_transport(self):
        """Test that invalid rtspTransport raises ValidationError."""
        with pytest.raises(ValidationError):
            StreamConfig(rtspTransport="invalid")
    
    def test_valid_rtsp_transports(self):
        """Test valid rtspTransport values."""
        for transport in ["udp", "tcp", "auto"]:
            config = StreamConfig(rtspTransport=transport)
            assert config.rtspTransport == transport
    
    def test_extra_fields_allowed(self):
        """Test that extra fields are allowed."""
        config = StreamConfig(
            source="rtsp://test",
            customField="customValue"
        )
        assert config.model_extra.get("customField") == "customValue"


class TestPathsConfig:
    """Tests for PathsConfig model."""
    
    def test_add_stream(self):
        """Test adding a stream."""
        paths = PathsConfig()
        paths.add_stream("stream1", {
            "source": "rtsp://test",
            "rtspTransport": "tcp"
        })
        assert "stream1" in paths.paths
        assert paths.paths["stream1"].source == "rtsp://test"
    
    def test_remove_stream(self):
        """Test removing a stream."""
        paths = PathsConfig()
        paths.add_stream("stream1", {"source": "rtsp://test"})
        paths.remove_stream("stream1")
        assert "stream1" not in paths.paths
    
    def test_get_stream(self):
        """Test getting a stream."""
        paths = PathsConfig()
        paths.add_stream("stream1", {"source": "rtsp://test"})
        stream = paths.get_stream("stream1")
        assert stream is not None
        assert stream.source == "rtsp://test"
    
    def test_get_nonexistent_stream(self):
        """Test getting a non-existent stream returns None."""
        paths = PathsConfig()
        stream = paths.get_stream("nonexistent")
        assert stream is None
    
    def test_to_dict(self):
        """Test converting to dictionary."""
        paths = PathsConfig()
        paths.add_stream("stream1", {
            "source": "rtsp://test",
            "rtspTransport": "tcp",
            "sourceOnDemand": True
        })
        result = paths.to_dict()
        assert isinstance(result, dict)
        assert "stream1" in result
        assert result["stream1"]["source"] == "rtsp://test"


class TestAuthConfig:
    """Tests for AuthConfig model."""
    
    def test_valid_auth_methods(self):
        """Test valid authentication methods."""
        for method in ["internal", "jwt", "http"]:
            config = AuthConfig(authMethod=method)
            assert config.authMethod == method
    
    def test_invalid_auth_method(self):
        """Test invalid authentication method raises ValidationError."""
        with pytest.raises(ValidationError):
            AuthConfig(authMethod="invalid")
    
    def test_with_internal_users(self):
        """Test with internal users."""
        users = [{"user": "admin", "pass": "password"}]
        config = AuthConfig(authMethod="internal", authInternalUsers=users)
        assert config.authInternalUsers == users


class TestRTSPConfig:
    """Tests for RTSPConfig model."""
    
    def test_valid_rtsp_address(self):
        """Test valid RTSP address format."""
        config = RTSPConfig(rtspAddress=":8554")
        assert config.rtspAddress == ":8554"
        
        config = RTSPConfig(rtspAddress="localhost:8554")
        assert config.rtspAddress == "localhost:8554"
    
    def test_invalid_rtsp_address(self):
        """Test invalid RTSP address format."""
        with pytest.raises(ValidationError):
            RTSPConfig(rtspAddress="invalid")
    
    def test_valid_encryption_values(self):
        """Test valid encryption values."""
        for encryption in ["no", "optional", "strict"]:
            config = RTSPConfig(rtspEncryption=encryption)
            assert config.rtspEncryption == encryption
    
    def test_invalid_encryption_value(self):
        """Test invalid encryption value."""
        with pytest.raises(ValidationError):
            RTSPConfig(rtspEncryption="invalid")
