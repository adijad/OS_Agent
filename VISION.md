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

The agent should interpret the goal, create an explicit execution run, observe the current computer state, decide what to do, visibly operate the computer, observe the result, preserve meaningful execution state, and continue until the goal reaches a verified terminal outcome.

The computer is the environment.

Applications, websites, files, dialogs, windows, controls, and other visible interfaces are all parts of that environment.

The long-term system should not merely be an LLM capable of issuing mouse and keyboard commands.

It should become a general computer-use agent with:

```text
real computer perception
        +
semantic tool use
        +
durable execution state
        +
policy and human control
        +
working memory
        +
hierarchical planning
        +
verification and recovery
        +
episodic experience
        +
procedural learning
        +
systematic observability and evaluation
```

---

# Core Interaction Model

A natural-language goal should create an explicit agent run.

Conceptually:

```text
USER GOAL
    ↓
RUN CREATED
    ↓
Understand intent
    ↓
Retrieve relevant prior experience / skills when useful
    ↓
Form or update a semantic plan when useful
    ↓
STEP STARTED
    ↓
Observe current computer
    ↓
Reason about current state
    ↓
Choose next semantic action
    ↓
Policy evaluation
    ↓
Act using the computer
    ↓
Observe real outcome
    ↓
Verify progress
    ↓
Update execution state
    ↓
Update working context / adapt / replan
    ↓
STEP COMPLETED
    ↓
Persist meaningful execution state
    ↓
Continue until terminal outcome
```

The computer remains the source of truth throughout execution.

The system must not assume that an action succeeded merely because the action was issued.

Likewise, after process recovery or human intervention, persisted agent state must never override the current real computer state.

The agent must re-observe reality and reconcile its prior knowledge with the environment that actually exists.

---

# Visible Computer Use

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

However, semantic information supports computer use rather than replacing it with hidden application-specific business APIs.

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

This allows the system to use semantic controls when available while still reasoning visually when accessibility information is incomplete.

The purpose of the agent is visible computer operation.

A browser is another application.

A website is another environment presented through that application.

A native Windows application is another environment.

The architecture should remain general across all of them.

---

# General Computer Tasks

The system is not tied to a particular application or website.

Goals may range from simple local operations to long, multi-application workflows.

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


LONGER STATEFUL TASK

"Find three suitable roles based on my requirements,
collect the important details,
compare them,
and prepare application material for the best one."
```

The same high-level architecture should operate across all of these environments.

---

# Canonical Agent Design Patterns

OS Agent should not adopt every popular agent pattern equally.

The following patterns define the intended long-term architecture.

| Pattern | Role in OS Agent | Architectural Status |
| --- | --- | --- |
| Tool Use / Function Calling | Operate the real computer through semantic actions | Core and foundational |
| Execution Runtime | Represent runs, steps, state transitions, persistence, and lifecycle | Core and foundational |
| Hierarchical Planning | Decompose long or multi-application goals into semantic subgoals | First-class for complex tasks |
| Memory and Context Management | Maintain useful task state and learn across experiences | First-class |
| Verification and Recovery | Ground success in environmental evidence and recover from failures | First-class |
| Policy and Human Control | Prevent unsafe or unintended consequential actions | Mandatory control plane |
| Orchestrator / Workers | Isolate specialized cognitive workloads when demonstrated useful | Optional, later-stage |

The mature OS Agent should therefore be understood primarily as:

```text
Tool-Using Computer Agent
          +
Durable Execution Runtime
          +
Hierarchical Semantic Planning
          +
Working / Episodic / Procedural Memory
          +
Environment-Grounded Verification and Recovery
          +
Policy and Human Control
          +
Observability and Evaluation
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

The runtime should provide generic capabilities.

The model should provide task-specific intelligence.

---

# Execution Runtime

As OS Agent progresses from short interactive tasks toward longer, stateful computer workflows, execution must become a first-class architectural abstraction.

A user goal should create an explicit **Run**.

That run progresses through **Steps**.

Meaningful changes during execution produce structured **Events**.

The execution runtime defines:

```text
What task exists?

What state is the task in?

What step is active?

What work has already happened?

What action is being attempted?

What outcome was observed?

Is the task running?

Is it waiting for a human?

Did it complete?

Did it fail?

Can it safely continue?
```

This information should not exist only inside an in-memory Python call stack.

---

## Runtime Is Different From Telemetry

Execution runtime and observability are closely related, but they serve different purposes.

