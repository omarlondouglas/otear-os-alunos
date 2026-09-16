---
name: messaging-automation
description: |
  Skills for automating outbound messaging and communication tasks across various platforms.
  Focuses on programmatic sending of messages with controlled delivery and minimal user interaction.
category: social-media
---

# Messaging Automation

This skill collection centralizes tools for automating outbound messaging. It focuses on programmatic sending of messages, ensuring controlled delivery, and streamlining communication workflows across different platforms.

## Unilateral WhatsApp Dispatch
Provides a method for sending single, unilateral WhatsApp messages via the Evolution API.
- **Core Functionality:** Automates sending text messages to WhatsApp numbers with a controlled delay between sends. It is designed for broadcast-style communication without bot interaction or response processing.
- **Key Features:** Supports text variation, configurable delays, and logging of dispatch status. Uses the Evolution API for sending messages.
- **Linked Content:** The `whatsapp-dispatch` skill (category: `social-media`) contains the specific implementation scripts (Bash template `templates/dispatch-template.sh`), configuration notes, and API details in its reference guide (`references/README.md`). The full original skill can be viewed with `skill_view(name='whatsapp-dispatch', category='social-media')`.
