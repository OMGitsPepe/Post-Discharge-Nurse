# Post-Discharge Nurse

**Pedro E. Perez**
October 4, 2026

## 1 Problem Formalization

The proposed project is a post-discharge monitoring agent that follows a simulated patient after leaving the hospital. 
The first version of the system will focus on a patient discharged after an acute non-ST segment elevation myocardial 
infarction (NSTEMI). The patient record will be generated using Synthea and will provide the initial hospital and 
discharge information needed by the agent.

The agent will begin operating after the patient has already been discharged. Its goal is not to diagnose the patient, 
prescribe treatment, or decide when the patient is ready to leave the hospital. Instead, the agent will monitor the 
patient's recovery during the first seven days after discharge. It will ask about symptoms, medication adherence and 
general recovery, maintain a history of the patient's responses, ask follow-up questions when information is incomplete 
and escalate concerning situations to a human clinician.

### 1.1 PEAS

**Performance measure:**

The agent will be evaluated based on whether it maintains an accurate internal state of the patient, asks
appropriate follow-up questions, correctly tracks medication adherence, escalates cases when predefined warning 
conditions are met, respects its safety boundaries and properly continues or terminates the follow-up process.

**Environment:**

The environment consists of a simulated post-discharge patient and the patient's synthetic medical record. 
The initial state is constructed from Synthea data, including the reason for hospitalization, relevant medical history, 
procedures performed during the hospitalization and the medications prescribed at discharge. After discharge, 
the environment will simulate daily patient responses and changes in recovery.

**Actuators:**

The agent can ask the patient about symptoms and medication adherence, ask follow-up questions, provide reminders 
that are already part of the discharge plan, continue routine monitoring, escalate the case to a human clinician or 
terminate the follow-up period.

**Sensors:**

The agent receives patient responses about symptoms, recovery and medication adherence. It also has access to the 
initial discharge information provided by the synthetic medical record.

### 1.2 Task Environment

The post-discharge environment is partially observable because the agent cannot directly observe the patient's true 
physical condition. It only receives information that the patient reports and information contained in the available 
medical record. Because the current observation may not contain the complete patient state, the agent must maintain 
an internal representation of the patient's recovery.

The environment is stochastic because the patient's future condition cannot be known with certainty. Even when a 
patient follows the discharge plan and takes the prescribed medications, symptoms may improve, remain unchanged, or worsen.

The environment is sequential because observations and actions from previous check-ins affect later decisions. 
For example, a report of fatigue may have a different meaning if previous check-ins show that the fatigue has been 
progressively worsening. Therefore, history is necessary for the agent to make appropriate decisions.

The environment is also dynamic because the patient's condition can change as time passes, independently of the 
agent's actions. A patient may improve or develop new or worsening symptoms between daily check-ins.

The implemented environment will be mostly discrete. The first prototype will use daily check-ins during the first 
seven days after discharge and represent important patient information using categories such as improving, unchanged, 
or worsening symptoms and medication taken or missed. Although real patient health can vary continuously, the prototype 
will use a discrete representation to keep the system manageable and evaluable.

Because the environment is partially observable, stochastic, sequential, and dynamic, the agent requires memory. 
The internal state will include previous symptoms, medication-adherence reports, previous follow-up questions and 
answers and prior escalation decisions. This allows the agent to compare current observations with previous check-ins 
and identify changes in the patient's recovery over time.

### 1.3 Sequential Formulation

Let $s_t$ represent the patient's true state at time $t$. This includes the patient's actual symptoms, 
recovery condition and medication adherence.

Let $o_t$ represent the observation available to the agent at time $t$. An observation may include a patient's 
report of symptoms, whether a medication was taken or missed, or an answer to a follow-up question. Because the 
environment is partially observable, $o_t$ may contain only part of the information present in $s_t$.

Let $a_t$ represent the action selected by the agent at time $t$. Possible actions include asking a follow-up 
question, providing an allowed reminder, continuing routine monitoring, escalating the case to a human clinician, 
or terminating the follow-up process.

Finally, $h_t$ represents the history available to the agent up to time $t$, including previous observations and actions:

$$h_t = (o_1, a_1, o_2, a_2, \dots, o_t)$$

The agent uses the current observation together with this history to maintain an internal patient state and 
select it next action. This allows the system to make decisions based on the patient's recovery trajectory rather than 
reacting only to the most recent response.

## 2 Architecture

The proposed system will use a single hybrid model-based and goal-directed agent. A model-based architecture is 
appropriate because the post-discharge environment is partially observable and sequential. The agent cannot directly 
observe the patient's complete health condition and must instead maintain an internal state based on the patient's 
previous responses, reported symptoms, medication adherence and earlier interactions. This internal state allows 
the agent to compare new observations with previous check-ins and identify changes in the patient's recovery over time.

