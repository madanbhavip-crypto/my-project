import streamlit as st
import serial
import numpy as np
import joblib
import time

# --- CONFIGURATION ---
PORT = 'COM3'  # Update this to your ESP32 port
MODEL_PATH = 'gesture_model_sunday.pkl'
SCALER_PATH = 'scaler_sunday.pkl'

# Load model and scaler
@st.cache_resource
def load_assets():
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    return model, scaler

def extract_features(rows):
    # Normalise each gesture to remove amplitude differences
    rows = (rows - rows.mean(axis=0)) / (rows.std(axis=0) + 1e-8)
    
    features = []
    for col in range(6):
        s = rows[:, col]
        features += [np.mean(s), np.std(s), np.min(s), np.max(s),
                     np.max(s)-np.min(s), np.sqrt(np.mean(s**2))]
    
    for col in range(6):
        s = rows[:, col]
        features.append(np.mean(np.abs(np.diff(s))))
    
    return features  # 42 features total
# --- UI LAYOUT ---
st.set_page_config(page_title="IEEE - SJCE: Air Digit Calculator")
st.title("IEEE - SJCE: Air Digit Calculator")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.info("**Instructions:**\n1. Hold button hardware setup.\n2. Draw digit or sign in the air.\n3. Release button.\n4. Draw `=` to calculate.")
    status_indicator = st.empty()
    status_indicator.warning("Offline: Press Start below.")

with col2:
    st.subheader("Current Expression")
    expression_display = st.empty()
    expression_display.code("Ready to calculate...", language="text")
    
    st.subheader("Result")
    result_display = st.empty()

# --- MAIN LOGIC ---
if st.button("Start Calculator"):
    model, scaler = load_assets()
    
    try:
        ser = serial.Serial(PORT, 115200, timeout=0.1)
        status_indicator.success(f"Connected to {PORT}")
        
        current_expr = ""
        rows_buffer = []
        in_gesture = False
        
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            
            if line == 'IDLE':
                if in_gesture and len(rows_buffer) >= 5:
                    in_gesture = False
                    # Process Gesture
                    feat = np.array(extract_features(np.array(rows_buffer))).reshape(1, -1)
                    pred = model.predict(scaler.transform(feat))[0]
                    
                    # Map Prediction
                    SYMBOL = {'plus': '+', 'minus': '-', 'multiply': '*', 'divide': '/', 'equals': '='}
                    symbol = SYMBOL.get(pred, str(pred))
                    
                    if symbol == '=':
                        try:
                            # Use lstrip to prevent leading zero errors in Python eval
                            sanitized_expr = " ".join([term.lstrip('0') if term.isdigit() else term for term in current_expr.split()])
                            res = eval(sanitized_expr)
                            result_display.success(f"Result: {res}")
                        except Exception as e:
                            result_display.error(f"Error: {e}")
                        current_expr = "" 
                    else:
                        current_expr += f" {symbol} " if not symbol.isdigit() else symbol
                    
                    expression_display.code(current_expr if current_expr else "0", language="text")
                    rows_buffer = []
                else:
                    in_gesture = False
                    rows_buffer = []

            elif ',' in line:
                if not in_gesture:
                    in_gesture = True
                    rows_buffer = []
                try:
                    rows_buffer.append(list(map(float, line.split(','))))
                except:
                    pass
            
            # Briefly sleep to allow Streamlit to update the UI
            time.sleep(0.01)

    except Exception as e:
        st.error(f"Connection Error: {e}")
