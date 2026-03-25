import urllib.parse
import streamlit as st
import google.generativeai as genai
import os
from streamlit_mic_recorder import mic_recorder

# Add a voice recorder button in the sidebar or main page
audio = mic_recorder(
    start_prompt="🎤 Start Speaking",
    stop_prompt="🛑 Stop Recording",
    key='recorder'
)

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
        "system_instruction": "You must act as a supportive community health worker (like an ASHA worker). Validate First: Acknowledge their pain with empathy (e.g., 'I’m so sorry you’ve been dealing with these aches for so long...'). Offer Common Causes: Mention 2-3 non-scary possibilities first (e.g., fatigue could be due to anemia, lack of rest, or the summer heat). Layered Discovery: Do not overwhelm with questions. Ask only 1-2 focused questions (e.g., 'Does the pain increase when you are working?' or 'How is your appetite lately?'). Subtle Safety Check: Gently mention that if the pain moves to the jaw or chest, it's important to let you know. Cultural Value: End with a simple home remedy suggestion (e.g., Ginger tea or a piece of Jaggery)."
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
        "system_instruction": "तुम्ही एका मदतीला धावणाऱ्या आरोग्य सेविकेप्रमाणे (आशा वर्करप्रमाणे) संवाद साधावा. आस्थेवाईक चौकशी: सर्वात आधी त्यांच्या त्रासाची दखल घेऊन त्यांना धीर द्या (उदा: 'अरेरे, खूप दिवसांपासून हे अंगदुखी सहन करत आहात का...'). साधी कारणे: घाबरवून न टाकता काही सामान्य कारणे सांगा (उदा: थकवा हा अशक्तपणा, पुरेशी विश्रांती न मिळणे किंवा उन्हाळ्यामुळे देखील असू शकतो). मोजके प्रश्न: एकाच वेळी अनेक प्रश्न विचारू नका. फक्त १-२ महत्त्वाचे प्रश्न विचारा (उदा: 'काम करताना त्रास वाढतो का?' किंवा 'जेवण वेळेवर जातंय का?'). सुचक इशारा: जर वेदना जबड्यापर्यंत किंवा छातीपर्यंत जात असतील, तर ते सांगणे महत्त्वाचे आहे असे हळुवारपणे सांगा. घरगुती उपाय: संवादाच्या शेवटी एखादा साधा घरगुती उपाय (उदा. गुळाचा खडा) सुचवा."
    },
    "తెలుగు": {
        "title": "WizLearnr: మహిళల ఆరోగ్య స్క్రీనింగ్",
        "header": "ఈరోజు మీ ఆరోగ్యం ఎలా ఉంది?",
        "disclaimer": "గమనిక: ఇది ప్రాథమిక తనిఖీ కోసం మాత్రమే. అత్యవసర పరిస్థితిలో ఆసుపత్రికి వెళ్లండి.",
        "input_placeholder": "మీ లక్షణాలను వివరించండి...",
        "age_label": "మీ వయస్సును నమోదు చేయండి",
        "remedy_label": "సంప్రదాయ చికిత్సలు చేర్చాలా?",
        "system_instruction": "మీరు ఒక ఆత్మీయమైన ఆరోగ్య సహాయకురాలిగా (ASHA worker వలె) మాట్లాడాలి. 1. ముందస్తుగా వారి బాధను గుర్తించి ఓదార్పునివ్వండి (ఉదా: 'అయ్యో, చాలా కాలంగా నొప్పులతో ఇబ్బంది పడుతున్నారా..'). 2. భయపెట్టకుండా సాధారణ కారణాలను చెప్పండి (ఉదా: నీరసం అనేది రక్తహీనత, తగినంత విశ్రాంతి లేకపోవడం లేదా ఎండ ప్రభావం వల్ల కూడా రావచ్చు). 3. ఒకేసారి అన్ని ప్రశ్నలు అడగకండి. కేవలం 1-2 ముఖ్యమైన ప్రశ్నలు మాత్రమే అడగండి (ఉదా: 'పని చేస్తున్నప్పుడు నొప్పి పెరుగుతుందా?' లేదా 'ఆకలి సరిగ్గా వేస్తోందా?'). 4. ఒకవేళ నొప్పులు దవడకు లేదా ఛాతీకి పాకితే అది ముఖ్యం అని సున్నితంగా చెప్పండి. 5. సంభాషణ చివరలో చిన్న ఇంటి చిట్కా (బెల్లం ముక్క) సూచించండి."
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

# --- 6. SUMMARY FOR DOCTOR ---
DOCTOR_SUMMARY_PROMPT = """
Summarize the above conversation for a medical professional in 3-4 bullet points.
Include:
1. Patient Age and Primary Complaint.
2. Duration of symptoms.
3. Presence or absence of 'Red Flags' (Chest pain, Jaw pain, Breathlessness on exertion).
4. Any traditional remedies already tried.
Keep it strictly clinical and brief.
"""

if st.button("📋 Generate Summary for Doctor"):
    # Combine the chat history for context
    chat_context = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages])
    
    # Call Gemini to summarize
    model = genai.GenerativeModel('gemini-2.5-flash')
    summary_response = model.generate_content(f"{chat_context}\n\n{DOCTOR_SUMMARY_PROMPT}")
    summary_text = summary_response.text
    
    st.subheader("Doctor's Note (Ready to Copy)")
    st.code(summary_text)
    
    #Create a WhatsApp Link
    encoded_text = urllib.parse.quote(summary_text)
    whatsapp_url = f"https://wa.me/?text={encoded_text}"
    
    #Professional Action Button
    st.link_button("📲 Send to Doctor via WhatsApp", whatsapp_url, type="primary", use_container_width=True)

# --- 7. VOICE MODE ---
if audio:
    # 'audio' contains the raw bytes of the recording
    audio_bytes = audio['bytes']
    
    # 1. Send the audio bytes to Gemini
    # Gemini can "hear" the audio and understand the language automatically
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # We pass the system prompt + the audio file
    response = model.generate_content([
        st.session_state.system_prompt,
        {"mime_type": "audio/wav", "data": audio_bytes}
    ])
    
    # 2. Display the AI's response as if it were a text chat
    st.session_state.messages.append({"role": "assistant", "content": response.text})
    st.rerun()