```text
Execution Runtime

What task is this?

What state is it in?

What work has completed?

What happened semantically?

What can safely happen next?


OpenTelemetry

What happened operationally?

How long did it take?

Which subsystem was slow?

Where did errors occur?

How many resources were consumed?
```

Telemetry observes execution.

The runtime defines execution.

OpenTelemetry must therefore not become the primary persistence layer for agent state.

A Grafana trace is not a substitute for knowing whether a task is currently waiting for approval.

---

# Runtime v0

The first execution-runtime implementation should remain intentionally small.

The initial abstractions should be:

```text
Run
Step
Event
Status
Outcome
Timestamps
```

Conceptually:

```text
Run
├── run_id
├── goal
├── status
├── created_at
├── started_at
├── completed_at
├── current_step
├── outcome
└── events
```

A step may contain:

```text
Step
├── step_id
├── run_id
├── number
├── status
├── started_at
├── completed_at
├── proposed_action
└── outcome
```

An event may contain:

```text
RuntimeEvent
├── event_id
├── run_id
├── step_id
├── type
├── timestamp
└── structured data
```

The exact schema should evolve from implementation experience rather than attempting to model every future concept immediately.

---

# Initial Runtime Persistence

Runtime v0 should introduce local persistence from the beginning.

The initial persistence layer does not require distributed infrastructure.

A local SQLite store is sufficient while execution semantics are being established.

Conceptually:

```text
AgentLoop
    ↓
Execution Runtime
    ↓
SQLite Run Store
```

The purpose is to make concepts such as:

```text
run identity
run status
steps
events
timestamps
terminal outcomes
```

survive beyond transient Python variables.

The runtime database should be treated as execution infrastructure rather than user memory.

A local database file should not be committed to the repository.

---

# Run Lifecycle

A run represents one user goal from creation through terminal outcome.

Initial statuses may include:

```text
CREATED
RUNNING
COMPLETED
FAILED
BLOCKED
CANCELLED
MAX_STEPS_REACHED
```

As HITL is introduced, additional valid states should include:

```text
WAITING_FOR_APPROVAL
WAITING_FOR_USER
PAUSED_FOR_INTERVENTION
```

Conceptually:

```text
CREATED
    ↓
RUNNING
    ↓
WAITING_FOR_APPROVAL
    ↓
RUNNING
    ↓
WAITING_FOR_USER
    ↓
RUNNING
    ↓
COMPLETED
```

These are execution states.

They should not be inferred from whether a Python function is currently blocking or running.

A task waiting for a user is still a valid task.

It is not necessarily an error.

---

# Runtime Events

Execution should produce meaningful semantic runtime events.

Examples may include:

```text
RUN_CREATED
RUN_STARTED

STEP_STARTED

OBSERVATION_CAPTURED

MODEL_REQUESTED
ACTION_PROPOSED

POLICY_ALLOWED
POLICY_BLOCKED
APPROVAL_REQUESTED
APPROVAL_GRANTED
APPROVAL_REJECTED

ACTION_STARTED
ACTION_COMPLETED
ACTION_FAILED

VERIFICATION_SUCCEEDED
VERIFICATION_FAILED

RETRY_SCHEDULED

RUN_PAUSED
RUN_RESUMED

STEP_COMPLETED

RUN_COMPLETED
RUN_FAILED
```

Runtime events should represent meaningful lifecycle transitions.

They should not become another low-level logging framework.

Implementation details belong in logs and telemetry.

Runtime events describe what happened to the agent task.

---

# Runtime and OpenTelemetry Correlation

Runtime concepts should map naturally to telemetry.

For example:

```text
Runtime                    Telemetry

Run               →       os_agent.run

Step              →       os_agent.step

Observation       →       computer.observe

Model decision    →       model.choose_action

Policy decision   →       policy.check

Action execution  →       executor.execute

Verification      →       verifier.verify
```

Runtime identifiers should eventually be attached to relevant telemetry:

```text
os_agent.runtime.run_id
os_agent.runtime.step_id
```

This allows an operational trace in Grafana to be correlated with the persisted semantic execution history.

The systems remain distinct:

```text
SQLite runtime state
= semantic execution lifecycle

OpenTelemetry
= traces, metrics, latency, resource consumption
```

---

# Durable Execution Direction

Runtime v0 establishes execution semantics and persistence.

It does **not** yet claim full crash-safe resumability.

True durable execution requires stronger semantics around:

```text
checkpointing
action attempts
uncertain effects
reconciliation
idempotency
retry behavior
crash boundaries
resume behavior
```

