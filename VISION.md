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
Retrieve relevant prior experience / skills when useful
        ↓
Form or update a high-level plan when useful
        ↓
Observe the current computer
        ↓
Reason about the current state
        ↓
Choose the next semantic action
        ↓
Policy evaluation
        ↓
Act using the computer
        ↓
Observe the real outcome
        ↓
Verify progress
        ↓
Update working context / adapt / replan if necessary
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

# Canonical Agent Design Patterns

OS Agent should not adopt every popular agent pattern equally.

The following patterns define the intended long-term architecture.

| Pattern | Role in OS Agent | Architectural Status |
| --- | --- | --- |
| Tool Use / Function Calling | Operate the real computer through semantic actions | Core and foundational |
| Hierarchical Planning | Decompose long or multi-application goals into semantic subgoals | First-class for complex tasks |
| Memory and Context Management | Maintain useful state during long tasks and learn across tasks | First-class |
| Verification and Recovery | Ground success in environmental evidence and recover from failures | First-class |
| Orchestrator / Workers | Isolate specialized cognitive workloads when there is demonstrated need | Optional, later-stage |

The mature OS Agent should therefore be understood primarily as:

```text
Tool-Using Computer Agent
          +
Hierarchical Semantic Planning
          +
Working / Episodic / Procedural Memory
          +
Environment-Grounded Verification and Recovery
          +
Policy and Human Control
```

It should not be designed primarily as a multi-agent system.

These are logical architectural roles.

They do not imply that every role requires a separate LLM.

Planning, execution, verification, memory management, and other cognitive roles may initially use the same underlying model through different contexts and contracts.

Telemetry and evaluation should later determine whether specialization across models is actually beneficial.

---

# Tool Use and Semantic Actions

Tool use is foundational because OS Agent must affect an external environment rather than merely produce text.

The core execution path should remain:

```text
Model
  ↓
Propose semantic action
  ↓
Validate and ground
  ↓
Policy
  ↓
Execute
  ↓
Observe real outcome
```

Low-level computer capabilities may include:

```text
click
type_text
press_key
hotkey
scroll
focus_window
open_application
drag
```

Over time, the system may learn or compose higher-level capabilities such as:

```text
find_file
read_document
navigate_browser
fill_form
create_calendar_event
```

These higher-level capabilities should not become hardcoded application-specific workflows by default.

They should preferably emerge as reusable procedural skills or compositions of general capabilities.

Avoid architectures such as:

```text
ChromeAgent
AmazonAgent
NotepadAgent
CalculatorAgent
FileExplorerAgent
```

The same general computer agent should operate different applications through observation and semantic action.

The runtime should provide general capabilities.

The model should provide task-specific intelligence.

---

# Memory Architecture

Memory is not a single subsystem.

OS Agent should distinguish three different forms of memory with different lifetimes and responsibilities.

## Working Memory

Working memory contains temporary information that matters for the current task.

It is not a deterministic domain schema.

For example, a shopping task may temporarily require remembering:

```text
Pixel 11 verified at $799
Direct product URL collected
Need two more qualifying candidates
One page failed repeatedly
```

A completely different task may require:

```text
Assignment PDF found
Deadline is September 14 at 11:59 PM
Calendar event still needs to be created
```

The runtime should provide a generic working-memory capability or task blackboard.

The model determines what information is relevant to the current goal.

Working memory exists to support long-horizon execution and context management.

It should not hardcode concepts such as:

```text
products
prices
phones
resumes
emails
calendar events
shopping results
```

into the core architecture.

The desired idea is:

```text
Runtime provides memory capability
            ↓
Model decides what is worth remembering
            ↓
Memory remains available throughout the task
            ↓
Agent uses it to maintain progress
```

Working memory should help answer:

```text
What have I learned?

What have I already completed?

What still needs to happen?

What failed?

What should I avoid repeating?

What information must survive beyond the last few actions?
```

---

## Episodic Memory

Episodic memory records what actually happened during a particular task.

For example:

