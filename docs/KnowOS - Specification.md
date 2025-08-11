# ProcOS Specification

This document provides a comprehensive specification for ProcOS, a process-oriented operating system designed to enable users to build and evolve personalized workflows using BPMN (Business Process Model and Notation). ProcOS emphasizes accessibility for generalists through visual process editing, while supporting advanced users with a robust backend. It integrates large language models (LLMs) for probabilistic task execution, deterministic tools for reliability, and an ambient intelligence system (DAS) for dynamic process generation and monitoring. The system starts minimal and grows organically based on user knowledge extracted into BPMN processes.

This spec is structured for use with GitHub Copilot or similar AI coding assistants: Provide prompts like "Implement the microkernel in Python based on this spec section" or "Generate BPMN XML for a TDE template." Use the sections to modularize development, starting with DAS for upfront integration.

## 1. Overview and Vision

- **Name**: ProcOS (Process-Oriented Operating System).
- **Core Concept**: An OS where BPMN processes are the primary units of computation. Users (e.g., traders, engineers, supply chain professionals) extract domain knowledge into editable BPMN workflows, creating tailored "OS variants." The system is "fuzzy" (probabilistic via LLMs) yet reliable (deterministic tools), starting blank and evolving via user inputs.
- **Key Principles**:
  - Accessibility: Visual BPMN editing for non-coders, like tinkering with a 1960s car engine.
  - Simplicity: Everything (orchestrators, executors) is a BPMN process to avoid complexity creep.
  - Probabilistic Nature: Tasks yield multiple weighted outcomes (e.g., A at 80%, B at 15%) with convergence criteria.
  - Knowledge Preservation: Log all iterations, errors, and insights in a vector store for DAS to learn from.
- **Target Users**: Generalists for simple edits; super users for complex backends; scalable across organizations (e.g., military branches sharing context).
- **High-Level Features**:
  - Dynamic process generation via DAS.
  - Scoring processes (e.g., "batting average" for usage/success).
  - Integration with tools like MATLAB, Python, or Docker containers.
  - Support for ontologies (e.g., requirements → components → processes → functions).

## 2. System Architecture

ProcOS uses a microkernel design with BPMN at its core. Components are isolated, scalable, and BPMN-based where possible. Deployment targets: Local (laptop with GPU) or AWS (via CDK for ECS/EKS, Bedrock for LLMs).

### 2.1 Components

- **Microkernel**:
  - Minimal bootstrapper (80–100 lines of Python code).
  - Functions: Initialize Camunda API, vector store, and DAS; monitor Camunda for new process executions; spawn PDOs on detection.
  - No active execution; stays lean and terminates unnecessary resources.

- **Process Definition Orchestrator (PDO)**:
  - BPMN process managing a single workflow instance.
  - Functions: Query Camunda API for process state (current/previous/next tasks); spawn TDEs dynamically for ready tasks (sequential or parallel); handle task priorities from Camunda definitions; update process state in Camunda; terminate on completion.
  - Scalability: One PDO per process instance; lightweight to avoid overhead.

- **Task Definition Executor (TDE)**:
  - Generic BPMN process for individual tasks, powered by LLM.
  - Functions: Receive task from PDO; evaluate input with context-managed prompts; execute probabilistically (iterate until convergence on weighted outcomes) or deterministically (call tools like Python, MATLAB); support container spawning (e.g., Docker for specialized envs); report outcome to PDO; terminate after task.
  - Isolation: No inter-TDE communication; generic template with LLM decision gateway for actions (e.g., route to file write or API call).

- **Digital Assistance System (DAS)**:
  - Ambient intelligence, integrated from startup.
  - Functions: Monitor user interactions, task executions, and system state via vector store; generate BPMN processes from inputs (text/voice, e.g., "Build a process to ingest data and train a model"); suggest refinements (e.g., optimize prompts based on scoring); pre-load a priori memory (sample processes); learn from logs to evolve the system.
  - Interfaces: Text/voice-based; visual BPMN editors (e.g., BPMN.io integration); contextual awareness (e.g., know current page/user action).

- **Vector Store**:
  - Backend: Milvus, Pinecone, or AWS Bedrock Knowledge Bases.
  - Functions: Store BPMN XML, prompts, task logs, errors, outcomes, ontologies, and build iterations; provide context for DAS and TDEs; enable scoring (e.g., track process usage/success rates).

