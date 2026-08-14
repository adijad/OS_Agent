# OS Agent

An experimental Windows computer-use agent built from the OS level up.

The project explores how an AI agent can observe and interact with desktop applications through Windows UI Automation, learn reusable capabilities, and eventually compose those capabilities to complete natural-language goals.

## Current Progress

The first OS interaction loop is working with Windows Notepad:

* Detect whether Notepad is running
* Launch it when needed
* Discover the text editor through Windows UI Automation
* Focus and interact with the editor
* Write text using keyboard input
* Read the resulting text through UI Automation
* Verify that the requested state was reached

Current flow:

```text
Observe → Identify Control → Act → Observe Result → Verify
```

## Project Direction

The longer-term goal is a self-expanding computer-use system that can:

* Understand natural-language goals
* Inspect the current Windows environment
* Reuse previously learned capabilities
* Discover new procedures when a capability does not exist
* Store successful procedures as reusable capabilities
* Replay known capabilities deterministically
* Repair capabilities when application interfaces change
* Compose multiple capabilities for larger tasks
* Require human approval for consequential actions

## Stack

* Python
* Windows UI Automation
* pywinauto

## Status

Early development. The current focus is building and understanding the underlying OS interaction layer before adding LLM reasoning and capability learning.