These capabilities should be added incrementally after policy, HITL, and verification provide the information necessary to implement them safely.

---

# Checkpoint and Resume

Long-running execution should eventually support checkpoints.

Conceptually:

```text
RUNNING
   ↓
STEP 17 COMPLETE
   ↓
CHECKPOINT
   ↓
process terminates
   ↓
runtime restarts
   ↓
load checkpoint
   ↓
re-observe computer
   ↓
reconcile persisted knowledge
with current environment
   ↓
continue safely
```

Resume must never blindly assume that the external computer remained unchanged.

Persisted state records:

```text
what the agent previously believed

what the agent attempted

what outcomes were previously observed
```

The current computer determines:

```text
what is true now
```

The real environment remains authoritative.

---

# Side-Effect Safety

Computer actions can have real consequences.

Execution recovery must therefore distinguish:

```text
Action proposed

Action authorized

Action issued

Execution result recorded

Effect observed

Effect verified
```

These are not equivalent states.

For example:

```text
Agent clicks "Submit"
        ↓
Application performs submission
        ↓
OS Agent crashes before recording success
```

After restart, blindly repeating the click may produce a duplicate side effect.

Future runtime versions should therefore evolve toward concepts such as:

```text
action identifiers
attempt identifiers
execution status
effect reconciliation
verification before retry
idempotency where possible
bounded retry policies
```

The system must never assume an action failed merely because the runtime failed to persist its result.

It must also never assume that an action succeeded merely because it was issued.

Environmental verification remains essential.

---

# Attempts and Recovery

As verification and recovery mature, one semantic action may have multiple attempts.

Conceptually:

```text
ACTION
  ↓
ATTEMPT 1
  ↓
observe
  ↓
verification failed
  ↓
diagnose
  ↓
ATTEMPT 2
  ↓
observe
  ↓
verification succeeded
```

Attempts should eventually become distinguishable so the system can measure:

```text
retry rate
recovery success rate
failure categories
repeated-action rate
time to recovery
verification failures
possible duplicate side effects
```

This abstraction should not be introduced before verification and recovery semantics exist.

---

# Replay and Inspection

Completed and failed runs should eventually be inspectable.

For example:

```text
Run: run_01ABC

Goal:
"Find the assignment PDF and add its deadline to my calendar."

Status:
COMPLETED

Steps:
1. Opened file browsing environment
2. Located candidate PDF
3. Verified document
4. Read deadline
5. Opened Calendar
6. Requested approval
7. Created event
8. Verified event
```

Replay initially means reconstructing execution history for:

```text
debugging
evaluation
incident analysis
learning
```

Replay does not automatically mean physically executing the actions again.

The system should distinguish:

```text
inspect historical execution

simulate reasoning from recorded observations

re-run model decisions

re-execute actions in a live environment
```

Each has different safety and reproducibility requirements.

---

# Memory Architecture

Memory is not a single subsystem.

OS Agent should distinguish execution state from three different forms of agent memory.

```text
Execution State
= what is happening to this run

Working Memory
= what information matters during this task

Episodic Memory
= what happened during previous tasks

Procedural Memory
= what reusable strategies were learned
```

These concepts may interact, but they must not collapse into one generic memory database.

---

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
Runtime provides generic memory capability
            ↓
Model decides what is worth remembering
            ↓
Information remains available during the run
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

What information must survive beyond recent action history?
```

Working memory may be persisted later as part of resumable runtime state, but it remains conceptually distinct from execution lifecycle state.

---

# Episodic Memory

Episodic memory records what actually happened during a particular task.

A persisted runtime history may later become one source for episodic-memory construction.

However:

```text
Runtime history
≠ automatically episodic memory
```

Runtime records are operational execution evidence.

Episodic memory is a curated representation of experience useful to future reasoning.

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

Episodic memory should preserve experience without assuming every successful behavior should automatically become a reusable skill.

---

# Procedural Memory

A successful experience may be generalized into a reusable strategy.

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

The memory architecture therefore remains:

```text
Execution State
= what is happening now

Working Memory
= what matters now

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

The agent can retrieve the previous file-finding skill and use it as a strong prior while still observing and reasoning about the current situation.

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

Skills should evolve through additional experience.

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

Skills may eventually track:

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

Avoid rigid plans such as:

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

does not require an elaborate plan.

But:

```text
"Find the PDF I downloaded yesterday,
read the deadline,
and add it to my calendar."
```

benefits from decomposition.

Initially, whether decomposition is useful should preferably be model-driven rather than encoded as a brittle deterministic classifier.

