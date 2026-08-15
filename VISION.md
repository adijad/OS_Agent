# OS Agent: Vision

## What We Are Building

OS Agent is a general-purpose AI agent that can operate a user's real computer from natural-language goals.

The user should be able to say things such as:

> Find my latest resume.

> Open Notepad and write a short meeting note.

> Find the assignment PDF I downloaded yesterday and open it.

> Check when my headphones are arriving on Amazon.

> Add toothpaste and Coke Zero to my Amazon cart.

> Find a document on my computer, read it, and use information from it in another application.

The agent should interpret the goal, observe the current computer state, decide what to do, visibly operate the computer, observe the result, and continue until the goal has been achieved.

The computer is the environment.

Applications, websites, files, dialogs, windows, and controls are all parts of that environment.

---

## Core Interaction Loop

The fundamental agent loop is:

```text
Natural-language goal
        ↓
Understand intent
        ↓
Retrieve relevant prior experience / skills
        ↓
Form a high-level plan
        ↓
Observe the current computer
        ↓
Reason about the current state
        ↓
Choose the next action
        ↓
Act using the computer
        ↓
Observe the result
        ↓
Adapt the plan if necessary
        ↓
Continue until success
```

The agent should remain aware of the actual state of the computer throughout execution.

It should not assume that an action succeeded merely because it attempted the action.

---

## Visible Computer Use

OS Agent is intended to behave like an operator using the user's actual computer.

The user should be able to see actions happen:

```text
move cursor
click
type
scroll
switch windows
open applications
navigate interfaces
```

The agent may use semantic information from the operating system, such as Windows UI Automation and accessibility data, to understand controls more reliably.

However, this semantic information supports computer use rather than replacing it with hidden application-specific business APIs.

The long-term perception model should combine:

```text
Accessibility / UI Automation
            +
       Screenshots
            +
   Window / application state
            ↓
      Agent observation
```

This allows the agent to use semantic controls when available while still being able to reason visually when accessibility information is incomplete.

---

## General Computer Tasks

The system is not tied to a particular application or website.

Goals may range from simple local operations to complex multi-application workflows.

Examples:

```text
LOCAL COMPUTER

"Find resume.pdf."

"Open Calculator and calculate 913 × 47."

"Open my MCP project in VS Code."


WEB APPLICATION

"Check when my Amazon headphones are arriving."

"Add a specific product to my Amazon cart."


CROSS-APPLICATION

"Find the PDF I downloaded yesterday, read the deadline,
and add it to my calendar."
```

The same high-level agent architecture should operate across all of these environments.

---

## Learning From Experience

The agent should not reason from scratch forever.

When it successfully completes a task, the system should preserve what happened and extract reusable knowledge from the experience.

Two kinds of memory should be distinguished.

### Experience Memory

An experience records what actually happened during a particular task.

For example:

```json
{
  "goal": "Find tax_return.pdf",
  "observations": [],
  "actions": [],
  "result": "success"
}
```

This is a record of a specific run.

### Procedural Memory

A successful experience may be generalized into a reusable skill.

For example:

```json
{
  "name": "find_local_file",
  "description": "Locate a file on the local computer.",
  "inputs": {
    "query": "string"
  },
  "strategy": [
    "open or focus the file browsing environment",
    "choose a likely search location",
    "search using the requested filename or description",
    "expand the search when necessary",
    "verify that the result matches the request"
  ]
}
```

The procedure should capture useful structure without memorizing brittle coordinates or one exact trajectory.

---

## Procedural Memory Is Guidance, Not a Macro

Learned skills should reduce reasoning, not remove intelligence.

Suppose the first task is:

> Find `report.pdf`.

The agent may discover that the file is in Downloads.

The system should not conclude:

```text
Finding a file = always search Downloads.
```

Instead, it should learn a more general strategy for locating files.

Later:

> Find `thesis.pdf`.

The agent can retrieve the previous file-finding skill and use it as a strong prior, while still observing and reasoning about the current situation.

The desired behavior is:

```text
Relevant skill exists
        ↓
Use skill as initial strategy
        ↓
Observe current environment
        ↓
Follow useful parts
        ↓
Reality differs?
     /        \
   no          yes
   ↓            ↓
continue     reason locally
               ↓
             adapt
               ↓
            continue
```

Skills should accelerate reasoning without trapping the agent inside outdated assumptions.

---

## Skill Evolution

A skill learned from one successful run may be incomplete.

Therefore skills should be able to evolve through additional experience.

Conceptually:

```text
Experience 1
    ↓
Skill v1

Experience 2
    ↓
Skill refined

Experience 3
    ↓
More general strategy

Failures
    ↓
Repair / improve strategy
```

Skills may eventually track information such as:

```text
successful uses
failed uses
applications observed
confidence
last verified time
known variants
common failure states
```

A successful trajectory is evidence, not absolute truth.

