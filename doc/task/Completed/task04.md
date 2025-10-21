# План дальнейшего развития Mediamtx Configuration Editor

**Дата:** 2025-10-21  
**Версия:** 0.3.4

---

## Введение

Этот документ определяет следующие шаги по улучшению проекта.

---

## 1. Высокий приоритет (P1) - Следующий спринт

### 1.1. Улучшение UI/UX
- **Задача:** Провести рефакторинг path_tab.py.	
	- добавить возможность изменения данных аутентификации 
	- Уточнение: необходимо скорректировать данные user:password в config_manager.data.'paths.json' типа 'runOnDemand' в соответствии с данными пользователя c 'auth.json'
	'runOnDemand': gst-launch-1.0 pulsesrc device=alsa_input.usb-0c76_USB_PnP_Audio_Device-00.mono-fallback do-timestamp=true volume=1.0 buffer-time=2000000 ! queue name=audio_source  audio_source. ! audio/x-raw, channels=1, rate=48000 ! queue ! audioconvert ! queue ! audioresample ! audio/x-raw, channels=1, rate=24000 ! queue ! opusenc bandwidth=1104 bitrate=64000 bitrate-type=1 inband-fec=FALSE packet-loss-percentage=0 dtx=FALSE ! queue ! opusparse ! queue ! sink. urisourcebin uri="rtsp://unit057:1KZez0Vo7Cid@127.0.0.1:$RTSP_PORT/vh" ! queue ! application/x-rtp,media=video ! queue ! parsebin ! queue ! h264parse ! queue ! sink. rtspclientsink name=sink location=rtsp://unit057:1KZez0Vo7Cid@localhost:$RTSP_PORT/avh
	- ввести поля замены аутентификационной пары: unit057:1KZez0Vo7Cid -> unit058:dsgfdgtrhyj




