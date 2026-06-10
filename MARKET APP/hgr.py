import cv2
import mediapipe as mp

# --- Setup ---
mp_hands = mp.solutions.hands
mp_draw  = mp.solutions.drawing_utils
hands    = mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7)

# Which landmark IDs are fingertips?
TIPS = [4, 8, 12, 16, 20]  # thumb, index, middle, ring, pinky

def count_fingers(landmarks):
    """Returns how many fingers are up."""
    count = 0
    lm = landmarks.landmark  # list of 21 dots

    # Thumb: compare x (sideways) instead of y
    if lm[TIPS[0]].x < lm[TIPS[0] - 1].x:
        count += 1

    # Other 4 fingers: tip higher (smaller y) than 2 joints below it
    for tip_id in TIPS[1:]:
        if lm[tip_id].y < lm[tip_id - 2].y:
            count += 1

    return count

# --- Main loop ---
cap = cv2.VideoCapture(0)          # open webcam

while True:
    success, frame = cap.read()    # grab one frame
    if not success:
        break

    # Flip so it feels like a mirror
    frame = cv2.flip(frame, 1)

    # MediaPipe needs RGB, OpenCV gives BGR
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_lms in result.multi_hand_landmarks:
            # Draw the skeleton on screen
            mp_draw.draw_landmarks(frame, hand_lms, mp_hands.HAND_CONNECTIONS)

            # Count fingers and show
            fingers = count_fingers(hand_lms)
            gesture = get_gesture(hand_lms)
            cv2.putText(frame, gesture, (10, 60),
            cv2.FONT_HERSHEY_SIMPLEX, 1.4, (0, 255, 100), 3)

    cv2.imshow("Hand Gesture", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # press Q to quit
        break

def get_gesture(landmarks):
    lm = landmarks.landmark

    # Is each finger up? (True/False)
    fingers = [
        lm[8].y  < lm[6].y,   # index
        lm[12].y < lm[10].y,  # middle
        lm[16].y < lm[14].y,  # ring
        lm[20].y < lm[18].y,  # pinky
    ]
    thumb_up = lm[4].x < lm[3].x  # for right hand

    # Match patterns
    if all(fingers):                              return "✋ Open hand"
    if not any(fingers) and not thumb_up:         return "✊ Fist"
    if thumb_up and not any(fingers):             return "👍 Thumbs up"
    if fingers[0] and fingers[1] and not fingers[2] and not fingers[3]: return "✌️ Peace"
    if fingers[0] and not fingers[1] and not fingers[2] and not fingers[3]: return "☝️ One"
    if not fingers[0] and not fingers[1] and not fingers[2] and fingers[3]: return "🤙 Call me"

    return "🤔 Unknown"