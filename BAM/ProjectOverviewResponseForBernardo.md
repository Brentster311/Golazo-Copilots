# Project Overview — Response for Bernardo

## CARET Data — What Exists and What Needs to Be Summarized

- We do have the email summary — double-check on that.
- Troubleshooting steps: I know Wade did something there. Verify current state.
- Questions: We do have that already. We may need to add PSQ into this section as well.
- You mention troubleshooting steps need to be deduplicated into a comprehensive list **per support topic**. I'm curious why per support topic and not per problem cluster — but maybe it's because of a certain overlap? I think I agree with that reasoning.
- **Steps + Queries + Telemetry**: This is going to be the exciting part of the project. I really have no idea how to estimate what this is going to take. Part of me asks: do we want a combination of traditional data science and LLM, or stick with all LLM? Not entirely certain. I'm going to be doing some research shortly around state-of-the-art troubleshooting for AIOps work, and I think that could apply here.

---

## Project 1: ARM Diagnostics

- I think this is the generation of the configuration problem we talked about before.
- I still think investing in an SLM might be worth it. But if it ends up just being me doing this work, I really don't have an idea of what that's going to take and what the probability of it actually working is. So it's probably going to be smart to start small.
- Your documentation mentions **Swagger** — where are these Swagger APIs coming from? Who hosts this? Is this ARM? Do we have documentation for this? I've not heard of this before. I do know Azure Resource Graph has APIs.
- The other question: just because ARM publishes the Swagger API, are we going to get access to it? How are we going to connect to it in real time? This is an interesting project — I think there are a lot of details that need to be worked out.

---

## Project 2: Support Topic Self Help

- We've talked about this one in the past. I absolutely think this should be cheap to generate.
- I hear a word that Scott Roberts is doing something around diagnostics — skipping forward, it sounds like they're doing a variant of something (maybe GT but smarter?). I need to get more detail there.
- The thing I want to re-analyze on self help: there have been a lot of changes in the portal since my team was actively involved. It might be worthwhile to understand where help is being presented and where it is actually deflecting. But maybe you already have this.

---

## Project 3: Error Message Self-Help Articles

- Makes sense.
- Isn't Scott G. (Scott Gee / GE) or the ACES team driving that?
- We should absolutely do that. I don't know what remains.
- From the CARET data — maybe we need to improve CARET to get better at extracting the error messages. That data is already there, though.

---

## Project 4: Auto-Generation of Troubleshooting Agents

- I get the intent here, and I'm glad it's in ideation phase.
- Is this auto-generation of agents? Is this something closer to the Eureka Learner, where we're learning and persisting skills?
- I think we should absolutely do that.

---

## Project 5: Scoping Questions

- This is in progress.
- Looks like we got approval from Privacy to do stuff here, as long as we de-identify. We'll have to figure out a persistence model, etc.

---

## Project 6: Problem Modeling

- It's already available.
- I want to do the two-tier version that we've been talking about. We've got to get that going.
- Once we get that going, it directly feeds into **Project 7** (Repair Items and Clustering).

---

## Project 7: Repair Items and Case Clustering

*(Covered above — Problem Modeling output feeds directly into this project.)*

---

## Project 8: Context IQ

- I saw the name at the very beginning and thought, "Oh, this is exciting."
- A new service that collects all necessary context throughout the portal while the customer is troubleshooting — OK.
- I've been spending a lot of time thinking about context and context windows, so it's interesting that this gets brought up here.
- This is a new service being built, not in ideation phase — I see.
- Context window here is more around collecting context that can be sent down — that will be immensely valuable, assuming those payloads aren't incredibly ginormous.
- The way you talk about it from a lifecycle perspective — **I like this idea very much**.
- I want it connected to the **left shift** somehow. It's not only around what we collect on the way down, but as we use the information — the safety nets and all that — as we solve problems for the customer, how do we understand **why the previous safety net missed it**?
- Creating that feedback loop is what's going to make this super awesome and virtuous in the long term.