```json
{
  "goal": "Find tax_return.pdf",
  "observations": [],
  "actions": [],
  "policy_events": [],
  "human_interactions": [],
  "result": "success"
}
```

This is evidence about a specific run.

A trajectory may eventually include:

```text
goal
observations
model decisions
actions
grounded targets
policy decisions
human interactions
working-memory updates
execution results
verification results
failures
retries
completion evidence
final outcome
```

Episodic memory should preserve experience without assuming that every successful behavior should automatically become a reusable skill.

---

## Procedural Memory

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

The three forms should remain conceptually separate:

```text
Working Memory
= what matters right now

Episodic Memory
= what happened before

Procedural Memory
= what reusable strategy was learned
```

---

# Procedural Memory Is Guidance, Not a Macro

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

They should not become deterministic macro replay.

---

# Skill Evolution

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

Failures are also learning signals.

---

# Hierarchical Planning and Skill Composition

Planning is essential for complex and long-horizon tasks, but plans should remain semantic and adaptive.

Avoid rigid action plans such as:

```text
1. Click Chrome
2. Click tab 3
3. Press Ctrl+L
4. Click result 2
5. Scroll 400 pixels
```

Those plans become stale as soon as the environment changes.

Instead, planning should describe what needs to happen.

For example:

```text
GOAL

Apply to this job using my latest resume


SEMANTIC PLAN

1. Identify the job posting
2. Locate the latest resume
3. Extract relevant requirements
4. Determine useful resume changes
5. Update the resume
6. Save a new version
7. Draft the application email
8. Request approval before sending
```

The existing observe -> reason -> act executor should dynamically determine how to accomplish each subgoal in the current environment.

The intended separation is:

```text
Planner
= WHAT needs to happen

Computer Executor
= HOW to accomplish the current subgoal
  in the observed environment
```

Planning should be optional for simple tasks rather than mandatory overhead.

For example:

```text
"Open Notepad."
```

does not need an elaborate planner.

But:

```text
"Find the PDF I downloaded yesterday,
read the deadline,
and add it to my calendar."
```

benefits from decomposition.

Initially, whether decomposition is useful should preferably be model-driven rather than encoded as a brittle deterministic task classifier.

A user goal may also require multiple learned skills.

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

For another task:

> Find a product name from an invoice and look it up on Amazon.

The planner may compose:

```text
find_local_file
        ↓
read_document
        ↓
extract_product
        ↓
search_product
```

The planner should determine whether:

```text
an existing skill solves the goal

multiple skills should be composed

an existing skill is only partially useful

or no useful skill exists and full reasoning is required
```

Planning must remain adaptive.

After meaningful subgoals or environmental changes, the system may revise the remaining plan rather than blindly executing an outdated script.

---

# Verification and Recovery

OS Agent should favor environment-grounded verification over generic continuous self-reflection.

For computer-use tasks, the real environment often provides stronger evidence than another model opinion.

The preferred loop is:

```text
Perform action or subtask
        ↓
Observe environment
        ↓
Verify outcome
      /       \
 success     failure
    │           │
    ▼           ▼
continue     diagnose
                ↓
          retry / recover
                ↓
             replan
```

Verification may operate at different levels.

### Deterministic verification

Example:

```text
Does Calculator show the completed expected expression?
```

### Semantic verification

Example:

```text
Is this actually the resume the user intended?
```

### Model-assisted verification

Example:

```text
Does this product satisfy the user's qualitative requirements?
```

Prefer the lowest-cost reliable verifier available.

The system should distinguish:

```text
Executor success
= the action was physically issued

Task success
= the observed environment provides evidence
  that the intended outcome was achieved
```

The model saying:

```text
"I completed the task."
```

is not sufficient evidence on its own.

Recovery should also be bounded.

Repeated failures should not lead to endless retries.

The system should be able to:

```text
diagnose
try an alternative strategy
replan
request clarification
request intervention
or stop safely
```

depending on the situation.

---

# Human-in-the-Loop

