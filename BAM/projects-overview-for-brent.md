name: projects-overview-for-brent
description: Overview of eight AI-powered support improvement projects for Brent
author: bernardm
skill: brain-dump
created_date: 2026-04-15 14:03:11
last_updated: 2026-04-15 13:03:34

# Projects Overview for Brent

## Executive Summary

The team is building eight interrelated projects that use AI to improve Azure support quality — from proactive self-diagnostics in the portal to better tooling for support engineers. The CARET system already contains the case-level data needed across all projects: troubleshooting steps taken by support engineers, custom queries executed, portal navigation telemetry, customer questions asked, case notes, and emails.

The core opportunity is to build and improve capabilities in CARET and problem modeling to fuel the work in all of these projects. Today, most projects rely on Azure Learn documentation and the LLM's built-in knowledge. The next wave of improvement comes from summarizing and structuring the CARET data so it can be consumed as a first-class input to every project.

The eight projects are: (1) ARM Diagnostics, (2) Support Topic Self Help, (3) Error Message Self-Help, (4) Troubleshooting Agents, (5) Scoping Questions, (6) Problem Modeling, (7) Repair Items / Case Clustering, and (8) Context IQ.

## CARET Data — What Exists and What Needs to Be Summarized

The CARET system already contains the following case-level data:

- Three properties that are relevant:
  - An email summary
  - The list of troubleshooting steps taken by support engineers
  - Questions asked to the customer during the troubleshooting process

What needs to be **summarized** from this CARET data (per support topic or problem type):

| Summarization | Feeds Into |
|---------------|------------|
| Troubleshooting steps → deduplicated, comprehensive list per support topic | Projects 1 (ARM Diagnostics), 2 (Support Topic Self Help), 3 (Error Message Self-Help), 4 (Troubleshooting Agents) |
| Questions asked to customers → classified as auto-collectible vs. manual | Project 5 (Scoping Questions) |
| Steps + queries + telemetry → agent instructions for troubleshooting | Project 4 (Troubleshooting Agents) |

## How the Projects Connect

The projects are not independent — they share data and build on each other:

```text
                    ┌──────────────────────────────┐
                    │  Case Data (CARET system)     │
                    │  - Troubleshooting steps taken │
                    │  - Questions asked to customer │
                    │  - Email summary               │
                    │  - Custom queries executed     │
                    │  - Portal navigation telemetry │
                    │  - Case notes & emails         │
                    └──────────┬───────────────────┘
                               │
          Summarized CARET data feeds all projects directly
                               │
          ┌────────────┬───────┼────────┬────────────┐
          ▼            ▼       ▼        ▼            ▼
  ┌───────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────┐
  │ Project 1:    │ │ Project 2:   │ │ Project 4:       │ │ Project 5:   │
  │ ARM           │ │ Support Topic│ │ Troubleshooting  │ │ Scoping      │
  │ Diagnostics   │ │ Self Help    │ │ Agents           │ │ Questions    │
  └───────────────┘ └──────────────┘ └──────────────────┘ └──────────────┘

  ┌───────────────┐ ┌──────────────┐ ┌──────────────────┐ ┌──────────────┐
  │ Project 3:    │ │ Project 6:   │ │ Project 7:       │ │ Project 8:   │
  │ Error Message │ │ Problem      │ │ Repair Items /   │ │ Context IQ   │
  │ Self-Help     │ │ Modeling     │ │ Case Clustering  │ │              │
  └───────────────┘ └──────────────┘ └──────────────────┘ └──────────────┘
```

**Key data flows:**

- **Summarized CARET data** (troubleshooting steps, questions, telemetry) feeds directly into Projects 1 (ARM Diagnostics), 2 (Support Topic Self Help), 3 (Error Message Self-Help), 4 (Troubleshooting Agents), 5 (Scoping Questions), and 8 (Context IQ).
- **Azure Learn / Microsoft Learn documentation** is used today across Projects 1, 2, and 3. Real case data will supplement it.
- **Kusto** is planned as a future data source for ARM Diagnostics checks but is deferred.


## Projects


### Project 1: ARM Diagnostics (Self-Diagnostics Generation)

#### What It Does

Uses AI to automatically generate diagnostic checks for Azure resources based on their Swagger API definitions. The checks run against live ARM data and produce customer-ready content identifying potential root causes — all within the portal, before the customer needs to create a support case.