---

## Planning and Skill Composition

A user goal may require more than one learned skill.

For example:

> Find the assignment PDF I downloaded yesterday, open it, and summarize the requirements.

The planner may compose:

```text
find_recent_file
        ↓
open_file
        ↓
read_document
        ↓
answer_user
```

For another goal:

> Find a product name from an invoice and look it up on Amazon.

The agent may compose:

```text
find_local_file
        ↓
read_document
        ↓
extract_product
        ↓
search_amazon
```

The planner should determine whether:

```text
an existing skill solves the goal

multiple skills should be composed

an existing skill is only partially useful

or no useful skill exists and full reasoning is required
```

---

## Human-in-the-Loop

Human involvement is a core part of the system, not an edge case.

There are three distinct forms of human interaction.

### Approval

The agent knows what to do, but the next action has meaningful consequences.

Examples include:

```text
placing an order
sending an email
deleting a file
submitting a payment
posting publicly
changing important settings
```

The agent should stop before the consequential action and explain what it intends to do.

Example:

```text
Approval required

Action:
Place Amazon order

Items:
- Toothpaste
- Coke Zero

Total:
$18.24

[Approve] [Reject]
```

Approval should happen at the semantic action level.

The user approves:

```text
"Place this order"
```

not:

```text
"Click x=842, y=611"
```

### Intervention

The agent may encounter a state it cannot safely or confidently resolve.

The system should allow:

```text
Agent control
      ↓
Pause
      ↓
Human takes control of the same desktop session
      ↓
Human resolves the situation
      ↓
Resume
      ↓
Agent observes the new state
      ↓
Continue
```

Human actions during intervention may later become useful learning signals.

### Clarification

Sometimes the agent can continue technically but does not know what the user intended.

For example:

```text
"I found three files that look like your resume.
Which one should I use?"
```

Clarification is distinct from approval and intervention.

---

## Safety

The agent operates a real computer and therefore must treat actions differently based on their consequences.

The policy system should eventually reason about categories such as:

```text
READ / OBSERVE
Usually automatic

NAVIGATION
Usually automatic

LOW-IMPACT WRITE
May be automatic depending on context

CONSEQUENTIAL ACTION
Require approval

DESTRUCTIVE OR SECURITY-SENSITIVE ACTION
Require strong approval or block
```

The agent should never interpret broad computer access as permission to perform every available action.

---

## Architectural Direction

The long-term system can be thought of as:

```text
                    USER GOAL
                        │
                        ▼
                 MAIN AGENT
             Planner / Reasoner
                        │
                        ▼
                SKILL RETRIEVAL
                  /           \
          relevant skill    no skill
               │               │
               ▼               ▼
        guided reasoning   full reasoning
               │               │
               └───────┬───────┘
                       ▼
                  OBSERVATION
                       │
             UIA + visual state
                       │
                       ▼
                    REASON
                       │
                       ▼
                PROPOSE ACTION
                       │
                       ▼
                 POLICY LAYER
                       │
              ┌────────┼────────┐
              │        │        │
            safe    approval   stuck
              │        │        │
              │      HUMAN    HUMAN
              │        │        │
              └────────┴────────┘
                       │
                       ▼
                    ACTION
                       │
              mouse / keyboard
                       │
                       ▼
                 REAL COMPUTER
                       │
                       ▼
                    OBSERVE
                       │
                      ...
                       │
                       ▼
                    SUCCESS
                       │
              ┌────────┴────────┐
              ▼                 ▼
       SAVE EXPERIENCE    CREATE / REFINE
                              SKILL
```

---

## Development Philosophy

Build bottom-up.

First give the system reliable eyes and hands.

Then build the observe → reason → act agent loop.

Then add experience recording.

Then add procedural memory.

Then add skill retrieval and composition.

Then improve adaptation, repair, and human collaboration.

Avoid hiding the computer-use problem behind application-specific APIs or large agent frameworks before the core interaction loop is understood.

The objective is not to collect as many tools as possible.

The objective is to build an agent that becomes more capable through experience while remaining aware of the computer it is actually operating.

---

## Near-Term Milestones

The immediate milestones are:

```text
1. Computer abstraction
2. Structured computer observation
3. Small controlled action space
4. LLM observe → reason → act loop
5. Natural-language Notepad task
6. Generalization to Calculator
7. Experience trajectory recording
8. Procedural skill extraction
9. Skill retrieval on similar future tasks
10. Human approval, intervention, and clarification
```

The first major proof point is:

> A user types "Open Notepad and write Hello World."

The system should determine what to do from the natural-language goal and the observed Windows environment without a hardcoded Notepad workflow.

The second proof point is:

> A user types "Open Calculator and calculate 913 × 47."

The same agent architecture should accomplish the goal without a Calculator-specific workflow being programmed in advance.

Only after those work should skill learning become the primary focus.
