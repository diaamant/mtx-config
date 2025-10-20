import json
import yaml
from pathlib import Path

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


# ---------------------------------------------


def pop_keys_to_dict(source_dict, keys_list):
    """
    Извлекает (с удалением) ключи из source_dict в новый словарь.
    """
    new_dict = {}
    for key in keys_list:
        if key in source_dict:
            new_dict[key] = source_dict.pop(key)
    return new_dict


def save_json_data(data, file_path):
    """
    Сохраняет данные в .json файл, если данные не пустые.
    """
    if not data:
        print(f"Нет данных для {file_path.name}, файл не создан.")
        return
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Успешно сохранен: {file_path}")
    except Exception as e:
        print(f"ОШИБКА сохранения {file_path}: {e}")


def main():
    # 1. Определение путей
    # Предполагаем, что main.py лежит в <project_root>/src/
    # а mediamtx01.yml лежит в <project_root>/work/
    base_dir = Path(__file__).parent.parent
    config_file_path = base_dir / "work/mediamtx01.yml"

    # Новый каталог для вывода
    output_dir = base_dir / "work/json/"

    # Создаем директорию, если ее нет
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Читаем файл конфигурации: {config_file_path}")
    print(f"Сохраняем JSON в директорию: {output_dir}\n")

    try:
        # 2. Чтение и парсинг YAML
        with open(config_file_path, "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        if not config_data:
            print("Файл пуст или не является корректным YAML.")
            return

        print("Файл успешно прочитан. Начинаем разделение данных...")

        # 3. Разделение данных

        # 3a. Извлекаем 'paths' (это вложенный словарь)
        paths_data = config_data.pop("paths", None)

        # 3b. Извлекаем 'pathDefaults' (это вложенный словарь)
        path_defaults_data = config_data.pop("pathDefaults", None)

        # 3c. Извлекаем группы ключей
        auth_data = pop_keys_to_dict(config_data, AUTH_KEYS)
        rtsp_data = pop_keys_to_dict(config_data, RTSP_KEYS)
        webrtc_data = pop_keys_to_dict(config_data, WEBRTC_KEYS)
        hls_data = pop_keys_to_dict(config_data, HLS_KEYS)
        rtmp_data = pop_keys_to_dict(config_data, RTMP_KEYS)
        srt_data = pop_keys_to_dict(config_data, SRT_KEYS)

        # 3d. Все, что осталось - это 'values_app'
        app_data = config_data

        print("\nРазделение завершено. Начинаем сохранение файлов...")

        # 4. Сохранение результатов в JSON файлы
        save_json_data(paths_data, output_dir / "paths.json")
        save_json_data(auth_data, output_dir / "auth.json")
        save_json_data(path_defaults_data, output_dir / "values_pathDefaults.json")
        save_json_data(rtsp_data, output_dir / "values_rtsp.json")
        save_json_data(webrtc_data, output_dir / "values_webrtc.json")
        save_json_data(hls_data, output_dir / "values_hls.json")
        save_json_data(rtmp_data, output_dir / "values_rtmp.json")
        save_json_data(srt_data, output_dir / "values_srt.json")
        save_json_data(app_data, output_dir / "values_app.json")

        print("\nЗадача выполнена.")

    except FileNotFoundError:
        print(f"ОШИБКА: Файл не найден по пути: {config_file_path}")
    except yaml.YAMLError as e:
        print(f"ОШИБКА: Не удалось распарсить YAML файл: {e}")
    except Exception as e:
        print(f"ОШИБКА: Произошла непредвиденная ошибка: {e}")


if __name__ == "__main__":
    main()
