# Tab names mapping
TAB_NAMES = {
    "values_app.json": "App",
    "auth.json": "Auth",
    "values_rtsp.json": "RTSP",
    "values_webrtc.json": "WebRTC",
    "values_hls.json": "HLS",
    "values_rtmp.json": "RTMP",
    "values_srt.json": "SRT",
    "values_pathDefaults.json": "Path Defaults",
    "paths.json": "Paths",
    "preview": "Preview",
}

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