#### Current State

- Functional pipeline from Swagger → checks → LLM → customer content.
- Relies primarily on the LLM's built-in knowledge about Azure resources plus the Swagger definition.
- Has the technical capability to consume additional data sources (e.g., Kusto) but is not yet using them.

#### Desired Enhancements

- **Pass summarized troubleshooting steps** (from CARET) alongside the Swagger so that generated checks cover all real-world scenarios, not just what the model knows.
- **Expand data sources** to include Kusto queries for richer diagnostic signals (deferred to a future phase).


### Project 2: Support Topic Self Help

#### What It Does

Generates self-help articles for support topics that either don't have self-help content or where deflection is low. Uses AI to generate new articles that incorporate what support engineers actually do to resolve cases.

#### Current State

- Today, the generation process only uses Azure Learn (Microsoft Learn) documentation as the source.

#### Desired Enhancements

- Bring summarized troubleshooting steps from CARET into the generation process so AI-generated self-help takes into account what support engineers are actually doing to resolve cases.


### Project 3: Error Message Self-Help Articles

#### What It Does

Generates self-help articles for specific error messages, so customers encountering errors in the Azure portal can immediately see relevant guidance without creating a support case.

#### Current State

- The approach is defined; leverages Azure Learn documentation as the primary knowledge source.

#### Desired Enhancements

- Take a similar approach to Project 2 (Support Topic Self Help) to generate error-message-specific self-help content from CARET data.


### Project 4: Auto-Generation of Troubleshooting Agents

#### What It Does

Automatically generates troubleshooting agents for support engineers. For a given support topic, produces agent instructions that guide the support engineer through troubleshooting.

#### Current State

- In ideation phase.

#### Desired Enhancements

- Bring summarized troubleshooting steps and summarized questions from CARET into the agent generation process.
- Consume ASC telemetry to further improve the generated agent instructions.


### Project 5: Scoping Questions

#### What It Does

Similar to the troubleshooting steps, takes all of the questions that support engineers asked customers across cases and classifies them into things that can be collected automatically versus things that require manual collection. Also enriches CRI creation with auto-extracted context.

#### Current State

- In ideation phase.

#### Desired Enhancements

- Leverage the summarized questions from CARET to generate scoping questions for each support topic.
- Use AI to classify each question with a priority level, where P0 is a question that must be answered before the case is opened (asked in the portal).
- Classify each question as automatically collectible (system can gather it) versus requires human response (must be asked to the customer).


### Project 6: Problem Modeling

#### What It Does

Detects and characterizes emerging problems even when there are very few reported cases. Addresses the challenge of identifying issues before they generate a statistically significant volume of support cases.

#### Current State

- Problem modeling is already available.
- Identified an issue where a large number of clusters contain only one or two cases (e.g., Virtual Machine running Windows has this problem).

#### Desired Enhancements

- Fix the low-case-count clustering issue so clusters are meaningful.
- Explore Consuming the two-tier version that Brent was working on if it is ready and is available.


### Project 7: Repair Items and Case Clustering

#### What It Does

Working with the ACES team, builds a system that uses AI to identify patterns across support cases, clusters them, and generates repair items for the most impactful issues to be sent to Azure service teams.

#### Current State

- Repair items are generated when a case cluster is opened, but they are not saved anywhere and are not created in advance.

#### Desired Enhancements

- Use case clusters to generate repair items for every cluster proactively (not just on-demand when opened).
- Review all generated repair items, deduplicate, cluster them, and find commonalities.
- Identify the top five most impactful repair items and expose those to the service teams.


### Project 8: Context IQ

#### What It Does

A new service that collects all necessary context throughout the entire case lifecycle — from when the customer is troubleshooting in the portal, through case creation, support engineer troubleshooting, and escalation as a CRI. Consumes data from scoping questions and other sources to properly scope the problem. The goal is to gather enough context to either solve the case in the portal or ensure the support engineer can resolve it as quickly as possible.

#### Current State

- New service being built.

#### Desired Enhancements

- Build context collection across all lifecycle stages: self-service troubleshooting, case creation, support engineer troubleshooting, and CRI escalation.
- Consume scoping question data (from Project 5) and additional sources to fully scope the problem.
- Enable portal-side resolution when possible; otherwise deliver rich context to the support engineer.