A user goal may also require multiple learned skills.

For example:

```text
find_recent_file
        ↓
open_file
        ↓
read_document
        ↓
answer_user
```

The planner should determine whether:

```text
one existing skill solves the goal

multiple skills should be composed

a skill is only partially useful

or no useful skill exists and full reasoning is required
```

Planning must remain adaptive.

After meaningful subgoals, failures, human interactions, or environmental changes, the system may revise the remaining plan rather than blindly executing outdated instructions.

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

## Deterministic Verification

Example:

```text
Does Calculator show the expected completed expression?
```

## Semantic Verification

Example:

```text
Is this actually the resume the user intended?
```

## Model-Assisted Verification

Example:

```text
Does this product satisfy the user's qualitative requirements?
```

Prefer the lowest-cost reliable verifier available.

The system must distinguish:

```text
Action issued
= the runtime attempted the physical action


Executor success
= the executor completed its invocation


Effect observed
= the environment changed


Effect verified
= observed evidence supports the intended consequence


Task success
= sufficient environmental evidence supports completion
```

The model saying:

```text
"I completed the task."
```

is not sufficient evidence on its own.

Recovery should be bounded.

Repeated failures should not produce endless retries.

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

Recovery actions should eventually be recorded through the execution runtime as distinct failures, attempts, and outcomes.

---

# Human-in-the-Loop

Human involvement is a core part of OS Agent rather than an edge case.

There are three distinct forms of human interaction:

```text
Approval
Clarification
Intervention
```

Human interactions should become explicit runtime states and events.

They should not remain merely blocking `input()` calls.

---

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

Approval authorizes the semantic consequence, not arbitrary future physical interaction.

Runtime lifecycle:

```text
RUNNING
    ↓
APPROVAL_REQUIRED
    ↓
WAITING_FOR_APPROVAL
      /             \
 approved          rejected
    ↓                 ↓
RUNNING          continue safely /
                 replan / terminate
```

---

## Clarification

Sometimes the agent can continue technically but does not know what the user intended.

For example:

```text
"I found three files that look like your resume.
Which one should I use?"
```

The runtime may transition:

```text
RUNNING
    ↓
WAITING_FOR_USER
    ↓
USER_RESPONSE_RECEIVED
    ↓
RUNNING
```

Clarification is distinct from approval.

The agent is not necessarily blocked by capability.

The user's intent is ambiguous.

---

## Intervention

The agent may encounter a state it cannot safely or confidently resolve.

The system should allow:

```text
Agent control
      ↓
PAUSED_FOR_INTERVENTION
      ↓
Human takes control
      ↓
Human resolves situation
      ↓
Agent resumes
      ↓
Fresh observation
      ↓
Reconcile execution state
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

The agent must re-observe after human intervention.

It should never assume what the human changed.

Human actions during intervention may later become useful learning signals.

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
→ ALLOW

click "Place order"
→ APPROVAL_REQUIRED

click "Delete permanently"
→ APPROVAL_REQUIRED or BLOCK depending on context
```

A `click` is not inherently safe or dangerous.

Its meaning depends on what the click will do.

Policy should therefore consider context such as:

```text
current goal
active application
target role
target name
surrounding semantic state
intended effect
runtime state
current task context
```

The initial semantic policy contract should produce:

```text
ALLOW

APPROVAL_REQUIRED

BLOCK
```

Policy outcomes should become runtime events and state transitions.

For example:

```text
ACTION_PROPOSED
       ↓
POLICY
   /     |      \
ALLOW APPROVAL  BLOCK
  │      │        │
  │      │        └── RUN may become BLOCKED
  │      │
  │      └── RUN becomes WAITING_FOR_APPROVAL
  │
  └── executor may proceed
```

The planner, memory system, learned skills, model, and optional future workers must never bypass the policy layer.

Broad access to a computer is not blanket permission to perform every available action.

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

Examples might include:

```text
Research worker
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

It makes the behavior of the system measurable and debuggable.

OS Agent now uses hierarchical OpenTelemetry traces corresponding to the real execution structure:

```text
os_agent.run
    │
    ├── os_agent.step
    │     ├── os_agent.computer.observe
    │     ├── os_agent.model.choose_action
    │     ├── os_agent.policy.check
    │     └── os_agent.executor.execute
    │
    ├── os_agent.step
    │     └── ...
    │
    └── completion
