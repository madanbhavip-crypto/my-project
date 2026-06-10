import cv2
import mediapipe as mp
import math
import numpy as np
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- Volume setup (works with all pycaw versions) ---
devices = AudioUtilities.GetSpeakers()
activate = devices._dev.Activate(           # <-- _dev is the fix
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None
)
volume = cast(activate, POINTER(IAudioEndpointVolume))
vol_range = volume.GetVolumeRange()
min_vol, max_vol = vol_range[0], vol_range[1]

# --- MediaPipe setup ---
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands(min_detection_confidence=0.7)

cap = cv2.VideoCapture(0)
w, h = 640, 480

while True:
    success, frame = cap.read()
    if not success:
        break

    frame  = cv2.flip(frame, 1)
    rgb    = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_lms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)
            lm = hand_lms.landmark

            x1 = int(lm[4].x * w);  y1 = int(lm[4].y * h)
            x2 = int(lm[8].x * w);  y2 = int(lm[8].y * h)

            cv2.circle(frame, (x1, y1), 10, (255, 0, 255), -1)
            cv2.circle(frame, (x2, y2), 10, (255, 0, 255), -1)
            cv2.line(frame,   (x1, y1), (x2, y2), (255, 0, 255), 3)

            distance    = math.hypot(x2 - x1, y2 - y1)
            vol         = np.interp(distance, [30, 200], [min_vol, max_vol])
            vol_percent = np.interp(distance, [30, 200], [0, 100])

            volume.SetMasterVolumeLevel(vol, None)

            bar_h = int(np.interp(vol_percent, [0, 100], [400, 150]))
            cv2.rectangle(frame, (50, 150), (80, 400), (200, 200, 200), 2)
            cv2.rectangle(frame, (50, bar_h), (80, 400), (0, 255, 0), -1)
            cv2.putText(frame, f"Vol: {int(vol_percent)}%", (40, 430),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    cv2.imshow("Volume Control", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()