- **Camunda Integration**:
  - BPMN engine for publishing, running, and querying processes.
  - Functions: Handle process definitions (XML); track states (active tasks, parallel splits); API for PDO/TDE interactions.

- **Context Manager**:
  - Tool for human/DAS to craft/test prompts.
  - Functions: Build prompts; test against LLMs (e.g., OpenAI, Ollama); approve/store in vector store; support uncertainty quantification (e.g., Monte Carlo, Bayesian).

### 2.2 Data Flow

1. User triggers BPMN process in Camunda (e.g., via UI or DAS-generated).
2. Microkernel detects and spawns PDO.
3. PDO queries Camunda for tasks; spawns TDE(s) for each (parallel if needed).
4. TDE executes task (LLM probabilistic or tool deterministic); logs to vector store.
5. TDE reports to PDO; PDO updates Camunda.
6. DAS monitors/logs; generates/suggests processes as needed.
7. Process completes; PDO/TDEs terminate.

### 2.3 Low-Level Processes (Starting Set)

Build these as BPMN templates in vector store for DAS to generate/expand:
- File Operations: Create, Read, Update, Delete, Move/Copy.
- Directory Operations: Create, List, Delete.
- Memory Operations: Allocate, Read, Write, Free.
- Disk Operations: Write, Read, Check Space.
- Network Operations: Send/Receive API Request, Open/Close Connection.
- Process Management: Start, Terminate, Monitor.
- System Queries: Check Resources, Get Info.

Each is a simple BPMN flow (e.g., "Create File": Validate path → Write data → Confirm).

## 3. Functional Requirements

- **Process Execution**:
  - Support sequential/parallel tasks with feedback loops.
  - Probabilistic: Run until convergence (e.g., stabilize on multi-path outcomes); use Bayesian/Monte Carlo for quantification.
  - Deterministic: Integrate tools (e.g., MATLAB, Scilab, ANSYS) via script tasks or containers.

- **DAS Capabilities**:
  - Generate BPMN from inputs (e.g., "Process for aircraft bootstrapping").
  - Monitor 24/7; offer suggestions (e.g., "Refine this task?"); build in sandbox for testing.
  - Scale across users/organizations with shared vector store context.

- **Scoring and Optimization**:
  - Track process metrics (usage, success rate); feed into DAS for auto-optimization or user visibility.

- **Ontologies and Advanced Features**:
  - Support first-order ontology: Requirements → Components → Processes → Functions (with constraints/interfaces).
  - Bootstrap complex systems (e.g., conceptualize aircraft from requirements in minutes).

- **User Interfaces**:
  - BPMN Editor: Integrate BPMN.io or React Flow for visual building.
  - DAS Interaction: Text/voice; contextual (e.g., know current BPMN edits and suggest XML changes).

- **Security and Reliability**:
  - Isolate TDEs; error checking/validation in BPMN tasks.
  - Log all for traceable "quality trail."

## 4. Non-Functional Requirements

- **Performance**: Computationally intensive probabilistic runs; optimize with horizontal scaling (e.g., AWS EKS).
- **Scalability**: Handle 1000s of TDEs; dynamic spawning.
- **Tech Stack**: Python 3+ for microkernel; Camunda/BPMN.io for processes; LLMs (OpenAI/Ollama); Docker for containers; AWS for deployment (CDK, ECS, Bedrock).
- **Constraints**: No internet in execution envs; keep prompts testable/offline.
- **Prototyping Timeline**: 5–7 days; prioritize DAS → Microkernel → PDO/TDE → Testing.

## 5. Implementation Notes for Copilot

- **Development Workflow**: Use VS Code/Cursor with GitHub Copilot. Prompt examples:
  - "Write Python microkernel to initialize Camunda and monitor API for new processes."
  - "Generate BPMN XML for a generic TDE with LLM decision gateway."
  - "Implement DAS in Python to generate BPMN from user prompt and store in vector store."
- **Testing**: Unit tests for components; end-to-end with sample processes (e.g., file write with parallel tasks).
- **Deployment**: Use AWS CDK for IaC; prompt Copilot: "Create CDK stack for ProcOS with ECS for TDEs and Bedrock for LLMs."
- **Knowledge Capture**: Log all Copilot prompts/responses/errors to vector store via script.

This spec provides a blueprint for building ProcOS. Iterate by prompting Copilot with specific sections, and expand based on prototypes. For questions, refine via chat.