```

The system records operational information such as:

```text
run status
steps
model calls
provider
model
token usage
cached tokens
reasoning tokens
model latency
observation latency
policy latency
executor latency
executed actions
action type
execution status
total run latency
```

OpenTelemetry metrics aggregate behavior across runs.

Telemetry is exported through OTLP into a local observability stack containing:

```text
OpenTelemetry Collector
Tempo
Prometheus
Grafana
```

The project includes a Grafana engineering dashboard for run, model, token, action, and latency metrics.

The observability stack exists to answer questions such as:

```text
How long do tasks take?

Where does task latency come from?

How many model calls does a task require?

How many tokens are used?

Which action types are expensive?

Which models require fewer steps?

How frequently do tasks succeed?

Where do retries occur?

How frequently are approvals required?

How often does verification catch false completion?

Does planning improve performance?

Does memory reduce repeated reasoning?
```

Telemetry should remain metadata-first and privacy-conscious.

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

Environment-grounded evaluation remains the source of truth for benchmark success.

A model claiming completion is not sufficient evidence.

---

# Evaluation Philosophy

OS Agent should evaluate the entire interaction loop rather than only LLM output quality.

Relevant measurements may include:

```text
task success rate
steps per task
model calls
tokens
latency
action failures
grounding failures
repeated actions
retries
recovery success
verification failures
human interventions
approval frequency
cost
```

Model comparisons should use the same tasks and the same environmental success criteria.

A small benchmark indicating that one model performed better than another does not establish universal superiority.

Architecture decisions should be driven by repeated evaluation rather than anecdotal impressions.

---

# Canonical Architectural Direction

The long-term architecture should evolve toward:

```text
                              USER GOAL
                                  │
                                  ▼
                           EXECUTION RUNTIME
                         create / persist run
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
                      │            │            │
                      │          HUMAN          │
                      │            │            │
                      └──────┬─────┘            │
                             ▼                  │
                          EXECUTOR              │
                             │                  │
                             ▼                  │
                       REAL COMPUTER            │
                             │                  │
                             ▼                  │
                        OBSERVATION              │
                             │                  │
                             ▼                  │
                          VERIFIER               │
                        /          \             │
                   success        failure        │
                      │              │           │
                      ▼              ▼           │
                next subgoal    recover / replan│
                      │              │           │
                      └──────┬───────┘           │
                             ▼                   │
                      RUNTIME STATE UPDATE ◄─────┘
                             │
                             ▼
                         CHECKPOINT
                       when appropriate
                             │
                             ▼
                      TERMINAL OUTCOME
                             │
                             ▼
                    EPISODIC TRAJECTORY
                             │
                             ▼
                PROCEDURAL SKILL LEARNING
```

OpenTelemetry and evaluation surround this architecture as an engineering control plane.

The execution runtime sits inside the system because it defines the lifecycle and state of the task itself.

Optional specialized cognitive workers may later sit around planning, research, analysis, or writing workloads.

They do not replace the single controlled computer-execution path.

---

# Architectural Invariants

The following principles should remain stable unless strong experimental evidence justifies changing them.

1. **The computer is the environment.**

2. **Real environmental state is the source of truth for current reality and task completion.**

3. **A user goal corresponds to an explicit execution run.**

4. **Execution state should not depend solely on an in-memory Python call stack.**

5. **Persisted execution state records previous knowledge and attempts, not guaranteed current environmental truth.**

6. **After recovery or human intervention, the agent must re-observe the computer before continuing.**

7. **The model proposes semantic actions rather than brittle coordinates or vendor-specific automation syntax whenever possible.**

8. **The runtime provides generic capabilities. The model provides task-specific reasoning.**

9. **Do not create application-specific agents or hardcoded application workflows by default.**

10. **Planning describes semantic subgoals, not rigid click sequences.**

11. **Working memory must remain generic rather than becoming deterministic domain-specific task state.**

12. **Execution state, working memory, episodic memory, and procedural memory are distinct systems.**

13. **Learned procedures guide execution. They do not become blind macro replay.**

14. **Policy and human control cannot be bypassed by planning, memory, tools, workers, or learned skills.**

15. **An issued action and a verified environmental effect are different states.**

16. **Retries must consider whether a previous action may already have produced a side effect.**

17. **Verification should prefer real environmental evidence over model self-claims.**

18. **Human waiting states are valid execution states rather than automatic failures.**

19. **Telemetry observes execution but does not replace the execution-state store.**

20. **Physical desktop mutation remains serialized even if specialized cognitive workers are introduced later.**

21. **New architectural complexity should be justified by evaluation and telemetry rather than added because a pattern appears sophisticated.**

22. **Model/provider specialization should be evidence-driven. Logical roles do not automatically require separate LLMs.**

23. **The system should remain adaptive to the current computer state rather than assuming previous environments still apply.**

24. **Distributed execution should only be introduced when local execution semantics are stable and evaluation demonstrates a need.**

---

# Canonical Implementation Order

The architecture above describes the destination.

The following sequence defines the intended implementation order.

This ordering is canonical so future work does not accidentally jump ahead or replace general mechanisms with task-specific shortcuts.

---

## 1. Tool Use / OS Interaction Foundation

```text
Reliable Windows observation
Screenshots and UI Automation
Semantic action schema
Mouse / keyboard / application control
Application lifecycle awareness
Observe → reason → act execution loop
Multiple model-provider abstraction
Environment-grounded evaluation
```

**Status: Established foundation**

---

## 2. Observability and Evaluation v1

```text
OpenTelemetry traces
Provider and model metadata
Token usage
Model latency
Run-level latency
Hierarchical run / step traces
Observation timing
Policy timing
Executor timing
Metrics
OTLP export
Tempo traces
Prometheus metrics
Grafana visualization
Environment-grounded benchmarks
```

**Status: Complete**

---

## 3. Execution Runtime v0

```text
Explicit Run abstraction
Explicit Step abstraction
Structured runtime Events
Run and step identifiers
Run statuses
Step statuses
Timestamps
Outcomes
Local SQLite persistence
Basic run inspection
Runtime IDs correlated with OpenTelemetry
```

The objective is to define OS Agent execution semantics.

Runtime v0 does not yet promise crash-safe resume.

**Status: Current phase**

---

## 4. Policy Engine v1

```text
Semantic risk evaluation
Consequence-aware decisions

