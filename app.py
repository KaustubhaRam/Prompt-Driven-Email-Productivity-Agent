import streamlit as st
import json
import os
import time
from typing import List, Dict, Any

USE_DUMMY_LLM = True 


MOCK_INBOX = [
    {
        "id": "e1",
        "sender": "alice@work.com",
        "subject": "Project Sync: Weekly standup",
        "body": "Hi team,\nCan we move the weekly standup from 10am to 11am on Tuesday?\nThanks,\nAlice",
        "timestamp": "2025-11-10 09:12"
    },
    {
        "id": "e2",
        "sender": "newsletter@technews.com",
        "subject": "This week's tech roundup",
        "body": "Your weekly digest: AI, cloud, and developer tools.",
        "timestamp": "2025-11-09 08:00"
    },
    {
        "id": "e3",
        "sender": "bob@partner.org",
        "subject": "Request: Updated architecture diagram",
        "body": "Could you share the updated system architecture diagram and the list of services to be migrated by Dec 1?",
        "timestamp": "2025-11-11 14:20"
    },
    {
        "id": "e4",
        "sender": "spam@offers.xyz",
        "subject": "You won a prize! Click here",
        "body": "Congratulations! Claim your prize now by replying with your details.",
        "timestamp": "2025-11-08 22:01"
    },
    {
        "id": "e5",
        "sender": "carol@hr.com",
        "subject": "Complete your compliance training",
        "body": "Hello,\nPlease complete the mandatory compliance training by November 20.\n- HR",
        "timestamp": "2025-11-07 11:30"
    },
    {
        "id": "e6",
        "sender": "dave@client.com",
        "subject": "Meeting request: Product demo",
        "body": "Hi,\nWould you be available next Thursday for a 45-minute product demo?",
        "timestamp": "2025-11-12 16:45"
    },
    {
        "id": "e7",
        "sender": "alerts@service.com",
        "subject": "Your service invoice is ready",
        "body": "Invoice for October is available. Total: $120. Due: Nov 25.",
        "timestamp": "2025-11-05 07:15"
    },
    {
        "id": "e8",
        "sender": "ellen@pm.com",
        "subject": "Can you review PR #452?",
        "body": "I've pushed the changes. Could you review PR #452 and merge it?",
        "timestamp": "2025-11-12 09:33"
    },
    {
        "id": "e9",
        "sender": "friend@example.com",
        "subject": "Weekend plans",
        "body": "Hey! Are you free this weekend for hiking?",
        "timestamp": "2025-11-13 20:00"
    },
    {
        "id": "e10",
        "sender": "ops@infra.com",
        "subject": "Incident: DB latency spike",
        "body": "DB cluster us-east-1 had high latency between 01:30 and 01:50.",
        "timestamp": "2025-11-14 02:10"
    },
    {
        "id": "e11",
        "sender": "recruiter@jobs.com",
        "subject": "Interview invitation",
        "body": "We'd like to schedule a first-round interview next week.",
        "timestamp": "2025-11-15 13:00"
    },
    {
        "id": "e12",
        "sender": "newsletter@health.com",
        "subject": "5 Tips to boost wellbeing",
        "body": "Short reads: hydration, sleep, microbreaks.",
        "timestamp": "2025-11-01 06:40"
    }
]



DEFAULT_PROMPTS = {
    "categorization": "Categorize this email as: Important, Newsletter, Spam, To-Do, Meeting, Invoice.",
    "action_extraction": "Extract tasks from this email. If none, return [].",
    "auto_reply": "Generate a short polite reply to this email."
}



def call_llm(prompt: str):
    text = prompt.lower()

    if "prize" in text or "won" in text:
        return "Spam"
    if "newsletter" in text or "digest" in text:
        return "Newsletter"
    if "invoice" in text or "due" in text:
        return "Invoice"
    if "meeting" in text or "request" in text or "demo" in text:
        return "Meeting"
    if "please" in text or "could you" in text or "share" in text:
        return "To-Do"

    return "Important"


