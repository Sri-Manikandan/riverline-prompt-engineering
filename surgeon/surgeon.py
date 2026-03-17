# This is completely based on few test cases and general flaw detection mechanism.
# It needs to be improved to be more accurate and reliable for real world scenarios.
# Also, when combined with the detective agent, it becomes a self-improving system for improving the system prompt.
# This is a standalone module

import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import json
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from detective.detective import agent_analyzer

with open("../system-prompt.md", "r", encoding="utf-8") as f:
    content = f.read()

with open("../transcripts/call_02.json", "r", encoding="utf-8") as f:
    transcript1 = json.load(f)
    transcript1 = transcript1['transcript']

with open("../transcripts/call_03.json", "r", encoding="utf-8") as f:
    transcript2 = json.load(f)
    transcript2 = transcript2['transcript']

with open("../transcripts/call_07.json", "r", encoding="utf-8") as f:
    transcript3 = json.load(f)
    transcript3 = transcript3['transcript']

with open("../transcripts/call_09.json", "r", encoding="utf-8") as f:
    transcript4 = json.load(f)
    transcript4 = transcript4['transcript']

with open("../transcripts/call_10.json", "r", encoding="utf-8") as f:
    transcript5 = json.load(f)
    transcript5 = transcript5['transcript']

def main():
    st.title("AI Flaw Analysis")
    st.write("This agent helps to analyze the flaws in the system prompt of the AI voice agent that makes debt collection calls for education loans.")
    st.write("It takes the system prompt and the transcripts of the calls and returns the flaws in the system prompt and the fixed system prompt.")
    if "flaws" not in st.session_state:
        st.session_state.flaws = []
    if "fixed_system_prompt" not in st.session_state:
        st.session_state.fixed_system_prompt = ""
    if "resimulated_call1" not in st.session_state:
        st.session_state.resimulated_call1 = ""
    if "resimulated_call2" not in st.session_state:
        st.session_state.resimulated_call2 = ""
    if "resimulated_call3" not in st.session_state:
        st.session_state.resimulated_call3 = ""

    if st.button("Analyze"):
        response = agent_analyzer1()
        st.session_state.flaws = response['structured_response'].flaws_in_system_prompt
        st.session_state.fixed_system_prompt = response['structured_response'].fixed_system_prompt
    st.write("Flaws in system prompt: ")
    for flaw in st.session_state.flaws:
        st.write("- " + flaw)
 
    with open("../system-prompt-fixed.md", "w", encoding="utf-8") as f:
        f.write(st.session_state.fixed_system_prompt)

    st.write("Resimulate calls by clicking the button below after analyzing the flaws")

    if st.button("Resimulate calls"):
        #write it as a string to txt file
        st.session_state.resimulated_call1 = resimulate_call(st.session_state.fixed_system_prompt,transcript1)
        # st.write(st.session_state.resimulated_call["messages"][1])
        with open("../results/resimulated_call_1.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call1["messages"][1].content)

        st.session_state.resimulated_call2 = resimulate_call(st.session_state.fixed_system_prompt,transcript2)
        with open("../results/resimulated_call_2.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call2["messages"][1].content)

        st.session_state.resimulated_call3 = resimulate_call(st.session_state.fixed_system_prompt,transcript3)
        with open("../results/resimulated_call_3.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call3["messages"][1].content)

    if st.button("Before and After Comparisons"):
        before_response = agent_analyzer(transcript1)
        after_response = agent_analyzer(st.session_state.resimulated_call1)
        st.subheader("Transcript 1")
        st.write("Before: ")
        st.write(before_response['structured_response'].agent_score)
        st.write("After: ")
        st.write(after_response['structured_response'].agent_score)

        before_response_2 = agent_analyzer(transcript2)
        after_response_2 = agent_analyzer(st.session_state.resimulated_call2)
        st.subheader("Transcript 2")
        st.write("Before: ")
        st.write(before_response_2['structured_response'].agent_score)
        st.write("After: ")
        st.write(after_response_2['structured_response'].agent_score)

        before_response_3 = agent_analyzer(transcript3)
        after_response_3 = agent_analyzer(st.session_state.resimulated_call3)
        st.subheader("Transcript 3")
        st.write("Before: ")
        st.write(before_response_3['structured_response'].agent_score)
        st.write("After: ")
        st.write(after_response_3['structured_response'].agent_score)
        
# This is completely based on few test cases and general flaw detection mechanism.
# It needs to be improved to be more accurate and reliable for real world scenarios.
# Also, when combined with the detective agent, it becomes a self-improving system for improving the system prompt.
# This is a standalone module

def agent_analyzer1():
    SYSTEM_PROMPT = f"""
    You are a senior Prompt Engineer evaluating an AI voice agent ("Alex")'s System Prompt, that performs debt collection calls for education loans, that helps to find flaws in the system prompt.

    The agent's system prompt is given as:
    {content}

    Your task is to STRICTLY evaluate the flaws in the system prompt and There are at least 3 serious flaws that directly caused failures in the bad calls.
    You will also be given the bad calls transcript.
    Transcript 1:
    {transcript1}
    Transcript 2:
    {transcript2}
    Transcript 3:
    {transcript3}
    Transcript 4:
    {transcript4}
    Transcript 5:
    {transcript5}

    Follow the rules when finding the flaws:
    1. Do not consider personalization of the behavior of the agent as a flaw
    2. Do not consider the agent's tone as a flaw
    3. Do not consider the agent's language switching as a flaw
    4. Do not consider the agent's payment commitment as a flaw
    5. Do not consider the agent's disruptions or audio issues as a flaw
    6. Do not consider the agent's wrong number handling as a flaw
    7. Try to avoid saying you are an AI if the customer asks. (dont consider this as a flaw)

    An example of a flaw would be Identity verification is not performed before disclosing the loan details.

    Your job is to:

    1. Identify what's wrong with the system prompt. Write down each flaw and which transcript proves it.Stick to maximum of 3 serious flaws.
    2. Write a fixed system prompt elimiating the identified flaws, in a markdown format, and also the available functions section should remain the same in the prompt, regardless of the flaws you find.
    """

    model = init_chat_model(
        "gpt-5.4",
        temperature=0
    )

    @dataclass
    class ResponseFormat:
        """Response schema for the agent.
        flaws_in_system_prompt: The flaws in the system prompt and which transcript proves it
        fixed_system_prompt: The fixed system prompt
        """
        flaws_in_system_prompt: list[str]
        fixed_system_prompt: str
        

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        response_format=ResponseFormat,
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "Help me to analyze the system prompt and find the flaws in it and provide the fixed system prompt"}]}
    )
    return response

def resimulate_call(fixed_system_prompt,transcript):
    SYSTEM_PROMPT = f"""
    You are a Expert call simulator for an AI voice agent ("Alex") that performs debt collection calls for education loans.

    The agent's system prompt is given, based on which you have to simulate the call as Alex, as:
    {fixed_system_prompt}

    Your task is to STRICTLY simulate the call as Alex, based on the system prompt given above.
    You can simulate the call based on the transcript given below and respond to the customer's questions:
    Transcript:
    {transcript}

    Your job is to:

    1. Simulate the call as Alex, based on the system prompt given above.
    2. Respond to the customer's questions based on the transcript given below.
    3. You have to output the simulation of the full call in a markdown format, which includes both the customer's response and the agent's response.
    4. You will only simulate the agent's response, not the customer's response and leave the customer's response as it is in the transcript.
    """

    model = init_chat_model(
        "gpt-5.4",
        temperature=0
    )
        

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": "Help me to simulate the call as Alex, based on the system prompt given above and respond to the customer's questions based on the transcript given below"}]}
    )
    return response



if __name__ == "__main__":
    main()