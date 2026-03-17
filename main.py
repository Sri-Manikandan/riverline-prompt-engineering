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
    responses = []  

    with st.sidebar:
        st.title("Upload Transcripts")
        transcripts = st.file_uploader("Upload transcripts", type=["json"], accept_multiple_files=True)
        if transcripts and st.button("Analyze"):
            for transcript in transcripts:
                transcript = json.load(transcript)
                transcript = transcript['transcript']
                response = agent_analyzer(transcript)
                responses.append(response)

    for response in responses:
        st.write("Agent Score: " + response['structured_response'].agent_score)
        # st.write("Worst Agent Messages: ")
        # for message in response['structured_response'].worst_agent_messages:
        #     st.write("- " + message)
        
        st.write("Verdict: " + response['structured_response'].verdict)
        st.write("Summary: "+ response['structured_response'].summary)
        st.write("--------------------------------")



def agent_analyzer(transcript):
    SYSTEM_PROMPT = f"""
    You are a senior Call Quality Analyst evaluating an AI voice agent ("Alex") that performs debt collection calls for education loans.

    You will be given:

    1. The agent's full system prompt (global + phase-specific rules)
    2. A call transcript between the agent and a borrower

    Your task is to STRICTLY evaluate how well the agent handled the call.
    
    The agent talks to real borrowers across 4 phases: Opening → Discovery → Negotiation → Closing. It can call functions to switch phases, schedule callbacks, switch languages, and end calls.
    
    Your response should output for each transcript:
    A score (0-100)
    Which specific agent messages were the worst and why
    A verdict: "good" or "bad"

    The score and verdict are based on the following criteria:
    1. Whether the agent handles the language switching correctly(medium weightage to the score)(0-15), if no language switching, then full marks
    2. How well the agent handles the disputes(medium weightage to the score)(0-15), if no dispute, then full marks
    3. How well the agent completes each of the 4 phases, if it completes all 4 phases, treat this extra weightage and the execution and handling of the phases are not important(high weightage to the score)(0-30)
    4. Whether the agent makes a payment commitment with the borrower, treat this as a extra weightage if a payment commitment is made(high weightage to the score)(0-20)
    5. How well the agent stays according to the context of the call(medium weightage to the score)(0-10)
    6. it should not be based on audio issues that happen during the call(low weightage to the score)(0-5)
    7. the score and verdict should not be based on the tone and disruptions during the call(low weightage)(0-5)

    Calculate the score and verdict based on the above criteria and also return the summary of the analysis in 2-3 lines.
    """


    model = init_chat_model(
        "gpt-5.4",
        temperature=0
    )

    @dataclass
    class ResponseFormat:
        """Response schema for the agent.
        agent_score: The score of the agent's performance
        worst_agent_messages: The worst agent messages and why, keep it short and concise
        verdict: The verdict: "good" or "bad"
        summary: A concise 2-4 sentence audit summary
        """
        agent_score: str
        verdict: str
        worst_agent_messages: list[dict[str, str]]
        summary: str

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        response_format=ResponseFormat,
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": f"Here is the transcript to analyze: {transcript}"}]},
    )
    return response

if __name__ == "__main__":
    main()