The agent is also goal-directed because its actions are selected according to the overall goal of safely monitoring 
the patient after discharge. The agent must decide whether to ask another question, continue routine follow-up, provide 
an allowed reminder, escalate the case to a clinician or terminate the follow-up period. These actions are chosen based 
on the patient's current information and history rather than only reacting to the most recent response.

The architecture will combine generative AI and classical deterministic components. The generative component will be 
used where natural-language flexibility is useful, such as interpreting free-text patient responses, generating 
appropriate follow-up questions and creating a summary when a case is escalated. The classical component will maintain 
the structured patient state, track medication adherence and symptom history, enforce the set of allowed actions, 
apply predefined escalation criteria, control the follow-up schedule and determine when the monitoring period should end. 
The generative component will not diagnose the patient, recommend treatment, change medication or create its own escalation rules.

A simple reflex agent was considered as an alternative architecture. A reflex agent could respond to the patient's 
current observation using predefined rules, but it would not adequately support this environment because the meaning 
of a current response may depend on previous observations. For example, a patient reporting fatigue has progressively 
worsened during several daily check-ins. Because the current observation alone is not sufficient, the agent needs an 
internal state and history.

A multi-agent architecture was also considered but is not necessary for the initial prototype. The current problem 
does not require separate agents for symptoms, medication adherence, escalation, or other tasks. These responsibilities 
can be handled by a single agent with structured state and deterministic safety controls. Additional agents, such as a 
medication-integration agent and refile-request-agent, could be considered as future extensions if the system grows in scope.

The initial implementation is expected to use Agno as the agent framework because it supports stateful agents, 
structured workflows and controlled interactions. However, Agno is an implementation choice rather than part of the 
architecture itself. The project will remain centered on the hybrid model-based and goal-directed design regardless of 
the specific framework used.

## 3 Milestone and scope Plan

### 3.1 Prototype

By Module 9, the goal is to have a working prototype of the post-discharge monitoring agent using synthetic patient 
data from Synthea. The first prototype will focus on one NSTEMI patient and will simulate daily follow-up during the 
first seven days after discharge.

The system should be able to construct the patient's initial discharge state from the Synthea record, receive simulated 
patient responses, interpret information about symptoms and medication adherence, update the patient's structured internal 
state and select an appropriate next action. The available actions will include asking follow-up questions, providing 
reminders already contained in the discharge plan, continuing routine monitoring, escalating the case to a simulated 
human clinician or ending the follow-up period.

The prototype should also maintain a history of previous observations and actions so that later decisions can depend 
on the patient's recovery trajectory rather than only the most recent response. The initial implementation is expected 
to use Agno, although the framework may change if another implementation better supports the selected architecture.

### 3.2 Assurance and Evaluation

By Module 12, the working prototype will be expanded with an evaluation and observability process. Multiple simulated 
patient trajectories will be created to test situations such as normal recovery, medication non-adherence, worsening 
symptoms, incomplete or ambiguous responses, and cases that should or should not be escalated.

The complete trajectory of each test case will be recorded so that the system can be evaluated on memory accuracy, 
follow-up question appropriateness, medication-adherence tracking, escalation accuracy, safety-boundary compliance, 
and correct termination of the follow-up process. Failures found during testing will be analyzed to determine where 
they occurred in the agent loop and whether they should be fixed, mitigated, or accepted.

If the NSTEMI implementation works reliably and sufficient time remains, an additional disease or discharge scenario 
may be added to test whether the same architecture can generalize beyond the original patient type.

### 3.3 Scope Reduction

If the project becomes too large to complete within the available time, additional disease or discharge scenarios 
will be removed first and the system will remain focused only on NSTEMI. Appointment tracking and other optional 
discharge-plan features can also be removed while keeping symptom monitoring and medication adherence as the core functions. 
The number of evaluation scenarios may be reduced if necessary, and the system can remain a command-line application 
instead of adding a graphical or web interface.

The core agent loop, structured memory, daily follow-up, and escalation behavior will not be removed because these are 
necessary to demonstrate the sequential and agentic behavior of the system.

### 3.4 Explicitly Out of Scope

The project will not attempt to diagnose patients, recommend treatment, prescribe or change medications, analyze 
medication interactions, or determine whether a patient is ready for hospital discharge. It will not use real patient 
data, connect to a live electronic health record, send real notifications to clinicians, or be presented as a clinically 
validated medical system.

The initial system will also remain a single-agent architecture. Additional specialized agents, such as a 
medication-interaction agent, may be considered as future extensions but are not part of the current project scope.