Human involvement is a core part of the system, not an edge case.

There are three distinct forms of human interaction.

## Approval

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

Approval should authorize the intended semantic consequence, not arbitrary future physical interaction.

---

## Intervention

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

Examples may include:

```text
CAPTCHA
unexpected authentication
unrecognized dialog
repeated failure
environment state the agent cannot safely recover from
```

The agent must re-observe the environment after human intervention.

It should never assume what the human changed.

Human actions during intervention may later become useful learning signals.

---

## Clarification

Sometimes the agent can continue technically but does not know what the user intended.

For example:

```text
"I found three files that look like your resume.
Which one should I use?"
```

Clarification is distinct from approval and intervention.

The agent is not stuck technically.

The user's intent is ambiguous.

---

# Safety and Policy

The agent operates a real computer and therefore must treat actions differently based on their consequences.

Policy and human control form a control plane around the cognitive architecture.

They are not optional add-ons.

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

Policy should evaluate semantic consequences rather than only primitive action names.

For example:

```text
click "Next page"
→ likely allow

click "Place order"
→ approval required

click "Delete permanently"
→ approval required or block depending on context
```

A `click` is not inherently safe or dangerous.

Its meaning depends on what the click will do.

The policy layer should therefore consider context such as:

```text
current goal
active application
target role
target name
surrounding semantic state
intended effect
current task context
```

The planner, memory system, learned skills, and model must never bypass the policy layer.

The agent should never interpret broad computer access as permission to perform every available action.

---

# Optional Orchestrator and Cognitive Workers

Orchestrator-worker architecture is not a foundational requirement for OS Agent.

Do not split the system into application-specific agents.

Avoid:

```text
Browser Agent
Chrome Agent
Amazon Agent
File Agent
Notepad Agent
Calculator Agent
```

The goal is one general computer-use architecture.

Specialized workers may become useful later when tasks contain genuinely different cognitive workloads with different context requirements.

For example:

```text
Research / analysis worker
Document analysis worker
Writing worker
Computer operator
```

A future architecture might look like:

```text
                    ORCHESTRATOR
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
  Research Worker   Writing Worker   Computer Operator
                                             │
                                             ▼
                                        Real Desktop
```

Even if specialized workers are introduced, physical computer control should remain serialized.

A core invariant is:

> Only one authority should mutate the physical desktop at a time.

Workers may reason or analyze independently.

Multiple workers should not concurrently click, type, switch windows, or otherwise compete for the same desktop session.

Worker specialization should be introduced only after telemetry and evaluation demonstrate a concrete benefit.

The system should not become multi-agent merely because multi-agent architectures appear sophisticated.

---

# Observability and Evaluation

OpenTelemetry and systematic evaluation are part of the engineering architecture of OS Agent.

Observability does not make decisions for the agent.

It makes the behavior of the agent measurable and debuggable.

The whole architecture should eventually be observable across signals such as:

```text
run / task
steps
model calls
provider and model
token usage
latency
observations
action proposals
policy decisions
execution results
working-memory operations
planning / replanning
verification
retries and failures
human approvals
clarifications
interventions
final outcome
```

A user goal should correspond to one coherent trace with nested spans for meaningful stages of execution.

Conceptually:

```text
os_agent.run
    │
    ├── os_agent.step
    │     ├── computer.observe
    │     ├── model.choose_action
    │     ├── policy.check
    │     └── executor.execute
    │
    ├── os_agent.step
    │     └── ...
    │
    └── completion
```

Telemetry should make it possible to answer questions such as:

```text
Does planning improve task success?

Does procedural memory reduce model calls or tokens?

How much context does working memory add?

How often does verification catch false completion?

Where does latency come from?

Which models perform best for planning versus execution?

How frequently are approvals or interventions required?

Which tasks cause repeated retries?

Which actions fail most frequently?

How much does a successful task cost?
```

Telemetry should be metadata-first and privacy-conscious.

Sensitive information such as:

```text
screenshots
document contents
credentials
personal messages
private files
payment information
authentication data
```

