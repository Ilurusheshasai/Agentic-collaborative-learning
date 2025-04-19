# Agentic Collaborative Learning

Welcome to **Agentic Collaborative Learning**, an automated, multi-agent system designed to supercharge student collaboration and learning quality in any classroom setting! This agentic model helps to solve that problem by allowing topic sharing between students by professor. Students submit the part of topic they have to prepare submit it in shared drive folder and LLM verifies it based on instruction provided by professor and then send email to other students to refer notes of it meets professor set bar, else suggest improvements to student and suggests a re-submission before sending to others.

**Whats the point of every student reading the same notes yet the dont learn fully and dont get feedback on what they lack. Its embarcing to learn something in Univs and be in an ackward position when someone asks you questions and you cant answer it. This agentic model approach try's to eleminate the problem, by giving time to prepare notes, tell what you miss and share the notes with your peers quick feedbacks and encouraging discussions among students for next classes by preparing question that help you understand the why and how of learning process (Future work -  preparing question that help you understand the why and how of learning process).**

👥 Student Conversation

-Dude1: Hey Bob, did you ever feel overwhelmed when everyone submits notes but no one really knows which ones are any good?
-Dude2: Absolutely. I’ve spent hours trying to piece together classmates’ notes, only to find crucial parts missing or unclear.
-Dude1: That’s why I’m excited about Agentic Collaborative Learning. It automatically collects submissions, uses an LLM to check them against our professor’s criteria, and then either gives feedback or shares the polished version with everyone.
-Dude2: Wow—that means if my draft is missing examples or derivations, I get immediate suggestions to improve it before it’s shared broadly.
-Dude1: Exactly! And once approved, it emails the class with a link. Plus, it can generate discussion questions so we come to class prepared to dig deeper.
-Dude2: Sounds like it’ll save time and make discussions way more engaging. No more guessing what the key concepts are and knowledge gaps!

Dude1: Yep, and the professor sets the learning objectives once, then it runs itself. Pretty cool for our learning.
---

## 🚀 Project Overview

Traditional peer-based learning in large topics often suffers from:
- **Repeated Learning**: Every student learns same topics during an assignment and just get graded they they dont know how others are thinking and what is expected to learn.    
- **Fragmented material**: Students produce notes of varying quality, leading to confusion.
- **Delayed feedback**: Human grading/feedback can take days, hindering momentum.
- **Lack of engagement**: Static notes sit unused, and class discussions lack fresh stimulus.

**Agentic Collaborative Learning** addresses these challenges by:
2. **Automating note collection** via a **Drive Monitor Agent**.
3. **Instantly evaluating quality** with an **LLM Critique Agent** against professor‑defined learning objectives.
4. **Providing feedback loops** through a **Feedback Agent**, so students iteratively improve their notes.
5. **Broadcasting polished notes** to peers with a **Notification Agent** once approved.
6. **Sparking discussion** by auto‑generating thought‑provoking questions via a **Content Agent**.

This pipeline ensures **high‑quality, consistent**, and **engaging** learning resources, boosting both efficiency and student motivation.

---

## 🎯 Why It Matters

> “In modern classrooms, learning materials are only as effective as their currency and quality.”

- **Quality Control**: Automated LLM evaluation enforces a consistent standard across all student submissions.
- **Timely Feedback**: Near‑real‑time critique helps students correct gaps before misconceptions solidify.
- **Collaborative Amplification**: Approved notes become shared resources, reducing redundant effort and promoting peer learning.
- **Engagement Catalyst**: Generated quizzes and discussion prompts keep the classroom conversation lively and focused.

This becomes crucial in fast‑paced growing word—where traditional workflows can bottleneck.

---

## 🔧 Architecture & Agents

```
[Student Upload] → Drive Monitor Agent → LLM Critique Agent → Feedback Agent → Final Approval → Notification Agent → Content Agent → [Class Engagement]
```

| Agent                   | Responsibility                                                                                      |
|-------------------------|-----------------------------------------------------------------------------------------------------|
| **Drive Monitor Agent** | Watches a designated Google Drive folder for new uploads                                           |
| **LLM Critique Agent**  | Evaluates notes vs. professor’s scope (objectives, derivations, examples)                          |
| **Feedback Agent**      | Sends personalized feedback to the uploader for improvements                                        |
| **Notification Agent**  | Broadcasts approved notes (with attachments) to classmates                                          |
| **Content Agent**       | Generates discussion questions & polished email content using LLMs (Gemini)                         |

Built modularly in **Python**, leveraging:

- **Google Drive API** (monitoring & file operations)
- **Google GenAI (Gemini)** for critique and content generation
- **SMTP** for email notifications
- **Configurable JSON** for folder IDs, learning objectives, and class rosters

---

## ⚙️ Technology Stack

- **Language:** Python 3.10+
- **APIs:** Google Drive API, Google GenAI (Gemini)
- **Libraries:** `google-auth`, `google-api-python-client`, `google-genai`, `openai` (optional), `smtplib`
- **Design Pattern:** Multi‑agent system, event‑driven architecture

---

## 📂 Folder Structure

```
agentic_learning/
├── agents/
│   ├── drive_monitor/   # Detects uploads & metadata
│   ├── critique_agent/  # LLM evaluation and email content
│   ├── notification_agent/ # SMTP email sender
│   └── content_agent/   # Generates discussion questions and polished messages
├── config/             # JSON configs: drive_folder, scope, emails
├── state/              # Persistent state of processed files
├── credentials.json    # OAuth credentials for Drive API
├── requirements.txt    # Python dependencies
└── README.md           # Project overview and instructions
```

---

## 🚀 Quick Start

1. **Clone** this repo:
   ```bash
   git clone https://github.com/yourusername/agentic-collaborative-learning.git
   cd agentic-collaborative-learning
   ```

2. **Setup** virtual environment & install dependencies:
   ```bash
   python -m venv env
   source env/bin/activate    # Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure**:
   - Place `credentials.json` in the project root.
   - Edit `config/drive_folder.json` with your Drive folder ID & class emails.
   - Edit `config/scope.json` with professor’s learning objectives.
   - Set environment variables: `GEMINI_API_KEY`, `SMTP_SERVER`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASS`, `FROM_EMAIL`.

4. **Run** the monitor:
   ```bash
   python -m agentic_learning.agents.drive_monitor.monitor
   ```


---

## 📖 Discussion & Future Directions

This project is a basic yet **conversational, agentic approach** to learning:

- **Agent-driven collaboration** transforms static sharing into dynamic, automated workflows.
- **LLM integration** elevates both content quality and student agency.
- **Continuous feedback loops** foster a growth mindset—errors become learning moments.

this architecture can be extended to:
- Real‑time Slack/Teams integrations
- Advanced analytics dashboards tracking student progress
- Adaptive quizzes based on individual performance
- Gamification elements (badges, leaderboards)

---

## 🤝 Contributing

We welcome collaboration! Please fork, open issues, and submit PRs.

---

## 📜 License

MIT © [sai Iluru]

---

*Presented at HackUMBC 2025 — Empowering the next generation of learners through agentic automation.*