def llm_extract_actions(body: str):
    body = body.lower()
    actions = []

    if "share" in body and "diagram" in body:
        actions.append({"task": "Share updated architecture diagram", "deadline": "2025-12-01"})

    if "complete" in body and "training" in body:
        actions.append({"task": "Complete compliance training", "deadline": "2025-11-20"})

    if "review" in body and "pr" in body:
        actions.append({"task": "Review PR #452", "deadline": ""})

    return actions


def llm_autoreply(email):
    subject = "Re: " + email["subject"]

    if "meeting" in email["subject"].lower():
        body = "Hi, thanks for your message. I am available on Thursday 11 AM or Friday 2 PM."
    if "prize" in email["subject"].lower():
        body=" "
    else:
        body = "Hi, thanks for the update. I will get back to you shortly."

    return {"subject": subject, "body": body}



PROMPT_FILE = "prompts.json"
PROCESSED_FILE = "processed.json"
DRAFTS_FILE = "drafts.json"


def load(file, default):
    if os.path.exists(file):
        try:
            return json.load(open(file))
        except:
            return default
    return default


def save(file, data):
    json.dump(data, open(file, "w"), indent=2)





st.set_page_config(page_title="Email Productivity Agent", layout="wide")

if "prompts" not in st.session_state:
    st.session_state.prompts = load(PROMPT_FILE, DEFAULT_PROMPTS)

if "processed" not in st.session_state:
    st.session_state.processed = load(PROCESSED_FILE, {})

if "drafts" not in st.session_state:
    st.session_state.drafts = load(DRAFTS_FILE, {})



left, right = st.columns([1, 2])

with left:
    st.title(" Prompt Brain")

    st.session_state.prompts["categorization"] = st.text_area(
        "Categorization Prompt", st.session_state.prompts["categorization"], height=90
    )

    st.session_state.prompts["action_extraction"] = st.text_area(
        "Action Extraction Prompt", st.session_state.prompts["action_extraction"], height=100
    )

    st.session_state.prompts["auto_reply"] = st.text_area(
        "Auto-Reply Prompt", st.session_state.prompts["auto_reply"], height=100
    )

    if st.button("Save Prompts"):
        save(PROMPT_FILE, st.session_state.prompts)
        st.success("Prompts saved!")

    st.markdown("###  Run Ingestion")

    if st.button("Process Inbox"):
        for email in MOCK_INBOX:
            eid = email["id"]

            category = call_llm(email["subject"] + email["body"])
            actions = llm_extract_actions(email["body"])
            draft = llm_autoreply(email)

            st.session_state.processed[eid] = {
                "category": category,
                "actions": actions,
                "draft": draft,
            }

            time.sleep(0.1)

        save(PROCESSED_FILE, st.session_state.processed)
        st.success("Inbox processed!")

with right:
    st.title(" Inbox")

    for email in MOCK_INBOX:
        if st.button(email["subject"], key=email["id"]):
            st.session_state["selected"] = email["id"]

    if "selected" in st.session_state:
        eid = st.session_state["selected"]
        email = next(e for e in MOCK_INBOX if e["id"] == eid)

        st.subheader(email["subject"])
        st.write(f"**From:** {email['sender']}")
        st.write(f"**At:** {email['timestamp']}")
        st.write(email["body"])

        if eid in st.session_state.processed:
            res = st.session_state.processed[eid]

            st.markdown("### Category")
            st.write(res["category"])

            st.markdown("### Actions")
            st.json(res["actions"])

            st.markdown("### Draft Reply")
            draft = res["draft"]

            dsub = st.text_input("Subject", value=draft["subject"])
            dbody = st.text_area("Body", value=draft["body"], height=150)

            if st.button("Save Draft"):
                st.session_state.drafts[eid] = {
                    "subject": dsub,
                    "body": dbody,
                    "email": email,
                }
                save(DRAFTS_FILE, st.session_state.drafts)
                st.success("Draft saved!")

            st.markdown("### Ask Email Agent")
            q = st.text_input("Ask anything about this email:")
            if st.button("Ask"):
                answer = (
                    "Here is my analysis:\n"
                    f"- Category: {res['category']}\n"
                    f"- Actions: {res['actions']}\n"
                    f"- Suggested reply: {draft['body']}"
                )
                st.write(answer)


st.markdown("---")
st.caption("Simplified Email Productivity Agent")