should not be recorded merely because instrumentation exists.

Environment-grounded evaluations should remain the source of truth for benchmark success.

A model claiming completion is not sufficient evidence.

---

# Canonical Architectural Direction

The long-term system should evolve toward:

```text
                           USER GOAL
                               │
                               ▼
                       OPTIONAL PLANNER
                               │
                    semantic subgoals / replan
                               │
                               ▼
                       CONTEXT MANAGER
                      /               \
                     ▼                 ▼
              WORKING MEMORY      RETRIEVED SKILLS
                     \                 /
                      └───────┬────────┘
                              ▼
                       COMPUTER AGENT
                    observe → reason
                              │
                              ▼
                       SEMANTIC ACTION
                              │
                              ▼
                           POLICY
                    /          |          \
                 allow      approval      block
                   │            │
                   │          HUMAN
                   │            │
                   └──────┬─────┘
                          ▼
                       EXECUTOR
                          │
                          ▼
                    REAL COMPUTER
                          │
                          ▼
                     OBSERVATION
                          │
                          ▼
                       VERIFIER
                     /          \
                success        failure
                   │              │
                   ▼              ▼
             next subgoal     recover / replan
                   │              │
                   └──────┬───────┘
                          ▼
                   TASK COMPLETION
                          │
                          ▼
                  EPISODIC TRAJECTORY
                          │
                          ▼
              PROCEDURAL SKILL LEARNING
```

OpenTelemetry and evaluation surround this architecture as an engineering control plane.

Optional specialized cognitive workers may later sit around planning, analysis, or writing workloads, but they do not replace the single controlled computer-execution path.

---

# Architectural Invariants

The following principles should remain stable unless strong experimental evidence justifies changing them.

1. **The computer is the environment.**

2. **Real environmental state is the source of truth for completion.**

3. **The model proposes semantic actions rather than brittle coordinates or vendor-specific automation syntax whenever possible.**

4. **The runtime provides generic capabilities. The model provides task-specific reasoning.**

5. **Do not create application-specific agents or hardcoded application workflows by default.**

6. **Planning describes semantic subgoals, not rigid click sequences.**

7. **Working memory must remain generic rather than becoming deterministic domain-specific task state.**

8. **Working, episodic, and procedural memory are different systems with different lifetimes.**

9. **Learned procedures guide execution. They do not become blind macro replay.**

10. **Policy and human control cannot be bypassed by planning, memory, tools, or learned skills.**

11. **Verification should prefer real environmental evidence over model self-claims.**

12. **Physical desktop mutation remains serialized even if specialized cognitive workers are introduced later.**

13. **New architectural complexity should be justified by evaluation and telemetry rather than added because a pattern appears sophisticated.**

14. **Model/provider specialization should be evidence-driven. Logical roles do not automatically require separate LLMs.**

15. **The system should remain adaptive to the current computer state rather than assuming previous environments still apply.**

---

# Canonical Implementation Order

The architecture above describes the destination.

The following sequence describes the intended implementation order.

This ordering is canonical so future work does not accidentally jump ahead or replace general mechanisms with task-specific shortcuts.

