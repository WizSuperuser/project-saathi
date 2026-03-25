import streamlit as st
import google.generativeai as genai
import os

# --- 1. CONFIGURATION & SECURITY ---
# Securely fetch API Key (Cloud Run sets this as an environment variable)
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("API Key not found. Please set the GEMINI_API_KEY environment variable.")

# --- 2. MULTILINGUAL UI STRINGS ---
LANG_DATA = {
    "English": {
        "title": "WizLearnr: Women's Health Triage",
        "header": "How are you feeling today?",
        "disclaimer": "Note: This is a screening tool, not a doctor. In emergencies, go to the hospital.",
        "input_placeholder": "Describe your symptoms...",
        "age_label": "Enter your Age",
        "remedy_label": "Include Traditional Care?",
        "system_instruction": "You are a professional, empathetic medical assistant. Focus on atypical symptoms in women (jaw pain, fatigue, nausea as cardiac signs). Use a discovery-first approach. For low-risk, suggest safe Indian home remedies (Ajwain, Shunti, Haldi)."
    },
    "हिंदी": {
        "title": "WizLearnr: महिला स्वास्थ्य स्क्रीनिंग",
        "header": "आज आपकी तबीयत कैसी है?",
        "disclaimer": "नोट: यह केवल एक स्क्रीनिंग टूल है। आपातकालीन स्थिति में तुरंत अस्पताल जाएं।",
        "input_placeholder": "अपने लक्षणों के बारे में बताएं...",
        "age_label": "अपनी उम्र दर्ज करें",
        "remedy_label": "पारंपरिक उपचार शामिल करें?",
        "system_instruction": "आप एक पेशेवर मेडिकल सहायक हैं। महिलाओं में असामान्य लक्षणों (जैसे हृदय की समस्याओं के लिए जबड़े का दर्द या थकान) पर ध्यान दें। पहले सवाल पूछें, फिर सलाह दें। कम जोखिम वाले मामलों में घरेलू नुस्खे (अजवाइन, हल्दी) बताएं।"
    },
    "मराठी": {
        "title": "WizLearnr: महिला आरोग्य तपासणी",
        "header": "आज तुम्हाला कसे वाटत आहे?",
        "disclaimer": "टीप: हे केवळ प्राथमिक तपासणी साधन आहे. आणीबाणीच्या वेळी रुग्णालयात जा.",
        "input_placeholder": "तुमची लक्षणे सांगा...",
        "age_label": "तुमचे वय सांगा",
        "remedy_label": "पारंपारिक उपाय समाविष्ट करायचे का?",
        "system_instruction": "तुम्ही एक अनुभवी वैद्यकीय सहाय्यक आहात. महिलांमधील 'असामान्य' लक्षणांकडे (उदा. हृदयाच्या त्रासासाठी पाठदुखी किंवा थकवा) जाणीवपूर्वक लक्ष द्या. कमी जोखमीच्या तक्रारींसाठी घरगुती उपाय सुचवा."
    },
    "తెలుగు": {
        "title": "WizLearnr: మహిళల ఆరోగ్య స్క్రీనింగ్",
        "header": "ఈరోజు మీ ఆరోగ్యం ఎలా ఉంది?",
        "disclaimer": "గమనిక: ఇది ప్రాథమిక తనిఖీ కోసం మాత్రమే. అత్యవసర పరిస్థితిలో ఆసుపత్రికి వెళ్లండి.",
        "input_placeholder": "మీ లక్షణాలను వివరించండి...",
        "age_label": "మీ వయస్సును నమోదు చేయండి",
        "remedy_label": "సంప్రదాయ చికిత్సలు చేర్చాలా?",
        "system_instruction": "మీరు మహిళల ఆరోగ్య సహాయకులు. మహిళల్లో వచ్చే అసాధారణ లక్షణాలపై (గుండె సమస్యలకు దవడ నొప్పి లేదా అలసట) ప్రత్యేక శ్రద్ధ వహించండి. తక్కువ ప్రమాదం ఉన్నప్పుడు ఇంటి వైద్యం (వాము, శొంఠి) సూచించండి."
    }
}

# --- 3. SYMPTOM LEXICON (Internal Discovery Aid) ---
SYMPTOM_LEXICON = {
    "Cardiac": ["Ghabrahat", "Bechaini", "Chhati mein bhari-pan", "Aayasam", "Gunde lo manta", "Jaw pain", "Vennu noppi"],
    "Anemia": ["Kamzori", "Ashaktpana", "Nirusam", "Kallu thirugutunnayi", "Chakkar"],
    "Respiratory": ["Dum lagna", "Aayasam", "Oopiri aadakapovadam"],
    "Gastric": ["Vakara", "Potta noppi", "Bloating", "Vamu", "Ajwain"]
}

# --- 4. STREAMLIT UI SETUP ---
st.set_page_config(page_title="WizLearnr Triage", page_icon="🩺", layout="centered")

# Language Selection Buttons (Top of Page)
col1, col2, col3, col4 = st.columns(4)
with col1: 
    if st.button("English"): st.session_state.lang = "English"
with col2:
    if st.button("हिंदी"): st.session_state.lang = "हिंदी"
with col3:
    if st.button("मराठी"): st.session_state.lang = "मराठी"
with col4:
    if st.button("తెలుగు"): st.session_state.lang = "తెలుగు"

if 'lang' not in st.session_state: st.session_state.lang = "English"
L = LANG_DATA[st.session_state.lang]

st.title(L["title"])
st.write(f"### {L['header']}")
st.caption(L["disclaimer"])

# Sidebar Context
with st.sidebar:
    age = st.number_input(L["age_label"], min_value=1, max_value=120, value=25)
    remedy_on = st.toggle(L["remedy_label"], value=True)

# --- 5. CHAT LOGIC ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input(L["input_placeholder"]):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Call Gemini 1.5 Flash
    with st.chat_message("assistant"):
        try:
            model = genai.GenerativeModel("gemini-2.5-flash")
            
            # Construct Context
            context = f"{L['system_instruction']} User Age: {age}. Traditional remedies enabled: {remedy_on}."
            full_prompt = f"System: {context}\n\nUser: {prompt}\nAssistant:"
            
            response = model.generate_content(full_prompt)
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Error: {e}")
