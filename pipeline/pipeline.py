import streamlit as st
from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
import json

with open("../system-prompt.md", "r", encoding="utf-8") as f:
    system_prompt_old = f.read()

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
    st.title("Entire Pipeline")
    st.write("This module helps to evaluate all the call transcripts and deems it as good and bad along with the agent score and worst agent messages and which in turn, it uses to identify flaws in the system prompt of the agent, and helps in fixing the system prompt according to improve the agent's performance ")
    if 'responses' not in st.session_state:
        st.session_state.responses = []

    if 'fixed_system_prompt' not in st.session_state:
        st.session_state.fixed_system_prompt = ""

    if 'resimulated_call1' not in st.session_state:
        st.session_state.resimulated_call1 = ""
    if 'resimulated_call2' not in st.session_state:
        st.session_state.resimulated_call2 = ""
    if 'resimulated_call3' not in st.session_state:
        st.session_state.resimulated_call3 = ""
    if 'resimulated_call4' not in st.session_state:
        st.session_state.resimulated_call4 = ""
    if 'resimulated_call5' not in st.session_state:
        st.session_state.resimulated_call5 = ""

    if 'resimulated_responses' not in st.session_state:
        st.session_state.resimulated_responses = []
    if 'original_responses' not in st.session_state:
        st.session_state.original_responses = []
    st.subheader("Step 1: Analyzing the call transcripts and deeming it as good and bad")
    with st.sidebar:
        st.title("Upload Transcripts")
        transcripts = st.file_uploader("Upload transcripts", type=["json"], accept_multiple_files=True)
        if transcripts and st.button("Analyze"):
            for transcript in transcripts:
                transcript = json.load(transcript)
                transcript = transcript['transcript']
                response = agent_analyzer(transcript)
                st.session_state.responses.append(response)
    
    for i, response in enumerate(st.session_state.responses):
        st.subheader("Call Transcript:" + str(i+1))
        st.write("Agent Score: " + response['structured_response'].agent_score)
        st.write("Worst Agent Messages: ")
        for message in response['structured_response'].worst_agent_messages:
            st.write("- " + message)
        
        st.write("Verdict: " + response['structured_response'].verdict)
        st.write("--------------------------------")

    #write to a json file
    with open("../results/detective_response.txt", "w", encoding="utf-8") as f:
        f.write(str(st.session_state.responses))

    st.subheader("Step 2: Analyzing the flaws from the bad verdict transcrpits and fixing the system prompt")
    if st.button("Analyze Flaws and fix system prompt"):
        bad_responses = [response for response in st.session_state.responses if response['structured_response'].verdict == "bad"]
        with open("../results/bad_responses.txt", "w", encoding="utf-8") as f:
            f.write(str(bad_responses))

        prompt_analyzer_response = agent_analyzer1(bad_responses)

        flaws = prompt_analyzer_response['structured_response'].flaws_in_system_prompt
        st.session_state.fixed_system_prompt = prompt_analyzer_response['structured_response'].fixed_system_prompt
        st.write("Flaws in system prompt: ")
        for flaw in flaws:
            st.write("- " + flaw)

        with open("../results/flaws.txt", "w", encoding="utf-8") as f:
            f.write(json.dumps(flaws, indent=4))
    
        with open("../system-prompt-fixed.md", "w", encoding="utf-8") as f:
            f.write(st.session_state.fixed_system_prompt)
    
    st.subheader("Step 3: Resimulating the calls with the fixed system prompt")
    if st.button("Resimulate calls"):
        st.session_state.resimulated_call1 = resimulate_call(st.session_state.fixed_system_prompt, transcript1)
        st.session_state.resimulated_call2 = resimulate_call(st.session_state.fixed_system_prompt, transcript2)
        st.session_state.resimulated_call3 = resimulate_call(st.session_state.fixed_system_prompt, transcript3)
        st.session_state.resimulated_call4 = resimulate_call(st.session_state.fixed_system_prompt, transcript4)
        st.session_state.resimulated_call5 = resimulate_call(st.session_state.fixed_system_prompt, transcript5)

        with open("../results/resimulated_call_1.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call1["messages"][1].content)
        with open("../results/resimulated_call_2.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call2["messages"][1].content)
        with open("../results/resimulated_call_3.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call3["messages"][1].content)
        with open("../results/resimulated_call_4.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call4["messages"][1].content)
        with open("../results/resimulated_call_5.txt", "w", encoding="utf-8") as f:
            f.write(st.session_state.resimulated_call5["messages"][1].content)

        st.write("Proceed to next step")

    st.subheader("Step 4: Comparing the resimulated calls with the original calls")
    if st.button("Compare Calls"):
        resimulated_response1 = agent_analyzer(st.session_state.resimulated_call1)
        resimulated_response2 = agent_analyzer(st.session_state.resimulated_call2)
        resimulated_response3 = agent_analyzer(st.session_state.resimulated_call3)
        resimulated_response4 = agent_analyzer(st.session_state.resimulated_call4)
        resimulated_response5 = agent_analyzer(st.session_state.resimulated_call5)
        original_response1 = agent_analyzer(transcript1)
        original_response2 = agent_analyzer(transcript2)
        original_response3 = agent_analyzer(transcript3)
        original_response4 = agent_analyzer(transcript4)
        original_response5 = agent_analyzer(transcript5)

        st.session_state.resimulated_responses = [resimulated_response1, resimulated_response2, resimulated_response3, resimulated_response4, resimulated_response5]
        st.session_state.original_responses = [original_response1, original_response2, original_response3, original_response4, original_response5]

        with open("../results/resimulated_responses.txt", "w", encoding="utf-8") as f:
            f.write(str(st.session_state.resimulated_responses))
        with open("../results/original_responses.txt", "w", encoding="utf-8") as f:
            f.write(str(st.session_state.original_responses))

        st.write("Proceed to next step")

    st.subheader("Step 5: Comparing the resimulated calls score with the original calls score")
    if st.button("Compare Scores"):
        st.subheader("Before")
        for i, response in enumerate(st.session_state.original_responses):
            st.write("Call Transcript: " + str(i+1))
            st.write("Agent Score: " + response['structured_response'].agent_score)
            st.write("Verdict: " + response['structured_response'].verdict)
            st.write("--------------------------------")
    
        st.subheader("After")
        for i, response in enumerate(st.session_state.resimulated_responses):
            st.write("Call Transcript: " + str(i+1))
            st.write("Agent Score: " + response['structured_response'].agent_score)
            st.write("Verdict: " + response['structured_response'].verdict)
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
    1. Whether the agent handles the language switching correctly(medium weightage to the score)(0-10), if no language switching, then full marks
    2. How well the agent handles the disputes(medium weightage to the score)(0-26), if no dispute, then full marks
    3. How well the agent completes each of the 4 phases, if it completes all 4 phases, treat this extra weightage and the execution and handling of the phases are not important(high weightage to the score)(0-27)
    4. Whether the agent makes a payment commitment with the borrower, treat this as a extra weightage if a payment commitment is made(high weightage to the score)(0-17)
    5. How well the agent stays according to the context of the call(medium weightage to the score)(0-10)
    6. it should not be based on audio issues that happen during the call(low weightage to the score)(0-5)
    7. the score and verdict should not be based on the tone and disruptions during the call(low weightage)(0-5)
    8. if the call was identified as a wrong number by the agent, then, this supersedes all other criteria and the verdict should be "good" and the score should be based on it.

    Calculate the score and verdict based on the above criteria and also return the worst agent messages and why it is worst
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
        """
        agent_score: str
        verdict: str
        worst_agent_messages: list[str]

    agent = create_agent(
        model=model,
        system_prompt=SYSTEM_PROMPT,
        response_format=ResponseFormat,
    )

    response = agent.invoke(
        {"messages": [{"role": "user", "content": f"Here is the transcript to analyze: {transcript}"}]},
    )
    return response

def agent_analyzer1(bad_responses):
    SYSTEM_PROMPT = f"""
    You are a senior Prompt Engineer evaluating an AI voice agent ("Alex")'s System Prompt, that performs debt collection calls for education loans, that helps to find flaws in the system prompt.

    The agent's system prompt is given as:
    {system_prompt_old}

    Your task is to STRICTLY evaluate the flaws in the system prompt and There are at least 3 serious flaws that directly caused failures in the bad calls.
    You will also be given the analysis of the bad calls transcripts and the agent messages that were identified as worst and why it was considered worst.
    You can find the flaws based out of it.
    
    Bad calls transcripts analysis:
    {bad_responses}

    Follow the rules when finding the flaws:
    1. Do not consider personalization of the behavior of the agent as a flaw
    2. Try to avoid saying you are an AI if the customer asks. (dont consider this as a flaw)

    Your job is to:

    1. Identify what's wrong with the system prompt. Write down each flaw and which transcript proves it. Stick to a maximum of 3 serious flaws.
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