ALLOW

APPROVAL_REQUIRED

BLOCK

Safety boundary independent of model reasoning
Policy decisions recorded as runtime events
```

---

## 5. Human-in-the-Loop v1

```text
Approval
Clarification
Intervention

WAITING_FOR_APPROVAL
WAITING_FOR_USER
PAUSED_FOR_INTERVENTION

Semantic approval rather than coordinate approval
Fresh observation after human actions
Runtime-aware human interaction
```

---

## 6. Runtime Pause / Resume Semantics

```text
Run pause
Run resume
Human waiting states
Persisted paused state
Resume entry point
Fresh observation on resume
Runtime reconciliation
```

This is not yet full crash recovery.

It establishes intentional pause and continuation semantics.

---

## 7. Working Memory and Context Management

```text
Generic task blackboard
Important discoveries
Collected evidence
Unresolved failures
Active subgoal
Remaining work
Compact model context for long trajectories
Avoid deterministic domain-specific state
```

---

## 8. Hierarchical Planning

```text
Semantic task decomposition
Optional planning for complex goals
Adaptive replanning
Subgoal management
Skill composition
No rigid click-by-click plans
```

---

## 9. Verification and Recovery

```text
Environment-grounded outcome verification
Deterministic verification when possible
Semantic verification when required
Model-assisted verification when necessary

Bounded retries
Failure diagnosis
Alternate strategies
Replanning
Clarification
Intervention
```

The runtime should begin distinguishing failures and recovery attempts here.

---

## 10. Advanced Runtime Durability

```text
Checkpoint creation
Checkpoint loading
Crash recovery
Attempt identifiers
Action identifiers
Side-effect uncertainty
Effect reconciliation
Verification before retry
Bounded retry policies
Safe resume
```

Durability should be introduced only after verification and policy provide enough information to resume safely.

---

## 11. Episodic Trajectory Construction

```text
Construct meaningful task experiences from runtime history

Goal
Observations
Actions
Policy events
Working-memory updates
Human interactions
Verification results
Failures
Retries
Completion evidence
Final outcome
```

Build a learning dataset from real execution.

---

## 12. Procedural Skill Learning

```text
Extract generalized reusable strategies
Avoid brittle macro replay
Track successful and failed uses
Track confidence
Refine procedures through experience
```

---

## 13. Skill Retrieval and Composition

```text
Retrieve relevant procedures semantically
Use procedures as priors rather than scripts
Compose multiple skills for complex goals
Adapt retrieved knowledge to the current environment
```

---

## 14. Replay and Long-Running Execution

```text
Inspect historical runs
Replay reasoning from captured state where appropriate
Compare historical decisions
Support longer persisted workflows
Improve crash resilience
Investigate safe live re-execution only where justified
```

Physical-action replay should never be treated as equivalent to historical inspection.

---

## 15. Optional Specialized Cognitive Workers

```text
Introduce only for demonstrated specialization needs
Separate cognitively different workloads when beneficial
Allow different models where telemetry justifies it
Keep physical computer control serialized
```

---

# Do Not Jump Ahead

The presence of a later-stage capability in the long-term architecture does not mean it should be implemented before its prerequisites.

In particular:

```text
Do not build sophisticated crash recovery
before execution semantics, policy, and verification exist.

