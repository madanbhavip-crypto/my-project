import cv2
import mediapipe as mp
import numpy as np

# MediaPipe setup
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

mp_draw = mp.solutions.drawing_utils

# Webcam
cap = cv2.VideoCapture(0)

# Canvas
canvas = np.zeros((480, 640, 3), dtype=np.uint8)

# Colors
RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
BLACK = (0, 0, 0)

draw_color = BLUE
brush_thickness = 5
eraser_thickness = 30

prev_x, prev_y = 0, 0


def fingers_up(hand_landmarks):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    # Thumb
    fingers.append(
        hand_landmarks.landmark[tips[0]].x >
        hand_landmarks.landmark[tips[0] - 1].x
    )

    # Other fingers
    for tip in tips[1:]:
        fingers.append(
            hand_landmarks.landmark[tip].y <
            hand_landmarks.landmark[tip - 2].y
        )

    return fingers


while True:

    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    # Toolbar
    cv2.rectangle(frame, (0, 0), (100, 60), RED, -1)
    cv2.rectangle(frame, (100, 0), (200, 60), GREEN, -1)
    cv2.rectangle(frame, (200, 0), (300, 60), BLUE, -1)
    cv2.rectangle(frame, (300, 0), (400, 60), (50, 50, 50), -1)

    cv2.putText(frame, "ERASE",
                (315, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2)

    if results.multi_hand_landmarks:

        hand_landmarks = results.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        finger_state = fingers_up(hand_landmarks)

        index_x = int(hand_landmarks.landmark[8].x * w)
        index_y = int(hand_landmarks.landmark[8].y * h)

        middle_x = int(hand_landmarks.landmark[12].x * w)
        middle_y = int(hand_landmarks.landmark[12].y * h)

        # Open palm -> Clear canvas
        if all(finger_state):
            canvas = np.zeros((480, 640, 3), dtype=np.uint8)

        # Selection Mode (Index + Middle)
        elif finger_state[1] and finger_state[2]:

            prev_x, prev_y = 0, 0

            cv2.circle(frame, (index_x, index_y),
                       12, (255, 255, 255), -1)

            if index_y < 60:

                if 0 < index_x < 100:
                    draw_color = RED

                elif 100 < index_x < 200:
                    draw_color = GREEN

                elif 200 < index_x < 300:
                    draw_color = BLUE

                elif 300 < index_x < 400:
                    draw_color = BLACK

        # Drawing Mode (Only Index Finger)
        elif finger_state[1] and not finger_state[2]:

            cv2.circle(frame,
                       (index_x, index_y),
                       10,
                       draw_color,
                       -1)

            if prev_x == 0 and prev_y == 0:
                prev_x, prev_y = index_x, index_y

            thickness = (
                eraser_thickness
                if draw_color == BLACK
                else brush_thickness
            )

            cv2.line(canvas,
                     (prev_x, prev_y),
                     (index_x, index_y),
                     draw_color,
                     thickness)

            prev_x, prev_y = index_x, index_y

    else:
        prev_x, prev_y = 0, 0

    # Merge drawing with frame
    gray_canvas = cv2.cvtColor(canvas, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(
        gray_canvas,
        20,
        255,
        cv2.THRESH_BINARY
    )

    mask_inv = cv2.bitwise_not(mask)

    frame_bg = cv2.bitwise_and(
        frame,
        frame,
        mask=mask_inv
    )

    canvas_fg = cv2.bitwise_and(
        canvas,
        canvas,
        mask=mask
    )

    output = cv2.add(frame_bg, canvas_fg)

    cv2.putText(output,
                "Open Palm = Clear",
                (420, 90),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 255, 255),
                2)

    cv2.imshow("AI Virtual Painter", output)

    key = cv2.waitKey(1)

    if key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()