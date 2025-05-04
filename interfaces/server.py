import logging
import os
from flask import Flask, request, Response
from twilio.twiml.messaging_response import MessagingResponse
from agent.marketing_ai_agent import MarketingAgent

app = Flask(__name__)


users = {}


@app.route("/", methods=["GET"])
def root():
    return "🟢 OK", 200


@app.route("/whatsapp", methods=["GET", "POST"])
def whatsapp_webhook():
    incoming_msg = request.values.get("Body", "").strip()
    from_number = request.values.get("From", "").replace("whatsapp", "")
    print(f"📩 הודעה מ-{from_number}: {incoming_msg}")

    if from_number not in users:
        users[from_number] = MarketingAgent.load_state(name=from_number)
    ajent = users[from_number]

    response_text = ajent.process_conversational_lead(incoming_msg)

    twiml = MessagingResponse()
    twiml.message(response_text)
    logging.info(response_text)
    return Response(str(twiml), mimetype="application/xml")


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 4000))
    app.run(debug=True, host="0.0.0.0", port=port)