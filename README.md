# OS Agent

A general-purpose AI agent that learns to operate a real Windows computer from natural-language goals.

OS Agent explores how an AI system can observe the current desktop, reason about what to do next, visibly interact with applications using mouse and keyboard actions, and improve future performance by learning reusable procedures from successful experience.

## Vision

The goal is to support tasks ranging from simple local actions:

```text
"Find my latest resume."

"Open Notepad and write Hello World."

"Open Calculator and calculate 913 × 47."
```

to larger workflows:

```text
"Check when my headphones are arriving on Amazon."

"Find the PDF I downloaded yesterday, read the deadline,
and use that information in another application."
```

The core interaction loop is:

```text
Goal
 ↓
Retrieve relevant prior skills
 ↓
Plan
 ↓
Observe
 ↓
Reason
 ↓
Act
 ↓
Observe again
 ↓
Adapt
 ↓
Complete
```

Learned procedures are intended to **guide future reasoning rather than become brittle macros**.

See [VISION.md](VISION.md) for the full project direction.

## Current Progress

The initial Windows interaction proof of concept is working with Notepad.

The system can currently:

* Detect whether Notepad is running
* Launch it when needed
* Discover the text editor through Windows UI Automation
* Focus and interact with the editor
* Write text using keyboard input
* Read the resulting text through UI Automation
* Verify that the requested state was reached

Current low-level loop:

```text
Observe → Identify Control → Act → Observe Result → Verify
```

## Next Milestone

The next goal is to move from scripted automation to an actual agent loop.

Instead of hardcoding which Notepad control to use, the system will expose a structured observation of the current computer to an LLM and give it a small controlled action space.

The first target is:

```text
User:
"Open Notepad and write Hello World."

Agent:
observe → reason → act → observe → verify
```

The same architecture will then be tested on a different application, such as:

```text
"Open Calculator and calculate 913 × 47."
```

without implementing an application-specific workflow.

## Long-Term Direction

OS Agent is intended to develop:

* General OS-level computer use
* Accessibility and visual perception
* Natural-language planning
* Experience recording
* Procedural memory
* Skill retrieval and composition
* Adaptation when interfaces or circumstances differ
* Human approval for consequential actions
* Human takeover and resume when the agent gets stuck
* Clarification when user intent is ambiguous

## Human-in-the-Loop

The system will distinguish between three forms of human involvement:

**Approval:** The agent knows what to do but needs permission before a consequential action.

**Intervention:** The agent is stuck and temporarily gives control of the live computer back to the user.

**Clarification:** The agent needs additional information about what the user intended.

## Current Stack

* Python
* Windows UI Automation
* pywinauto

## Status

Early development.

The current focus is building the OS interaction and observation layer before introducing the first LLM-driven observe → reason → act loop.
