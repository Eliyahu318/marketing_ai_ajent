# marketing_ai_agent.py
import json
import logging
import os
import re
from datetime import datetime
from pathlib import Path
from itertools import islice

from config import settings
from agent.gpt_client import ask_gpt
from agent.prompts import CONVERSATION_PROMPT, CONFIRM_DETAILS_PROMPT, \
    UPDATE_LEAD_PROMPT, CLASSIFY_INTENT_PROMPT
from storage.storage import ensure_file_exists, append_jsonl_file, load_json_file
from agent.lead_validator import validate_lead
from agent.finalize_lead import finalize_lead
from interfaces.info_sender import send_email

DEBUG_MODE = True

logging.basicConfig(level=logging.DEBUG)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


class MarketingAgent:
    def __init__(self, name: str, messages_history: list = None, lead_info: dict = None, state: dict = None):
        self._name = name
        self._lead_info = lead_info
        self._state = state or {
            "last_updated": datetime.now().isoformat(),
            "finished": False,
            "awaiting_reset_decision": False,
            "awaiting_confirmation": False,
            "awaiting_correction": False
        }

        business_profile = load_json_file(settings.business_profile_dir)
        system_message = {
            "role": "system",
            "content": CONVERSATION_PROMPT.format(
                company_name=business_profile.get('name', ''),
                mission=business_profile.get('mission', ''),
                services=business_profile.get('services', []),
                target_audience=business_profile.get('target_audience', ''),
                tone=business_profile.get('tone', ''),
                send_to_email=business_profile.get('send_to_email', '')
            )
        }
        if not messages_history:
            self._messages_history = [system_message]
        else:
            if messages_history[0].get("role") == "system":
                messages_history[0] = system_message  # !זה מוחק את אינדקס 0
            self._messages_history = messages_history

        user_directory = Path(str(settings.user_dir).format(costumer_number=name))
        user_directory.mkdir(parents=True, exist_ok=True)

        self._lead_file = f"{user_directory}/{settings.lead_template.format(costumer_number=name)}"
        self._chat_history_file = f"{user_directory}/{settings.chat_template.format(costumer_number=name)}"
        ensure_file_exists(self._lead_file)
        ensure_file_exists(self._chat_history_file)

    def classify_intent_decision(self, user_input: str) -> str:
        history = "\n".join(
            f"{m['role']}: {m['content']}"
            for m in self._messages_history[-4:])

        full_prompt = CLASSIFY_INTENT_PROMPT.format(context=history, user_input=user_input)
        response = ask_gpt(messages=[{"role": "system", "content": full_prompt}])
        return response.strip().upper()

    def update_lead_based_on_correction(self, correction: str) -> str:
        prompt = UPDATE_LEAD_PROMPT.format(correction=correction, lead_info=dict(islice(self._lead_info.items(), 4)))
        response = ask_gpt(messages=[
            {"role": "system", "content": prompt}
        ])
        self._messages_history.append({"role": "assistant", "content": response})  # ?
        return response

    def extract_json_from_text(self, text: str) -> dict | None:
        try:
            match = re.search(r"\{.*\}", text, re.DOTALL)
            if match:
                return json.loads(match.group())
        except Exception:
            return None

    def check_finish_conversation(self, response: str) -> str | bool:
        if self.extract_json_from_text(response):
            self._lead_info = self.extract_json_from_text(response)
            valid_info = validate_lead(self._lead_info)
            if valid_info[0]:
                confirmation_prompt = CONFIRM_DETAILS_PROMPT.format(lead_info=dict(islice(self._lead_info.items(), 4)))
                confirmation_message = ask_gpt(messages=[{"role": "system", "content": confirmation_prompt}])
                self._state["awaiting_confirmation"] = True
                self._state["last_updated"] = datetime.now().isoformat()
                self._messages_history.append({"role": "assistant", "content": confirmation_message})
                return confirmation_message
            else:
                return valid_info[1]
        return False

    def continue_conversation(self, response):
        self._messages_history.append({"role": "assistant", "content": response})
        self._state["last_updated"] = datetime.now().isoformat()
        return response

    def process_conversational_lead(self, user_input: str) -> str:
        if user_input == "בקרה":
            return str(self._messages_history)

        self._messages_history.append({"role": "user", "content": user_input})  # ?

        if self._state.get("awaiting_confirmation"):
            intent = self.classify_intent_decision(user_input)
            if intent == "CONFIRM":
                self._lead_info, self._state = finalize_lead(
                    lead_info=self._lead_info, state=self._state, messages_history=self._messages_history)
                self.save_state()
                log_text = "\n".join(self._lead_info["conversation_log"])
                send_email(subject=f"{self._name} summary information", body=f"{self._lead_info['summary']}\n\n---\n\n{log_text}")
                response = "תודה! הפרטים נשמרו ונציג יחזור אליך בקרוב 🙌"
                self._messages_history.append({"role": "assistant", "content": response})
                return response
            elif intent == "CORRECT":
                self._state["awaiting_confirmation"] = False
                self._state["awaiting_correction"] = True
                response = "הבנתי. אנא פרט מה תרצה לתקן בפרטים."
                self._messages_history.append({"role": "assistant", "content": response})
                return response
            else:
                response = "סליחה, לא הצלחתי להבין. האם הפרטים נכונים או שברצונך לתקן משהו?"
                self._messages_history.append({"role": "assistant", "content": response})
                return response

        if self._state.get("awaiting_correction"):
            correction = user_input.strip()
            updated_summary = self.update_lead_based_on_correction(correction)
            if updated_summary == "UNKNOWN":
                pass
            else:
                self._state['awaiting_correction'] = False
                finished = self.check_finish_conversation(response=updated_summary)
                if finished:
                    return finished
                else:
                    response = "לא הבנתי את כוונתך, תוכל לחזור שוב?"
                    self._messages_history.append({"role": "assistant", "content": updated_summary})
                    return response

        if self._state.get("awaiting_reset_decision"):
            intent = self.classify_intent_decision(user_input)
            if intent == "RESET":
                self._state["awaiting_reset_decision"] = False
                self._state["finished"] = False
                self._messages_history = self._messages_history[:1]
                self._lead_info = None
                return "מעולה, נתחיל שיחה חדשה. איך אפשר לעזור?"
            elif intent == "CONTINUE":
                self._state["awaiting_reset_decision"] = False
                self._state["finished"] = False
                self._state["awaiting_correction"] = True
                response = "מצוין, נמשיך מאיפה שהפסקנו. איך אפשר לעזור?"
                self._messages_history.append({"role": "assistant", "content": response})
                return response
            else:
                response = "לא הבנתי. ברצונך שיחה חדשה או להמשיך מהיכן שהיינו?"
                self._messages_history.append({"role": "assistant", "content": response})
                return response

        if self._state.get("finished"):
            self._state["awaiting_reset_decision"] = True
            response = "השיחה הקודמת הסתיימה. תרצה שנתחיל שיחה חדשה? (כן/לא)"
            self._messages_history.append({"role": "assistant", "content": response})
            return response

        response = ask_gpt(messages=self._messages_history)
        finish = self.check_finish_conversation(response)
        if finish:
            # print("212", self._lead_info["summary"])
            return finish
        return self.continue_conversation(response)

    @classmethod
    def load_state(cls, name: str) -> "MarketingAgent":
        user_directory = str(settings.user_dir).format(costumer_number=name)
        lead_file = f"{user_directory}/{str(settings.lead_template).format(costumer_number=name)}"
        chat_history_file = f"{user_directory}/{str(settings.chat_template).format(costumer_number=name)}"

        try:
            lead_info = load_json_file(lead_file) if os.path.exists(lead_file) else None
        except json.decoder.JSONDecodeError:
            lead_info = None

        if os.path.exists(chat_history_file):
            try:
                chat_data = load_json_file(chat_history_file)
                state = chat_data.get("state", {})
                messages = chat_data.get("messages", [])
            except json.decoder.JSONDecodeError:
                state = None
                messages = None
        else:
            state = None
            messages = None

        return cls(name=name, lead_info=lead_info, messages_history=messages, state=state)

    def save_state(self):
        if isinstance(self._lead_info, dict) and self._lead_info:
            append_jsonl_file(path=self._lead_file, data=self._lead_info)

        full_data = {
            "messages": self._messages_history,
            "state": self._state
        }
        append_jsonl_file(path=self._chat_history_file, data=full_data)
