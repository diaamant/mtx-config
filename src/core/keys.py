# Tab names mapping

NAMES_TAB = {
    "APP": "app",
    "AUTH": "auth",
    "RTSP": "rtsp",
    "WEBRTC": "webrtc",
    "HLS": "hls",
    "RTMP": "rtmp",
    "SRT": "srt",
    "PATH_DEFAULTS": "pathDefaults",
    "PATHS": "paths",
    "Preview": "preview",
}

TAB_NAMES = {v: k for k, v in NAMES_TAB.items()}

# --- СПИСКИ КЛЮЧЕЙ ДЛЯ РАЗДЕЛЕНИЯ ---
# Ключи, относящиеся к аутентификации
AUTH_KEYS = [
    "authMethod",
    "authInternalUsers",
    "authHTTPAddress",
    "authHTTPExclude",
    "authJWTJWKS",
    "authJWTJWKSFingerprint",
    "authJWTClaimKey",
    "authJWTExclude",
    "authJWTInHTTPQuery",
]

# Ключи, относящиеся к RTSP
RTSP_KEYS = [
    "rtsp",
    "rtspTransports",
    "rtspEncryption",
    "rtspAddress",
    "rtspsAddress",
    "rtpAddress",
    "rtcpAddress",
    "multicastIPRange",
    "multicastRTPPort",
    "multicastRTCPPort",
    "multicastSRTPPort",
    "multicastSRTCPPort",
    "rtspServerKey",
    "rtspServerCert",
    "rtspAuthMethods",
    "rtspUDPReadBufferSize",
]

# Ключи, относящиеся к WebRTC
WEBRTC_KEYS = [
    "webrtc",
    "webrtcAddress",
    "webrtcEncryption",
    "webrtcServerKey",
    "webrtcServerCert",
    "webrtcAllowOrigin",
    "webrtcTrustedProxies",
    "webrtcLocalUDPAddress",
    "webrtcLocalTCPAddress",
    "webrtcIPsFromInterfaces",
    "webrtcIPsFromInterfacesList",
    "webrtcAdditionalHosts",
    "webrtcICEServers2",
    "webrtcHandshakeTimeout",
    "webrtcTrackGatherTimeout",
    "webrtcSTUNGatherTimeout",
]

# Ключи, относящиеся к HLS
HLS_KEYS = [
    "hls",
    "hlsAddress",
    "hlsEncryption",
    "hlsServerKey",
    "hlsServerCert",
    "hlsAllowOrigin",
    "hlsTrustedProxies",
    "hlsAlwaysRemux",
    "hlsVariant",
    "hlsSegmentCount",
    "hlsSegmentDuration",
    "hlsPartDuration",
    "hlsSegmentMaxSize",
    "hlsDirectory",
    "hlsMuxerCloseAfter",
]

# Ключи, относящиеся к RTMP
RTMP_KEYS = [
    "rtmp",
    "rtmpAddress",
    "rtmpEncryption",
    "rtmpsAddress",
    "rtmpServerKey",
    "rtmpServerCert",
]

# Ключи, относящиеся к SRT
SRT_KEYS = [
    "srt",
    "srtAddress",
    "srtpAddress",
    "srtcpAddress",
]


TAB_KEYS = {
    "AUTH": AUTH_KEYS,
    "RTSP": RTSP_KEYS,
    "WEBRTC": WEBRTC_KEYS,
    "HLS": HLS_KEYS,
    "RTMP": RTMP_KEYS,
    "SRT": SRT_KEYS,
    "PATH_DEFAULTS": "pathDefaults",
    "PATHS": "paths",
}
