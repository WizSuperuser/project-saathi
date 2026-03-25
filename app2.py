import streamlit as st
import pandas as pd
from langchain.llms import OpenAI
import openai
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationSummaryMemory
from langchain.callbacks import get_openai_callback
from langchain.schema import SystemMessage

# Set up OpenAI API key
openai.api_key = ''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

# Initialize LangChain with the provided parameters
llm = OpenAI(temperature=0, model_name="gpt-3.5-turbo-instruct", openai_api_key=openai.api_key)

preamble = """
Act like a college teacher who specializes in guiding students through new concepts and problem-solving techniques. 
Your primary focus is on helping students learn and improve their understanding of academic subjects through a structured hint system. 
For each question, provide hints first, and if the student asks for more help, gradually offer more detailed guidance, 
culminating in a comprehensive solution if necessary. Your objective is to ensure that students have the opportunity to grasp 
the concept and explore different approaches before revealing the complete answer. Emphasize the importance of focusing on studies 
and avoid distractions.
"""

conversation_chain = ConversationChain(llm=llm, memory=ConversationSummaryMemory(llm=llm))
conversation_chain.memory.chat_memory.add_message(SystemMessage(content=preamble))

def get_response_and_questions(chain, query):
    response = chain.run(query)
    questions_prompt = f"Based on the query '{query}', provide 3 probable questions for further understanding:"
    questions = chain.run(questions_prompt)
    return response, questions

def format_response(response, questions):
    questions = [q.strip() for q in questions.split('\n') if q.strip()]
    formatted_response = f"{response}\n\nFor your further understanding, consider the following questions:\n"
    for idx, question in enumerate(questions, 1):
        formatted_response += f"{idx}. {question}\n"
    return formatted_response

# Function to append available time columns
def append_time_column(input_csv_file, available_time_minutes, available_time_days):
    df = pd.read_csv(input_csv_file)
    df['Available time(mins)'] = available_time_minutes
    df['Available days'] = available_time_days
    return df

# Function to generate smart notes using OpenAI
def generate_notes(topic):
        prompt = (f"Create structured notes on the topic '{topic}' with headings, subheadings, "
              f"and content. Make the headings and subheadings bold. Provide simple explanations "
              f"and examples where possible.")
        return llm(prompt)

# Now you can use the generate_notes function
notes = generate_notes("Artificial Intelligence in Healthcare")
print(notes)

