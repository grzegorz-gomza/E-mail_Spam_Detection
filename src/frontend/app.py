import streamlit as st
import requests
import json

# --- App config & titles ---
st.set_page_config(page_title="Spam Detector")
st.title("📧 Spam Detector Dashboard")
st.write("Enter the email text below to predict whether it is **Spam** or **Not Spam**.")

# --- Input ---
email = st.text_area("Email to predict", height=150, max_chars=2000)

# --- Prediction logic ---
def predict_email(email_text):
    url = "http://backend.docker:8000/predict"
    headers = {'Content-Type': 'application/json'}
    data = {"email": email_text}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=10)
        response.raise_for_status()
        result = response.json()
        # Expecting something like: {"prediction": "spam", "confidence": 0.98}
        return result
    except requests.exceptions.RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "Invalid response from server"}

# --- UI: Prediction button and output ---
if st.button('🚀 Predict Spam/Not Spam'):
    if not email.strip():
        st.warning("Please enter an email for prediction.")
    else:
        with st.spinner("Analyzing..."):
            result = predict_email(email)
        if "error" in result:
            st.error(result["error"])
        else:
            prediction = result.get("prediction", "unknown").capitalize()
            confidence = result.get("confidence")
            color = "red" if prediction.lower() == "spam" else "green"
            st.markdown(
                f"### Result: <span style='color:{color}'>{prediction}</span>", unsafe_allow_html=True
            )
            if confidence is not None:
                st.write(f"**Confidence:** {confidence*100:.2f}%")
