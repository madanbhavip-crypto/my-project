import cv2
import mediapipe as mp
import time
import numpy as np
import random
import winsound  # Built-in Windows audio system

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7,
    max_num_hands=1
)

# --- RE-APPLYING STABLE DIRECTSHOW BACKEND ---
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not cap.isOpened():
    print("Camera not detected!")
    exit()

# Force MJPEG properties to prevent backend hanging
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
# ---------------------------------------------
def get_finger_template(hand_landmarks, handedness):
    fingers = []
    label = handedness.classification[0].label
    
    # Thumb
    thumb_tip = hand_landmarks.landmark[4].x
    thumb_ip = hand_landmarks.landmark[3].x
    if label == "Left":
        fingers.append(1 if thumb_tip > thumb_ip else 0)
    else:
        fingers.append(1 if thumb_tip < thumb_ip else 0)

    # Other 4 fingers
    tips = [8, 12, 16, 20]
    pips = [6, 10, 14, 18]
    for tip, pip in zip(tips, pips):
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y:
            fingers.append(1)
        else:
            fingers.append(0)
    return fingers

class Particle:
    def __init__(self, x, y, spell_type, vx=None, vy=None):
        self.x = x
        self.y = y
        self.size = random.randint(4, 8)
        self.life = 1.0
        self.decay = random.uniform(0.02, 0.06)
        self.spell_type = spell_type
        
        # Physics vectors
        if vx is not None and vy is not None:
            self.vx = vx + random.uniform(-2, 2)
            self.vy = vy + random.uniform(-2, 2)
        else:
            self.vx = random.uniform(-3, 3)
            self.vy = random.uniform(-3, 3)

    def update(self):
        self.x += self.vx
        self.y += self.vy
        if self.spell_type == "FLIPENDO":
            self.vy += 0.2  # Gravity pulling air dust down
        else:
            self.vy -= 0.1  # Floating elements
        self.life -= self.decay

    def draw(self, img):
        if self.life <= 0: return
        alpha_color = (255, 255, 255)
        if self.spell_type == "FIREBALL":
            alpha_color = (0, random.randint(100, 200), 255)
        elif self.spell_type == "FLIPENDO":
            alpha_color = (255, 180, 100) # Wind blue-white
        elif self.spell_type == "AVADA":
            alpha_color = (0, 255, 0) # Deadly green
            
        cv2.circle(img, (int(self.x), int(self.y)), int(self.size), alpha_color, -1)

# System Arrays & Motion Trackers
particles = []
motion_trail = []
prev_pos = None
prev_time = time.time()

# Spell States
current_spell = "None"
casted_spell = "None"
spell_count = 0
charge_pitch = 400

while True:
    success, frame = cap.read()
    if not success: break

    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape
    overlay = frame.copy()
    
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    detected_spell = "None"
    idx_pt = None
    velocity = 0
    vx, vy = 0, 0

    if results.multi_hand_landmarks and results.multi_handedness:
        hand_landmarks = results.multi_hand_landmarks[0]
        handedness = results.multi_handedness[0]
        finger_pattern = get_finger_template(hand_landmarks, handedness)
        
        # Focus on index tip for tracking paths
        index_tip = hand_landmarks.landmark[8]
        idx_pt = (int(index_tip.x * w), int(index_tip.y * h))
        
        # Append to a fading motion trail
        motion_trail.append(idx_pt)
        if len(motion_trail) > 15:  # Keep last 15 positions
            motion_trail.pop(0)

        # --- LEVEL 4 VELOCITY CALCULATIONS ---
        curr_time = time.time()
        dt = curr_time - prev_time
        if prev_pos is not None and dt > 0:
            vx = (idx_pt[0] - prev_pos[0]) / dt
            vy = (idx_pt[1] - prev_pos[1]) / dt
            velocity = np.sqrt(vx**2 + vy**2) # Total speed in pixels/sec
            
        prev_pos = idx_pt
        prev_time = curr_time

        # --- ADVANCED GESTURE ARRAYS ---
        if finger_pattern == [0, 1, 0, 0, 0]:
            # If moving slowly, it's just a raw stance
            if velocity < 1500:
                detected_spell = "WAND READY"
            # LEVEL 4 MOTION TRIGGER: Quick slashing motion with finger raised
            else:
                detected_spell = "FLIPENDO"
        elif finger_pattern == [0, 1, 1, 0, 0]:
            detected_spell = "FIREBALL"
        elif finger_pattern == [1, 1, 0, 0, 1]:  # Forbidden Dark Magic Stance
            detected_spell = "AVADA"

    else:
        prev_pos = None
        if len(motion_trail) > 0:
            motion_trail.pop(0)

    # --- RENDER MOTION TRAILS ---
    for i in range(1, len(motion_trail)):
        thickness = int(np.sqrt(15 / float(i + 1)) * 2.5)
        cv2.line(frame, motion_trail[i - 1], motion_trail[i], (0, 255, 255), thickness)

    # --- CASTING PHYSICS & RETRO AUDIO FREQUENCIES ---
    if detected_spell != "None":
        if detected_spell in ["FIREBALL", "AVADA"]:
            # Gradual synthetic charge up sounds
            charge_pitch = min(charge_pitch + 15, 1200)
            winsound.Beep(int(charge_pitch), 20)  # Asynchronous short audio burst
            
            if idx_pt:
                for _ in range(3):
                    particles.append(Particle(idx_pt[0], idx_pt[1], detected_spell))
                    
        elif detected_spell == "FLIPENDO" and casted_spell != "FLIPENDO":
            # Instant blast sound effect
            winsound.Beep(800, 80)
            winsound.Beep(400, 100)
            casted_spell = "FLIPENDO"
            spell_count += 1
            
            # Fire particles violently in the direction of your physical hand movement!
            if idx_pt:
                for _ in range(30):
                    particles.append(Particle(idx_pt[0], idx_pt[1], "FLIPENDO", vx * 0.02, vy * 0.02))
                    
        if detected_spell == "WAND READY":
            charge_pitch = 400  # Reset sound pitch
            
    # Update and Draw System Particles
    for p in particles[:]:
        p.update()
        if p.life <= 0:
            particles.remove(p)
        else:
            p.draw(frame)

    # --- ADVANCED CYBERPUNK HUD ---
    cv2.rectangle(frame, (0, 0), (w, 85), (10, 10, 10), cv2.FILLED)
    cv2.line(frame, (0, 85), (w, 85), (255, 0, 150), 2)
    
    cv2.putText(frame, f"VELOCITY: {int(velocity)} px/s", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (100, 255, 100), 1)
    cv2.putText(frame, f"ACTION: {detected_spell}", (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (245, 245, 245), 2)
    
    # Glow text effect for Casted Spells
    cv2.putText(frame, f"ACTIVE: {casted_spell}", (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
    cv2.putText(frame, f"SPELL COUNT: {spell_count}", (w - 190, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

    cv2.imshow("Arcade Spell Engine - Level 4", frame)
    if cv2.waitKey(1) & 0xFF == 27: break

cap.release()
cv2.destroyAllWindows()