# Custom CSS for styling
st.markdown("""
    <style>
    .chat-bubble {
        margin: 10px 0;
        padding: 10px;
        border-radius: 5px;
        background-color: #f1f1f1;
        max-width: 80%;
    }
    .user-chat {
        text-align: right;
        background-color: #e6f7ff;
        margin-left: auto;
    }
    .ai-chat {
        text-align: left;
    }
    .prompt-container {
        margin-top: 20px;
    }
    .prompt {
        display: inline-block;
        padding: 10px;
        margin: 5px;
        background-color: #e0e0e0;
        border-radius: 5px;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.title("WizLearnrAI")
navigation = st.sidebar.radio("Navigation", ["Ask Anything", "Plan Your Learning", "Take Smart Notes", "Get Feedback"])

# Main Content
st.title("WizLearnrAI")

# Ask Anything Section
if navigation == "Ask Anything":
    st.write("## Chat")

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    chat_container = st.container()
    user_input = st.text_input("Type Here", value=st.session_state.get('clicked_prompt', ''))

    if st.button("Send", key="send_button"):
        if user_input:
            # Get response from the AI
            response, questions = get_response_and_questions(conversation_chain, user_input)
            formatted_response = format_response(response, questions)

            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("WizLearnrAI", formatted_response))
            st.session_state.clicked_prompt = ''

    with chat_container:
        for user, msg in st.session_state.chat_history:
            if user == "You":
                st.markdown(f"<div class='chat-bubble user-chat'>{msg}</div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='chat-bubble ai-chat'>{msg}</div>", unsafe_allow_html=True)

    st.write("## Recommended Prompts")
    if st.button("Real-world applications of the law of conservation of momentum in sports", key="prompt_1"):
        st.session_state.clicked_prompt = "Real-world applications of the law of conservation of momentum in sports"
    if st.button("How does the concept change if the collision between the ball and the wall is inelastic?", key="prompt_2"):
        st.session_state.clicked_prompt = "How does the concept change if the collision between the ball and the wall is inelastic?"
    if st.button("Can you explain the concept through analogies in sports like cricket?", key="prompt_3"):
        st.session_state.clicked_prompt = "Can you explain the concept through analogies in sports like cricket?"

# Plan Your Learning Section
elif navigation == "Plan Your Learning":
    st.write("## Plan Your Learning")
    
    # File upload widget
    uploaded_file = st.file_uploader("Upload your course details CSV", type=["csv"])

    if uploaded_file is not None:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)

    # User inputs for available time
    available_time_hours = st.number_input("Enter available time in hours per day:", min_value=0.5, max_value=24.0, value=2.0)
    available_time_days = st.number_input("Enter available time in days:", min_value=1, value=5)
    available_time_minutes_per_day = available_time_hours * 60

    # Load and prepare course data
    df = pd.read_csv('C:/Users/hindv/Downloads/Course.csv')

    def append_time_column(df, available_time_minutes, available_time_days):
        df['Available time(mins)'] = available_time_minutes
        df['Available days'] = available_time_days
        return df

    # Append available time columns
    df = append_time_column(df, available_time_minutes_per_day, available_time_days)

    # Sort the dataframe by time
    df_sorted = df.sort_values(by='time', ascending=False)

    def get_topic_weight(topic):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an assistant that helps assign weights to topics."},
                {"role": "user", "content": f"Assign a relative weight (0 to 1) to the following topic based on its importance and difficulty: {topic}. Respond with only the numerical weight."}
            ]
        )
        return float(response.choices[0].message['content'].strip())

    # Calculate weights for each topic and normalize
    df_sorted['Weight'] = df_sorted['Topic'].apply(get_topic_weight)
    df_sorted['Normalized_Weight'] = df_sorted['Weight'] / df_sorted['Weight'].sum()

    # Allocate the available time to each topic based on the normalized weights
    total_available_time_minutes = available_time_minutes_per_day * available_time_days
    df_sorted['Allocated_Time'] = df_sorted['Normalized_Weight'] * total_available_time_minutes

    # Function to distribute allocated time across available days
    def allocate_time(df, available_time_minutes_per_day):
        allocation_schedule = []
        current_day = 1
        time_left_in_day = available_time_minutes_per_day

        for _, row in df.iterrows():
            allocated_time = row['Allocated_Time']

            while allocated_time > 0:
                if allocated_time <= time_left_in_day:
                    allocation_schedule.append((f"Day {current_day}", row['Topic'], allocated_time))
                    time_left_in_day -= allocated_time
                    allocated_time = 0
                else:
                    allocation_schedule.append((f"Day {current_day}", row['Topic'], time_left_in_day))
                    allocated_time -= time_left_in_day
                    current_day += 1
                    time_left_in_day = available_time_minutes_per_day

        return allocation_schedule

    # Generate and display the learning schedule
    schedule = allocate_time(df_sorted, available_time_minutes_per_day)

    st.write("### Your Learning Schedule:")
    for entry in schedule:
        st.write(f"{entry[0]}: {entry[1]} - {entry[2]:.2f} minute(s)")

    # Save the updated dataframe to a CSV file if needed
    #df_sorted.to_csv('/mnt/data/Updated_Course_details.csv', index=False)


# Take Smart Notes Section
elif navigation == "Take Smart Notes":
    st.write("## Take Smart Notes")

    if 'chat_history_notes' not in st.session_state:
        st.session_state.chat_history_notes = []

    user_input_notes = st.text_input("Type Here", key="user_input_notes")

    if st.button("Send", key="send_notes"):
        if user_input_notes:
            st.session_state.chat_history_notes.append(("You", user_input_notes))
            generated_notes = generate_notes(user_input_notes)
            st.session_state.chat_history_notes.append(("WizLearnrAI", f"Here are the notes I generated on '{user_input_notes}':\n\n{generated_notes}"))

    for user, msg in st.session_state.chat_history_notes:
        if user == "You":
            st.markdown(f"<div class='chat-bubble user-chat'>{msg}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble ai-chat'>{msg}</div>", unsafe_allow_html=True)

# Get Feedback Section
elif navigation == "Get Feedback":
    st.write("## Get Feedback")
    # Implement your feedback logic here