Do not build long-term procedural memory
before working memory and reliable trajectories exist.

Do not add powerful long-horizon planning
before policy and human control are established.

Do not add multi-agent workers
merely to make the architecture look more advanced.

Do not replace generic computer use
with application-specific agents
when a general capability can solve the problem.

Do not introduce deterministic task-state schemas
for domains such as shopping,
job searching,
email,
or file management.

Do not treat model-declared success
as proof that a real-world task succeeded.

Do not use OpenTelemetry
as the persistence layer for execution state.

Do not assume a missing action result means
that a real-world side effect did not occur.

Do not introduce distributed queues,
workflow engines,
or orchestration systems
before the local runtime demonstrates a concrete need.
```

---

# Current Development Position

The project has established the Tool Use / OS Interaction foundation.

Current computer-use capabilities include:

```text
Windows desktop observation
Active-window observation
UI Automation controls
Screenshot perception
Semantic target IDs
UI control values

Visible mouse interaction
Literal text input
Special keys
Structured hotkeys
Application opening
Application focusing

Application lifecycle reasoning
Semantic action validation
Action execution

Natural-language agent loop

OpenAI provider
Anthropic provider

Cross-model evaluation
Environment-grounded Calculator evaluation

Browser interaction
```

The project has also completed **Observability v1**.

Current observability capabilities include:

```text
One coherent trace per user goal

os_agent.run
    ↓
os_agent.step
    ↓
computer.observe
model.choose_action
policy.check
executor.execute

Provider / model telemetry

Input tokens
Output tokens
Total tokens
Cached tokens
Reasoning tokens

Model latency
Observation latency
Policy latency
Executor latency
Total run latency

Run-level aggregation

OpenTelemetry metrics

OTLP export

OpenTelemetry Collector

Tempo traces

Prometheus metrics

Grafana engineering dashboard

Docker Compose observability environment
```

The current development phase is:

```text
PHASE 3

EXECUTION RUNTIME V0
```

The immediate objective is:

```text
USER GOAL
    ↓
CREATE RUN
    ↓
Persist run identity and status
    ↓
STEP
    ↓
Persist meaningful execution events
    ↓
Terminal outcome
    ↓
Persist final run state
```

The first runtime version should remain intentionally small:

```text
Run
Step
Event
Status
Outcome
Timestamps
SQLite persistence
Basic inspection
Telemetry correlation
```

After Runtime v0 is stable:

```text
Policy Engine v1
        ↓
Human-in-the-Loop v1
        ↓
Runtime pause / resume
        ↓
Working Memory
        ↓
Hierarchical Planning
        ↓
Verification / Recovery
        ↓
Advanced Runtime Durability
        ↓
Episodic Trajectories
        ↓
Procedural Learning
```

---

# Runtime Evolution

The runtime should evolve incrementally rather than attempting full durability immediately.

```text
Runtime v0
Execution semantics + persistence
        ↓
Runtime v1
HITL lifecycle + intentional pause/resume
        ↓
Runtime v2
Verification-aware checkpoint/recovery
        ↓
Runtime v3
Attempts + side-effect reconciliation
        ↓
Runtime v4
Replay + long-running execution
```

Each version should be justified by capabilities that already exist.

---

# Development Philosophy

Build bottom-up and preserve generality.

First give the system reliable eyes and hands.

Then make the observe -> reason -> act loop measurable.

Then define what an execution run actually is.

Then establish semantic safety and human control before increasing autonomy.

Then add generic working memory.

Then add hierarchical planning.

Then add environment-grounded verification and recovery.

Then strengthen durability using the execution evidence now available.

Then construct episodic trajectories.

Then learn procedural skills from real experience.

Only introduce specialized cognitive workers if a demonstrated workload justifies the complexity.

Avoid hiding the computer-use problem behind:

```text
application-specific APIs
large agent frameworks
workflow engines
multi-agent abstractions
distributed systems
```

before the underlying execution semantics are understood.

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
durable
inspectable
verifiable
safe
adaptive
human-controllable
and aware of the real computer it is operating
```

