import streamlit as st
from streamlit_webrtc import webrtc_streamer, RTCConfiguration, VideoTransformerBase

import cv2
import numpy as np

# Corrected direct URL of your background image
background_image_url = 'https://live.staticflickr.com/65535/53597581524_260942e41a_b.jpg'


class ObjectFocusTransformer(VideoTransformerBase):
    def transform(self, frame):
        img = frame.to_ndarray(format="bgr24")

        # Simple color detection for demonstration (detecting a blue object)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Define the range of blue color in HSV
        lower_blue = np.array([100,150,50])
        upper_blue = np.array([140,255,255])
        mask = cv2.inRange(hsv, lower_blue, upper_blue)
        # Find contours to detect objects
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            # Optionally, filter out small objects by area
            area = cv2.contourArea(contour)
            if area > 500:  # Min area threshold
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)

        return img

# Configuring RTC
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

# Inject CSS for the background image using a placeholder
background_placeholder = st.empty()
background_placeholder.markdown(f"""
<style>
.stApp {{
    background-image: url({background_image_url});
    background-size: cover; /* Try changing this to 'contain' or '100% 100%' to see which works better for you */
    background-position: center; /* This ensures the image is centered */
    background-repeat: no-repeat; /* Prevents the image from repeating */
}}
</style>
""", unsafe_allow_html=True)

# Define the categorization function
def categorize_waste_simple(user_input):
    categories = {
        "plastic": ["plastic", "bottle", "polyethylene", "polypropylene", "packaging"],
        "food": ["food", "peel", "leftover", "fruit", "vegetable", "meat", "banana peel", "bread", "compost", "rice", "banana", "coffee", "coffee grounds", "juice","apple" ],
        "paper": ["paper", "cardboard", "newspaper", "magazine", "book", "note", "envelope"]
    }
    for category, keywords in categories.items():
        if any(keyword in user_input for keyword in keywords):
            return category
    return "paper"  # Default to paper if no other category matches

# Define a callback function to update UI based on user input
def update_category():
    user_input = st.session_state.user_input.lower()
    category = categorize_waste_simple(user_input)
    # Update the UI elements or state variables here
    # Note: Implement necessary updates based on categorization

# Define button styling and logic
def create_button(label, background_color, emoji, disabled=False, highlight=False):
    glow_class = "glow_effect" if highlight else ""
    disabled_attribute = "disabled" if disabled else ""
    button_html = f"""
        <button class='styled_button {glow_class}' style='background-color: {background_color};' {disabled_attribute}>
            {emoji} {label}
        </button>
    """
    return button_html

# Global style for buttons and glowing effect
button_container_style = """
<style>
    .button_container {
        display: flex;
        gap: 10px;
        justify-content: start;
        flex-wrap: wrap;
    }
    .styled_button {
        background-color: #4CAF50;
        border: none;
        color: white;
        padding: 16px 32px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 20px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 12px;
        transition: box-shadow 0.3s ease;
    }
    .styled_button:hover {
        background-color: #45a049;
    }
    .glow_effect {
        box-shadow: 0 0 30px #EE4B2B;
    }
</style>
"""

# Streamlit application UI
st.title('UCD Waste Ninja 🥷')

st.header("Describe Your Trash")
user_input = st.text_input("What are you disposing of?", key="user_input", on_change=update_category)

# Categorize user input
category = categorize_waste_simple(user_input.lower())

# Apply styles
st.markdown(button_container_style, unsafe_allow_html=True)
st.markdown("<div class='button_container'>", unsafe_allow_html=True)

# Generate and display buttons with conditional highlighting
buttons_html = (
    create_button('Paper', 'black', '📄', disabled=False, highlight=(category == "paper")) +
    create_button('Plastic', 'blue', '♻️', disabled=False, highlight=(category == "plastic")) +
    create_button('Food', 'brown', '🍎', disabled=False, highlight=(category == "food"))
)

st.markdown(buttons_html, unsafe_allow_html=True)
st.markdown("</div>", unsafe_allow_html=True)

st.header("Or, Show Us Your Trash")
# Configuring RTC
RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

webrtc_streamer(key="trash-webcam", rtc_configuration=RTC_CONFIGURATION, 
                media_stream_constraints={"video": True}, 
                video_transformer_factory=ObjectFocusTransformer)
