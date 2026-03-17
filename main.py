import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import json

with open("system-prompt.md", "r", encoding="utf-8") as f:
    content = f.read()

def main():
    st.title("AI Call Analyzer")
    st.write("This is a tool that analyzes the performance of an AI voice agent that makes debt collection calls for education loans.")
    st.write("It takes a transcript of a call and scores the agent's performance based on how well they handled the call.")
    st.write("It also returns the worst agent messages and why.")
    st.write("It also returns a verdict: 'good' or 'bad'.")

    if "responses" not in st.session_state:
        st.session_state.responses = []

    with st.sidebar:
        st.title("Upload Transcripts")
        transcripts = st.file_uploader("Upload transcripts", type=["json"], accept_multiple_files=True)
        if transcripts and st.button("Analyze"):
            for transcript in transcripts:
                transcript = json.load(transcript)
                transcript = transcript['transcript']
                response = agent_analyzer(transcript)
                st.session_state.responses.append(response)

    for response in st.session_state.responses:
        st.write("Agent Score: " + response['structured_response'].agent_score)
        st.write("Worst Agent Messages: ")
        for message in response['structured_response'].worst_agent_messages:
            st.write("- " + message)
        st.write("Verdict: " + response['structured_response'].verdict)
        st.write("--------------------------------")


def agent_analyzer(transcript):
    SYSTEM_PROMPT = f"""You are an expert in analyzing the call transcript and scoring the agent's performance based on how well they handled the call.
    You will be receiving the transcript of a call made by an AI voice agent that makes debt collection calls for education loans. It calls borrowers, explains their outstanding amount, and tries to help them pay or settle.

    ------------------------------------------------------------
    The agent runs on a system prompt: \n{content}\n
    
    ------------------------------------------------------------
    Rules:
    You need to score the agent's performance based on how well they handled the call.
    You need to return a score between 0 and 100, which agent messages were the worst and why, and a verdict: "good" or "bad".
    If the agent's performance is good, the score should be between 60 and 100.
    If the agent's performance is bad, the score should be between 0 and 60.
    ------------------------------------------------------------
    """


    model = init_chat_model(
        "gpt-5.2",
        temperature=0
    )

    @dataclass
    class ResponseFormat:
        """Response schema for the agent.
        agent_score: The score of the agent's performance
        worst_agent_messages: The worst agent messages and why, keep it short and concise
        verdict: The verdict: "good" or "bad"
        """
        # The score of the agent's performance
        agent_score: str
        # The worst agent messages and why
        worst_agent_messages: list[str]
        # The verdict: "good" or "bad"
        verdict: str

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        response_format=ResponseFormat,
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": f"Help me to analyze the given transcript {transcript} and return the score, the worst agent messages and the verdict."}]},
    )
    return response

if __name__ == "__main__":
    main()