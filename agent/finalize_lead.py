from datetime import datetime
from typing import Tuple

from agent.gpt_client import ask_gpt
from agent.prompts import SUMMARIZE_CONVERSATION_PROMPT


def build_conversation_log(messages) -> list:
    log = []
    for m in messages:
        if m["role"] == "user":
            log.append(f"לקוח: {m['content']}")
        elif m["role"] == "assistant":
            log.append(f"סוכן: {m['content']}")
    return log


def summarize_conversation_by_ajent(messages: list) -> str:
    prompt = SUMMARIZE_CONVERSATION_PROMPT
    prompt = prompt.format(messages=messages)
    return ask_gpt(messages=[{"role": "system", "content": prompt}])


def finalize_lead(lead_info: dict, state: dict, messages_history) -> tuple[dict, dict]:
    if not lead_info:
        return {}, state
    lead_info["conversation_log"] = build_conversation_log(messages=messages_history)
    lead_info["summary"] = summarize_conversation_by_ajent(messages=messages_history)
    state["finished"] = True
    state["awaiting_confirmation"] = False
    state["last_updated"] = datetime.now().isoformat()
    return lead_info, state

