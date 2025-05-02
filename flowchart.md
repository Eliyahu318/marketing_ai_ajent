# Flowchart for marketing_ai_ajent.py

This flowchart reflects the logic of the `marketing_ai_ajent.py` file in the `MarketingAjent` class, describing the `process_conversational_lead` function. It includes exact variable names and brief explanations for each node.

```mermaid
flowchart TD

  A[Start - user input received] --> B{Is user_input == בקרה?}
  B -- Yes --> B1[Return self._messages_history] --> Z[End]
  B -- No --> B2[Append message to history]

  B2 --> C{awaiting_confirmation?}
  C -- Yes --> C1[Classify user intent]
  C1 --> C_CONFIRM[CONFIRM]
  C_CONFIRM --> C2[finalize_lead + save_state]
  C2 --> C3[assistant: Thank you! Details saved.] --> Z
  C1 --> C_CORRECT[CORRECT]
  C_CORRECT --> C4[Update flags: awaiting_confirmation=False, awaiting_correction=True] --> C5[assistant: Please specify correction] --> Z
  C1 --> C_OTHER[OTHER]
  C_OTHER --> C6[assistant: Are the details correct or should we edit?] --> Z

  C -- No --> D{awaiting_correction?}
  D -- Yes --> D1[update_lead_based_on_correction]
  D1 --> D2[If response valid then set awaiting_confirmation=True]
  D2 --> D3[assistant: Show updated summary] --> Z

  D -- No --> E{awaiting_reset_decision?}
  E -- Yes --> E1[Classify user intent: reset or continue]
  E1 --> E_RESET[RESET]
  E_RESET --> E2[Reset: keep system message, clear lead_info and history]
  E2 --> E3[assistant: Starting new conversation] --> Z
  E1 --> E_CONTINUE[CONTINUE]
  E_CONTINUE --> E4[Clear flags, set awaiting_correction=True] --> E5[assistant: Continuing from last point] --> Z
  E1 --> E_UNKNOWN[UNKNOWN]
  E_UNKNOWN --> E6[assistant: Not understood. New chat or continue?] --> Z

  E -- No --> F{finished?}
  F -- Yes --> F1[Set awaiting_reset_decision=True] --> F2[assistant: Previous chat ended, start new one?] --> Z

  F -- No --> G[Send conversation to GPT] --> G1[Check if conversation is finished]
  G1 --> G_TRUE[true] --> G2[assistant: Show confirmation request] --> Z
  G1 --> G_FALSE[false] --> G3[assistant: Continue GPT conversation] --> Z

  style A fill:#f9f,stroke:#333,stroke-width:2px
  style Z fill:#fff,stroke:#000
```

