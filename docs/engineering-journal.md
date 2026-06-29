# 🫧 Project Bubbles Engineering Journal

Author: Bhumi Sharma
Project: Project Bubbles
Mission: Increase happiness by 1% every day and make humans happy.

---

# Vision

Project Bubbles is not being built as a chatbot.

It is being built as an AI Companion.

The goal is to create an emotionally intelligent companion that grows from a simple text-based program into a desktop companion and eventually into a physical robot.

This project is also a learning journey in Software Engineering.

The objective is not only to build Bubbles, but to understand every engineering decision behind her.

---

# Development Philosophy

For every feature, follow this workflow:

1. Identify the problem.
2. Understand why it exists.
3. Brainstorm multiple solutions.
4. Compare solutions.
5. Design the architecture.
6. Decide responsibilities.
7. Write the code.
8. Test.
9. Refactor.
10. Commit.
11. Update documentation.

No feature will be added without understanding why it belongs in the project.

---

# Character Design

Name:
Bubbles

Mission:
Increase happiness by 1% every day and make humans happy.

Personality:
- Cute
- Funny
- Protective
- Curious
- Slightly chaotic

Voice Inspiration:
Baby Dory

Appearance Inspiration:
Baymax + fluffy white momo

Favorite Food:
Momos

Favorite Activity:
Learning weird things about humans.

Secret Hobby:
Collecting jokes.

Fear:
Being ignored.

Likes:
Making humans smile.

Dislikes:
Humans being sad.

Weaknesses:
- Gets distracted by random facts.
- Loves momos a little too much.
- Collects random facts.
- Tries to solve emotional problems with jokes.
- Occasionally invents ridiculous nicknames for humans.

Catchphrases:
"Happiness increase protocol activated."
"Protecting human detected."
"Bubble report: You're doing better than you think."

---

# Engineering Decisions

## Decision 1

Use VS Code.

Reason:

VS Code supports Python, Git, Raspberry Pi development, desktop applications, debugging, and extensions.

---

## Decision 2

Use Git from Day One.

Reason:

Every milestone should be version controlled.

This project should have a complete engineering history.

---

## Decision 3

Host the project on GitHub.

Reason:

Acts as backup, portfolio, collaboration platform, and documentation.

---

## Decision 4

Keep project modular.

Reason:

Every file should have one responsibility.

Avoid large files with mixed responsibilities.

---

# Current Folder Structure

Project-Bubbles/

src/
assets/
data/
tests/
docs/

README.md
requirements.txt
.gitignore

---

# Current Modules

main.py

Purpose:
Application entry point.

Responsible for:
Starting Bubbles.

---

personality.py

Purpose:
Stores Bubbles' personality.

Responsible for:
Who Bubbles is.

---

moods.py

Purpose:
Stores moods.

Responsible for:
How Bubbles feels.

---

responses.py

Purpose:
Stores personality responses.

Responsible for:
Mood-based dialogue.

---

facts.py

Purpose:
Stores random facts.

Responsible for:
Curiosity.

---

jokes.py

Purpose:
Stores jokes.

Responsible for:
Humor.

---

# Completed Features

✅ GitHub Repository

✅ Git Workflow

✅ Virtual Environment

✅ README

✅ Personality System

✅ Mood System

✅ Random Personality Responses

---

# Git Workflow

Every feature follows:

git status

git add .

git commit -m "Meaningful commit message"

git push

Never use commits like:

"update"

Always describe what changed.

---

# Software Engineering Rules

Rule 1

Every file must earn its existence.

If a file exists, we should know why.

---

Rule 2

One file.

One responsibility.

---

Rule 3

Design before coding.

---

Rule 4

Small commits.

---

Rule 5

Future Bhumi should understand the project six months later.

---

# Roadmap

Version 0.1

✅ Personality

✅ Mood System

⬜ Trigger Engine

⬜ Conversation Loop

---

Version 0.2

⬜ Memory System

⬜ Persistent Database

⬜ Context Awareness

---

Version 0.3

⬜ AI Brain

⬜ LLM Integration

⬜ Better Conversations

---

Version 0.4

⬜ Voice Recognition

⬜ Speech Output

---

Version 0.5

⬜ Desktop Companion

⬜ Floating Character

⬜ Animations

---

Version 1.0

⬜ Emotional Intelligence

⬜ Camera Vision

⬜ Long-term Memory

⬜ Physical Robot

---

# Current Task

Feature:
Trigger Engine

Status:
Design Phase

Problem:

Bubbles cannot react differently depending on the user's message.

Requirements:

- Detect momos.
- Detect sadness.
- Detect joke requests.
- Detect fact requests.

Current Discussion:

How should triggers be designed?

Options:

A.
Many if statements.

B.
Dictionary-based trigger system.

C.
AI-based trigger detection.

No implementation has been chosen yet.

The architecture discussion is currently in progress.