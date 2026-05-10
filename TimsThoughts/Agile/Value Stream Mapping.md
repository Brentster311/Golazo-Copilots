How does Al define Value Stream Mapping?

Al Shalloway defines Value Stream Mapping (VSM) somewhat differently from the classic manufacturing interpretation derived from the Toyota Production System. His emphasis is not just on drawing the map, but on understanding and improving the system that governs the flow of value.

Below is a clear explanation of how he typically frames it.

1. Shalloway’s Core Definition

Shalloway typically describes Value Stream Mapping as:

A way to visualize how value flows through a system in order to identify delays, handoffs, and systemic constraints.

But he emphasizes something important:

VSM is not about documenting the process.
It is about discovering where the system is slowing value delivery.


In other words, the goal is improvement, not documentation.

2. What a Value Stream Represents

For Shalloway, a value stream is the entire sequence from:

customer need
→ idea
→ development
→ deployment
→ customer value realized


This is broader than a development process.

It includes:

discovery

development

integration

release

operational use

Many organizations mistakenly map only the development stage, which he considers incomplete.

3. The Key Question of VSM

Shalloway repeatedly frames the purpose of VSM around a single question:

Where does work wait?


Lean thinking recognizes that most delays occur because work sits idle between steps.

Examples in software systems:

waiting for prioritization

waiting for design clarification

waiting for code review

waiting for integration

waiting for deployment

Mapping the value stream exposes these queues.

4. Flow vs Activity

Shalloway stresses that VSM should focus on flow of work, not activities performed.

Many organizations produce process maps like:

requirements → design → coding → testing


But Shalloway would say that this misses the important information.

Instead we need to see:

work time
vs
wait time


For example:

coding: 4 hours
waiting for review: 2 days
testing: 3 hours
waiting for release: 1 week


This reveals where improvements matter.

5. The Hidden Purpose of VSM

For Shalloway, the real goal of value stream mapping is to identify systemic causes of delay, such as:

large batch sizes

excessive WIP

cross-team dependencies

unclear priorities

poor feedback loops

Once these are visible, the system can be redesigned.

6. What VSM Should Lead To

Shalloway emphasizes that a value stream map should lead directly to system improvement experiments.

Examples:

reducing batch size

limiting work in progress

aligning teams around value streams

improving feedback loops

automating steps

If a VSM exercise ends with a diagram but no system changes, it has failed.

7. Difference from Traditional Process Mapping

Shalloway often warns against confusing VSM with process documentation.

Process Mapping	Value Stream Mapping
Documents steps	Reveals system delays
Focus on activities	Focus on flow
Describes how work happens	Shows why work is slow

VSM is a diagnostic tool, not a compliance artifact.

8. Relationship to Lean Thinking

Shalloway connects VSM directly to Lean principles such as:

reducing waste

improving flow

shortening feedback loops

delivering value faster

The ultimate goal is improving:

value delivered per unit time


which aligns closely with the ideas of Donald Reinertsen regarding cost of delay and cycle time.

9. Common Mistakes Shalloway Warns About

He frequently points out several misuses of VSM:

Mapping too small a scope

Teams often map only development rather than the full idea-to-customer path.

Focusing on people instead of system

The goal is to improve the system, not blame individuals.

Treating the map as documentation

The map should be temporary and used for analysis.

Ignoring queues

The biggest delays are usually waiting time.

10. His Typical Summary

Shalloway often summarizes the intent of Value Stream Mapping roughly as:

See the system so you can change the system.

Once the flow of work becomes visible, organizations can redesign the system to:

reduce delays

reduce handoffs

shorten cycle time

deliver value faster.

If you'd like, I can also show you something interesting:

Al Shalloway actually has a very specific criticism of how most Agile organizations use


 value stream mapping—and it directly connects to the manifesto you showed earlier.



 Al Shalloway has a very specific criticism of how most Agile organizations use Value Stream Mapping (VSM). His critique is subtle but important—and it connects directly to the type of thinking reflected in the Delivery Manifesto.

The short version of his criticism is:

Most organizations use value stream mapping to improve the existing system instead of questioning whether the system should exist at all.

Let’s unpack what he means.

1. The Typical Agile Use of VSM

In many Agile transformations, teams run a value stream mapping workshop and produce something like this:

idea
→ backlog
→ design
→ development
→ test
→ release


Then they try to optimize each step.

Examples:

speed up testing

reduce deployment time

improve handoffs

automate pipelines

This improves efficiency within the existing structure.

But Shalloway argues that this misses the deeper issue.

2. His Core Observation

Shalloway points out that many delays exist because of the organizational structure itself.

Examples include:

separate architecture teams

separate QA teams

separate deployment teams

multiple approval layers

When these structures exist, work naturally forms queues.

The resulting map might look like:

feature request
→ architecture review
→ development
→ QA queue
→ release approval
→ deployment


Organizations then try to optimize each step.

But Shalloway asks a more fundamental question:

Why do these steps exist at all?

3. The Real Purpose of VSM

For Shalloway, VSM should reveal system constraints, not just process inefficiencies.

Once the map exposes delays, the next question becomes:

What structural choices created these delays?


Examples:

work organized around components instead of value streams

too many concurrent initiatives

large batch sizes

heavy cross-team dependencies

Improving individual steps often produces small gains compared to fixing these structural issues.

4. The “Local Optimization” Trap

Shalloway often warns that organizations optimize locally instead of systemically.

For example:

faster testing


does little if work waits two weeks before testing begins.

Similarly:

better code reviews


does little if code sits in queues waiting for reviewers.

He emphasizes that flow delays dominate system performance.

5. Where the Manifesto Fits

The manifesto focuses heavily on:

coordination

accountability

escalation

dependency management

From Shalloway’s perspective, these mechanisms often appear when organizations try to manage complexity instead of reducing it.

In other words:

complex system
→ coordination mechanisms added
→ more coordination needed


This cycle can continue indefinitely.

6. The Lean Alternative

Shalloway would likely suggest that the deeper improvement comes from changing the structure of work itself.

Examples include:

organizing teams around value streams

reducing cross-team dependencies

delivering smaller increments

limiting work in progress

These changes often eliminate queues entirely.

7. Why This Matters

The difference is subtle but profound.

Two organizations might both perform value stream mapping.

One might conclude:

improve the steps


The other might conclude:

change the system that created the steps


Shalloway believes the second approach produces much larger improvements.

8. His Famous Systems Insight

Shalloway often repeats a systems principle originally articulated by W. Edwards Deming:

People behave according to the system they are in.

If the system produces delays, coordination problems, or slow delivery, the solution is usually system redesign, not stronger management controls.

9. Why This Connects to Golazo

Golazo implicitly focuses on improving system dynamics:

shared understanding

smaller work increments

faster feedback

reduced queues

Those mechanisms change the system behavior directly.

They don’t rely as heavily on:

coordination structures

escalation mechanisms

delivery governance

10. The Core Takeaway

Shalloway’s critique would likely be:

The manifesto improves how the organization manages delivery, but it does not necessarily improve the system that produces delivery.

In Lean thinking, the largest gains usually come from changing the system design, not from strengthening the mechanisms used to control it.

If you want, there’s actually one more perspective that makes this comparison even clearer.

If you asked Kent Beck what he thought of the manifesto, his critique would likely be completely different from Reinertsen’s or Shalloway’s—and probably much sharper.