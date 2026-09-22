# Kairo

> Intelligent academic workload planning for students, teams, and educators.

Kairo is an AI-powered task management and workload optimization platform
designed for university students and project teams.

Kairo ingests course documents such as syllabi, extracts and classifies
assessments, decomposes complex deliverables into actionable subtasks,
evaluates required skills, and intelligently schedules and distributes work
based on deadlines, workload, skills, and calendar availability.

For educators, Kairo provides analytics into workload, task performance,
student progress, and potential bottlenecks within a course.

---

## Why Kairo?

Students rarely manage a single independent stream of work.

A typical semester involves multiple courses containing assignments, labs,
exams, reports, presentations, and team projects, each competing for limited
time. Group projects introduce an additional problem: work must be divided
across people with different skills, schedules, and existing workloads.

Kairo aims to transform this information into an intelligent execution plan.

Instead of simply asking:

> "What assignments do I have?"

Kairo attempts to answer:

> "What should we work on, who should work on it, and when should it happen?"

---

## Core Capabilities

- Syllabus and course-document ingestion
- AI-assisted assessment extraction
- Task classification
- Skill identification and assessment
- Intelligent task decomposition
- Team workload allocation
- Calendar-aware scheduling
- Individual and team task management
- Human-in-the-loop feedback
- Syllabus Q&A and contextual recommendations
- Professor-facing workload and performance analytics
- External integrations including Google Calendar and Google Drive

---

## System Architecture

Kairo is designed as a modular AI-enabled web platform consisting of a React
frontend, FastAPI application layer, asynchronous workers, AI/ML services,
operational and analytical data stores, and external integrations.

![Kairo System Architecture](Images/System%20Architecture.png)

### Major Components

**Frontend**
- React
- TypeScript
- Role-specific student, team lead, and professor experiences

**Backend**
- FastAPI
- Authentication and authorization
- Business logic
- Model orchestration
- Data ingestion
- External integrations

**Data**
- PostgreSQL / Supabase — transactional and relational data
- Redis — caching, queues, and ephemeral state
- BigQuery — analytical workloads
- Vector storage — semantic retrieval and RAG

**AI / ML**
- Document and table understanding
- Assessment extraction
- Task classification
- Skill identification
- Task decomposition
- Intelligent allocation and scheduling
- Retrieval-augmented Q&A

**Infrastructure**
- Docker
- Google Cloud Platform
- GitHub Actions
- Temporal / asynchronous workflow orchestration

---

## Data & AI Flow

Kairo combines user-provided information, course documents, calendar
availability, skill information, and historical data to generate actionable
work plans.

![Kairo Data Flow](Images/Data%20Flow%20Diagram.png)

The platform supports three primary user experiences:

### Student

Students manage individual coursework, availability, skills, deadlines,
generated subtasks, and personal schedules.

### Team Lead

Team leads manage collaborative projects, shared documents, team workload,
task assignments, and project schedules.

### Professor

Professors access aggregated analytics designed to identify workload patterns,
task bottlenecks, and opportunities for improving course delivery.

---

## AI/ML Pipeline

At a high level:

Course Documents
→ Document Processing
→ Assessment Extraction
→ Task Classification
→ Skill Identification
→ Task Decomposition
→ Intelligent Allocation
→ Schedule Optimization
→ User Feedback

Model outputs are designed to be measurable and correctable rather than
treated as unquestionable AI-generated results.

---

## Tech Stack

| Area | Technologies |
|---|---|
| Frontend | React, TypeScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL, Supabase |
| Cache / Queue | Redis |
| Workflow Processing | Celery / Temporal |
| Machine Learning | Python, NLP, Transformers, LLMs |
| Analytics | BigQuery |
| Vector Retrieval | Vector database / pgvector |
| Infrastructure | Docker, GCP |
| CI/CD | GitHub Actions |
| Integrations | Google Calendar, Google Drive, Gmail, Slack |

> The architecture is intentionally iterative. Technologies are introduced
> when justified by system requirements rather than solely for stack complexity.

---

## Project Background

Kairo is an evolution of **ProjectPath**, a University of Toronto engineering
capstone project focused on intelligent academic task management.

The original project explored syllabus parsing, task extraction, transformer-
based task classification, subtask generation, and intelligent resource
allocation.

Kairo expands that concept into a production-oriented system with a redesigned
data architecture, asynchronous processing, modern AI/ML pipelines, analytics,
external integrations, observability, and cloud deployment.

---

## Repository Structure

```text
kairo/
├── apps/
│   ├── api/                 # FastAPI backend
│   └── web/                 # React frontend
│
├── services/                # ML / processing services
├── packages/                # Shared packages
├── infrastructure/          # Deployment / infrastructure configuration
├── docs/
│   ├── architecture/
├── tests/
├── .github/
│   └── workflows/
├── Images
└── README.md

```
---

## Development Status

Kairo is currently under active development.

Current focus:

* Initial system architecture
* Initial data-flow design
* Core database schema
* Authentication
* Course and team management
* Document ingestion pipeline
* Assessment extraction pipeline
* Task classification
* Task decomposition
* Calendar integration
* Scheduling and allocation engine
* Analytics pipeline
* Production deployment

---

## Engineering Goals

Kairo is being developed with an emphasis on:

* Production-quality Python and API development
* Relational data modelling
* Data engineering and asynchronous pipelines
* Applied machine learning
* LLM and NLP system design
* Model evaluation and observability
* Distributed workflow orchestration
* Cloud-native deployment
* CI/CD and automated testing

---