```text
1. TOOL USE / OS INTERACTION FOUNDATION

   Reliable Windows observation
   Screenshots and UI Automation
   Semantic action schema
   Mouse / keyboard / application control
   Application lifecycle awareness
   Observe → reason → act execution loop
   Multiple model-provider abstraction
   Environment-grounded evaluation


2. OBSERVABILITY AND EVALUATION

   OpenTelemetry traces
   Model/provider metadata
   Token usage
   Model latency
   Run-level latency
   Hierarchical run / step traces
   Observation timing
   Policy timing
   Executor timing
   Metrics
   OTLP export / observability backend
   Environment-grounded benchmarks


3. POLICY ENGINE

   Semantic risk evaluation
   Consequence-aware actions

   ALLOW
   APPROVAL_REQUIRED
   BLOCK

   Safety boundaries independent of the model


4. HUMAN-IN-THE-LOOP

   Approval
   Clarification
   Intervention
   Pause / resume
   Fresh observation after human actions
   Semantic approval rather than coordinate approval


5. WORKING MEMORY AND CONTEXT MANAGEMENT

   Generic task blackboard
   Important discoveries
   Collected evidence
   Unresolved failures
   Active subgoal
   Remaining work
   Compact context for long trajectories
   Avoid deterministic domain-specific task state


6. HIERARCHICAL PLANNING

   Semantic task decomposition
   Optional planning for complex goals
   Adaptive replanning
   Subgoal management
   Skill composition
   No rigid click-by-click plans


7. VERIFICATION AND RECOVERY

   Environment-grounded outcome verification
   Deterministic verification when possible
   Semantic verification when required
   Model-assisted verification when necessary
   Bounded retries
   Failure diagnosis
   Alternate strategies
   Replanning
   Clarification or intervention when recovery fails


8. EPISODIC TRAJECTORY RECORDING

   Preserve complete task experiences
   Observations
   Actions
   Policy events
   Working-memory updates
   HITL events
   Verification results
   Failures
   Completion evidence
   Final outcomes

   Build a learning dataset from real executions


9. PROCEDURAL SKILL LEARNING

   Extract generalized reusable strategies
   Avoid brittle macro replay
   Track successful and failed uses
   Track confidence
   Refine skills through additional experience


10. SKILL RETRIEVAL AND COMPOSITION

    Retrieve relevant procedures semantically
    Use procedures as priors rather than scripts
    Compose multiple skills for complex goals
    Adapt retrieved knowledge to the current environment


11. OPTIONAL SPECIALIZED COGNITIVE WORKERS

    Introduce only for demonstrated specialization needs
    Separate cognitively different workloads when beneficial
    Allow different models where telemetry justifies it
    Keep physical computer control serialized
```

The presence of a later-stage design pattern in the long-term architecture does not mean it should be implemented before its prerequisites.

In particular:

```text
Do not jump to long-term procedural memory
before working memory and reliable trajectories exist.

Do not add powerful long-horizon planning
before policy and human control are established.

Do not add multi-agent workers
merely to make the architecture look more advanced.

Do not replace generic computer use
with application-specific agents
when a general capability can solve the problem.

Do not introduce deterministic task-state schemas
for individual domains such as shopping,
job searching, email, or file management.

Do not treat model-declared success
as proof that a real-world task succeeded.
```

---

# Current Development Position

The project has already established much of the Tool Use / OS Interaction foundation.

Current capabilities include:

```text
Windows desktop observation
Active-window observation
UI Automation controls
Screenshot perception
Semantic target IDs

Visible mouse interaction
Literal text input
Special keys
Structured hotkeys
Application opening
Application focusing

Application lifecycle reasoning

Semantic action validation
Action execution
Basic policy boundary

Natural-language agent loop

OpenAI provider
Anthropic provider

Cross-model evaluation

Environment-grounded Calculator evaluation

Browser interaction

UI control value observation

Initial OpenTelemetry model tracing
Token usage tracking
Model latency tracking
Provider/model metadata
```

The project is currently in:

```text
PHASE 2

OBSERVABILITY AND EVALUATION
```

The immediate observability objective is:

```text
ONE USER GOAL
      ↓
ONE COHERENT TRACE
      ↓
os_agent.run
    │
    ├── os_agent.step
    │     └── os_agent.model.choose_action
    │
    ├── os_agent.step
    │     └── os_agent.model.choose_action
    │
    └── ...
```

After hierarchical run and step tracing is validated, the next observability increment should be:

```text
os_agent.step
    ├── computer.observe
    ├── model.choose_action
    ├── policy.check
    └── executor.execute
```

Then:

```text
OpenTelemetry metrics
        ↓
OTLP export
        ↓
trace / metrics backend
```

After the observability foundation is sufficiently stable:

```text
Policy Engine v1
        ↓
Human-in-the-Loop
        ↓
Working Memory
        ↓
Hierarchical Planning
        ↓
Verification / Recovery
        ↓
Episodic Trajectories
        ↓
Procedural Learning
```

---

# Development Philosophy

Build bottom-up and preserve generality.

First give the system reliable eyes and hands.

Then make the observe → reason → act loop measurable.

Then establish safety and human control before increasing long-horizon autonomy.

Then add working memory and context management.

Then add hierarchical planning and environment-grounded verification.

Then record rich episodic trajectories and learn procedural skills from real evidence.

Only introduce specialized cognitive workers if a demonstrated workload justifies the additional complexity.

Avoid hiding the computer-use problem behind application-specific APIs or large agent frameworks before the core interaction loop is understood.

The objective is not to collect as many:

```text
tools
models
agents
frameworks
memory systems
design patterns
```

as possible.

The objective is to build a general computer agent that becomes more capable through experience while remaining:

```text
observable
verifiable
safe
adaptive
human-controllable
and aware of the real computer it is operating
```

---

# Major Proof Points

## Proof Point 1: Generic application execution

> A user types "Open Notepad and write Hello World."

The system should determine what to do from the natural-language goal and the observed Windows environment without a hardcoded Notepad workflow.

---

## Proof Point 2: Cross-application generality

> A user types "Open Calculator and calculate 913 × 47."

The same agent architecture should accomplish the goal without a Calculator-specific workflow being programmed in advance.

---

## Proof Point 3: Browser research with grounded evidence

The agent should be capable of:

```text
opening or focusing a browser
navigating interfaces
searching
reading accessible content
collecting useful evidence
recovering direct URLs
and returning grounded information
```

without introducing a browser-specific intelligence architecture.

---

## Proof Point 4: Safe consequential action

The agent should be able to reach a consequential action such as:

```text
send email
place order
delete file
submit form
```

then pause before execution, describe the semantic consequence, request approval, and correctly handle approval or rejection.

---

## Proof Point 5: Generic long-horizon working memory

The agent should complete a task requiring information to survive across many steps without introducing a domain-specific task-state schema.

For example:

> Find several suitable products, compare them, and return the verified results and direct links.

or:

> Find the PDF I downloaded yesterday, determine the deadline, and add it to my calendar.

---

## Proof Point 6: Adaptive planning

The agent should decompose a complex goal into semantic subgoals while continuing to react to the real environment.

If the environment changes or a planned route fails, it should revise the plan instead of blindly executing an outdated script.

---

## Proof Point 7: Verification and recovery

The agent should recognize when an attempted action did not produce the intended result.

It should use environmental evidence to:

```text
verify success
diagnose failure
retry differently
replan
clarify
or request intervention
```

rather than repeatedly issuing the same failing action.

---

## Proof Point 8: Learning from experience

After accumulating successful and failed trajectories, the system should extract reusable procedural knowledge.

A later related task should retrieve that knowledge as guidance and execute more effectively while remaining adaptive to the current environment.

---

# Long-Term Success Criteria

OS Agent should eventually demonstrate all of the following:

```text
A user expresses a goal naturally.

The system understands the goal.

The system determines whether planning is useful.

Relevant prior skills are retrieved when appropriate.

The agent maintains useful working context during long tasks.

The agent observes the actual computer.

The agent selects semantic actions.

Policy evaluates their consequences.

The user is involved when approval,
clarification, or intervention is necessary.

The agent visibly operates the computer.

The agent observes what actually happened.

The agent verifies progress using environmental evidence.

Failures lead to bounded recovery or replanning.

Successful and failed trajectories become learning signals.

Reusable procedures improve future execution.

Telemetry measures behavior, cost, latency,
reliability, and human involvement.

The system remains general across applications
rather than becoming a collection of app-specific bots.
```

The ultimate goal is not merely:

> An LLM that can click buttons.

The goal is:

> **A general, observable, safe, adaptive computer-use agent that can plan, act, verify, collaborate with humans, learn from experience, and become more capable over time while operating the user's real computer.**