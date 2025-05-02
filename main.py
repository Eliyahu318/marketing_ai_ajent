import logging
from agent.marketing_ai_agent import MarketingAgent


def main():
    ajent = MarketingAgent.load_state("0506718268")  # , confirm_callback=ask_user_confirm)
    while True:
        user_input = input("")
        response = ajent.process_conversational_lead(user_input=user_input)
        logging.info(response)
        if "הפרטים נשמרו" in response:
            break


if __name__ == "__main__":
    main()