---

# Major Proof Points

## Proof Point 1: Generic Application Execution

> A user types "Open Notepad and write Hello World."

The system should determine what to do from the natural-language goal and the observed Windows environment without a hardcoded Notepad workflow.

---

## Proof Point 2: Cross-Application Generality

> A user types "Open Calculator and calculate 913 × 47."

The same agent architecture should accomplish the goal without a Calculator-specific workflow being programmed in advance.

---

## Proof Point 3: Browser Research With Grounded Evidence

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

without introducing browser-specific intelligence architecture.

---

## Proof Point 4: Observable Execution

A user goal should produce one inspectable trace showing:

```text
run
steps
observations
model decisions
policy checks
executor operations
latency
token usage
final outcome
```

Operational metrics should be viewable through the OS Agent Grafana dashboard.

---

## Proof Point 5: Explicit Persistent Run

A user goal should create a runtime record with:

```text
run ID
status
steps
events
timestamps
outcome
```

The semantic history of execution should remain inspectable after `AgentLoop.run()` returns.

---

## Proof Point 6: Safe Consequential Action

The agent should be able to reach a consequential action such as:

```text
send email
place order
delete file
submit form
```

then pause before execution, describe the semantic consequence, request approval, and correctly handle approval or rejection.

The runtime should represent the waiting state explicitly.

---

## Proof Point 7: Runtime-Aware Human Interaction

The agent should be capable of becoming:

```text
WAITING_FOR_APPROVAL
WAITING_FOR_USER
PAUSED_FOR_INTERVENTION
```

without treating those states as task failure.

After human action, the agent should re-observe the environment before resuming.

---

## Proof Point 8: Generic Long-Horizon Working Memory

The agent should complete a task requiring information to survive across many steps without introducing a domain-specific task-state schema.

For example:

> Find several suitable products, compare them, and return the verified results and direct links.

or:

> Find the PDF I downloaded yesterday, determine the deadline, and add it to my calendar.

---

## Proof Point 9: Adaptive Planning

The agent should decompose a complex goal into semantic subgoals while continuing to react to the real environment.

If the environment changes or a planned route fails, it should revise the plan instead of blindly executing an outdated script.

---

## Proof Point 10: Verification and Recovery

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

## Proof Point 11: Safe Recovery After Interrupted Execution

A later runtime version should be able to recover from interrupted execution without blindly replaying prior actions.

Recovery should:

```text
load persisted execution state
re-observe the real computer
determine whether previous effects occurred
reconcile prior state with current reality
continue only when safe
```

---

## Proof Point 12: Learning From Experience

After accumulating successful and failed trajectories, the system should extract reusable procedural knowledge.

A later related task should retrieve that knowledge as guidance and execute more effectively while remaining adaptive to the current environment.

---

# Long-Term Success Criteria

OS Agent should eventually demonstrate all of the following:

```text
A user expresses a goal naturally.

The goal creates an explicit durable run.

The runtime knows the lifecycle state of that run.

The system determines whether planning is useful.

Relevant prior skills are retrieved when appropriate.

The agent maintains useful working context during long tasks.

The agent observes the actual computer.

The agent selects semantic actions.

Policy evaluates their consequences.

The user is involved when approval,
clarification, or intervention is necessary.

Human waiting states remain valid persisted run states.

The agent visibly operates the computer.

Actions and attempts are distinguishable.

The agent observes what actually happened.

The agent verifies progress using environmental evidence.

Failures lead to bounded recovery or replanning.

Interrupted execution can eventually resume safely.

Persisted runtime state never overrides fresh environmental truth.

Successful and failed executions become episodic learning signals.

Reusable procedures improve future execution.

Telemetry measures behavior, cost, latency,
reliability, recovery, and human involvement.

Runtime state remains distinct from telemetry and memory.

The system remains general across applications
rather than becoming a collection of app-specific bots.

Physical desktop mutation remains serialized.

Architectural complexity is introduced only when
evaluation demonstrates that it solves a real problem.
```

The ultimate goal is not merely:

> An LLM that can click buttons.

It is not merely:

> A workflow engine connected to an LLM.

It is not merely:

> A collection of application-specific automation scripts.

The goal is:

> **A general, observable, durable, safe, adaptive computer-use agent that can understand goals, maintain execution state, plan, operate the user's real computer, verify real-world outcomes, collaborate with humans, recover from failure, learn from experience, and become more capable over time.**