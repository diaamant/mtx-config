
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Auth(BaseModel):
    method: Optional[str] = None
    internal_users: Optional[List[Dict[str, Any]]] = Field(default_factory=list)

class RTSP(BaseModel):
    protocols: Optional[List[str]] = Field(default_factory=list)
    encryption: Optional[str] = None
    rtp_ip: Optional[str] = Field(alias="rtpIp", default=None)
    rtcp_ip: Optional[str] = Field(alias="rtcpIp", default=None)
    # Add all other RTSP fields here

class WebRTC(BaseModel):
    ice_servers2: Optional[List[Dict[str, Any]]] = Field(alias="iceServers2", default_factory=list)
    # Add all other WebRTC fields here

class HLS(BaseModel):
    variant: Optional[str] = None
    segment_count: Optional[int] = Field(alias="segmentCount", default=None)
    # Add all other HLS fields here

class RTMP(BaseModel):
    encryption: Optional[str] = None
    # Add all other RTMP fields here

class SRT(BaseModel):
    pass # Add SRT fields if any

class PathDefaults(BaseModel):
    source: Optional[str] = None
    # Add all other PathDefaults fields here

class App(BaseModel):
    log_level: Optional[str] = Field(alias="logLevel", default="info")
    external_authentication_url: Optional[str] = Field(alias="externalAuthenticationURL", default=None)
    # Add all other App fields here

class Path(BaseModel):
    source: Optional[str] = None
    run_on_demand: Optional[str] = Field(alias="runOnDemand", default=None)
    run_on_demand_restart: Optional[bool] = Field(alias="runOnDemandRestart", default=False)
    run_on_demand_start_timeout: Optional[str] = Field(alias="runOnDemandStartTimeout", default=None)
    # Add all other Path fields here

class ConfigStructure(BaseModel):
    auth: Optional[Auth] = None
    rtsp: Optional[RTSP] = None
    webrtc: Optional[WebRTC] = None
    hls: Optional[HLS] = None
    rtmp: Optional[RTMP] = None
    srt: Optional[SRT] = None
    path_defaults: Optional[PathDefaults] = Field(alias="pathDefaults", default=None)
    app: Optional[App] = None
    paths: Optional[Dict[str, Path]] = Field(default_factory=dict)

MODEL_MAPPING = {
    "auth.json": Auth,
    "values_rtsp.json": RTSP,
    "values_webrtc.json": WebRTC,
    "values_hls.json": HLS,
    "values_rtmp.json": RTMP,
    "values_srt.json": SRT,
    "values_pathDefaults.json": PathDefaults,
    "values_app.json": App,
    "paths.json": Dict[str, Path]
}
