# Melvin Conway and Tim's Delivery Architecture

*Melvin Conway is a computer scientist who, in 1968, published "How Do Committees Invent?" in Datamation magazine. The paper introduced what became known as Conway's Law: any organization that designs a system will produce a design whose structure is a copy of the organization's communication structure. The observation was initially dismissed as a joke. It was later validated empirically and became the theoretical foundation for Team Topologies, Domain-Driven Design's bounded contexts, and microservices architectural theory. Fred Brooks cited it in The Mythical Man-Month. Amazon's two-pizza team rule is a direct operational application of it.*

*Conway's contribution is narrow and precise: he has one big idea, and it is exactly right. His relevance to Tim's corpus is not peripheral — it is foundational.*

---

## 1. Conway's Law States Tim's Problem Precisely

Tim's central argument: large organizations lose delivery velocity because of coordination overhead, unclear ownership, and diffuse accountability. Conway's Law provides the mechanism.

If Azure's software boundaries have grown organically across org boundaries — if a single feature requires coordination between teams that do not share a manager below VP level — then the coordination cost is not a process failure. It is an architectural consequence. The software mirrors the org. If the org is fragmented, the software will be fragmented. If the software is fragmented, every increment requires cross-team coordination. Coordination is the tax on architectural debt accumulated through org decisions.

Tim's mission team model attempts to address this by creating small, single-threaded teams with bounded ownership. Conway would say: this is exactly right, and here is the constraint you must take seriously — **the software architecture must be redesigned to match the team topology, or the team topology will fail.**

Small teams cannot own bounded domains if the domain boundaries in the software do not match the team boundaries. If team A must reach into team B's codebase to ship their mission, the mission is not bounded. No amount of accountability structure fixes that. The org must restructure toward the architecture, or the architecture must restructure to match the org. Tim's corpus does not address this. It assumes the software can be carved into mission-shaped pieces without specifying how that carving happens.

---

## 2. The Reverse Conway Maneuver

The most important practical application of Conway's Law is what Skelton and Pais later named the Reverse Conway Maneuver: rather than designing software and then fitting a team structure around it, design the desired software architecture first, and then structure teams to match it.

This reversal matters enormously for Tim's model. If Tim wants steel threads that are durable and continuously exercisable, the software domains those threads cut through must have clean interfaces. If they do not have clean interfaces — if they are entangled — no weekly rhythm, no named lead, and no escalation discipline will produce the velocity Tim is looking for.

The Reverse Conway Maneuver says: decide what the clean interfaces should be, then build teams around those interfaces. The mission team charter should be derivable from the software architecture, not independent of it.

---

## 3. What Conway Would Ask Tim

**Does each mission team's scope match a naturally bounded domain in the software?**

If the answer is "mostly, but with some cross-team dependencies for shared infrastructure and platform services," Conway would say that is not a bounded mission. That is a partially bounded mission with unacknowledged coordination costs baked in. Those costs will show up as blocked PRs, delayed integrations, and teams waiting on each other — and they will be attributed to process problems rather than to what they actually are: architectural debt.

**Who owns the interface between mission teams at the software level?**

Not the organizational interface — the API, the event schema, the data contract. In Tim's model, named leads own accountability for outcomes. But outcomes are delivered through interfaces. If nobody owns the interface as a first-class artifact with a versioning discipline, mission teams will break each other's implementations while all technically delivering their own piece on time.

---

## 4. Why This Is Not in Tim's Corpus

Tim's corpus is written for an XLT audience, not an engineering audience. Interface design, domain boundaries, and architectural coherence are engineering concerns — and the corpus deliberately operates one level of abstraction above them. This is a scope decision, not an oversight.

But it creates a gap: the model works if the software architecture is clean enough to accommodate bounded mission teams. It fails predictably if the architecture is entangled — which, in a large, mature cloud platform, it almost certainly is in places.

The OFP response should acknowledge this dependency explicitly. The mission-team model is not self-contained. It presupposes architectural work that the corpus does not describe.
