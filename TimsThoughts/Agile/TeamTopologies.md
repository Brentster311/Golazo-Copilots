# Matthew Skelton & Manuel Pais — Team Topologies and Tim's Delivery Architecture

*Matthew Skelton and Manuel Pais published Team Topologies in 2019. The book is the most complete, practically documented treatment of how to structure software delivery teams in large organizations. It builds directly on Conway's Law, incorporates ideas from Lean, DevOps, and Domain-Driven Design, and introduces a precise typology of team structures and interaction modes. It is the closest thing the software industry has to a field manual for the problem Tim's corpus is trying to solve.*

---

## 1. The Four Team Types

Skelton and Pais define four types of teams, each with a distinct purpose:

- **Stream-aligned teams**: own a continuous flow of work aligned to a business or product domain. They are the primary delivery units. Every other team type exists to reduce the cognitive load on stream-aligned teams. Tim's "mission teams" are stream-aligned teams, though Tim does not name them as such.

- **Platform teams**: provide internal services to stream-aligned teams, allowing them to operate autonomously without rebuilding shared infrastructure. Tim's corpus assumes platform services exist but says nothing about how platform teams are structured, governed, or how their capacity is allocated to mission teams.

- **Enabling teams**: temporarily work with stream-aligned teams to help them build capability — filling skill gaps, introducing new practices, and then stepping back. Tim's model has no enabling team concept. His "team of teams" is a network of mission teams, not a network that includes enabling teams as a distinct type.

- **Complicated-subsystem teams**: own components that require deep specialist knowledge to maintain (e.g., a video codec, a distributed transaction engine). They reduce cognitive load on stream-aligned teams by owning the complexity. Tim's model does not address this type.

The omission of platform and enabling team types creates a structural gap. Mission teams that need platform capabilities must either build them themselves (duplication, cognitive overload) or coordinate cross-team (dependencies, the coordination cost Tim is trying to eliminate).

---

## 2. The Three Interaction Modes

Skelton and Pais define three legitimate ways teams can interact:

- **Collaboration**: two teams work together closely, with high bandwidth, for a bounded period on a specific problem. Expensive (full-team attention) but necessary for discovery work or resolving unclear domain boundaries.
- **X-as-a-Service**: one team provides a capability to another through a clean API, with no ongoing collaboration required. Low coordination cost; high autonomy.
- **Facilitating**: an enabling team works alongside a stream-aligned team temporarily to build capability.

Tim's model implies X-as-a-Service (mission teams should be autonomous) but does not specify how teams determine which mode applies, when to shift between modes, or what well-designed service boundaries look like.

---

## 3. Cognitive Load as the Primary Constraint

The central practical concept in Team Topologies is **cognitive load**: every team has a limit on how much domain complexity, platform complexity, and coordination complexity it can carry simultaneously. When cognitive load exceeds capacity, output quality degrades and velocity drops.

Tim's model controls team size (small, single-threaded) — which is exactly the right intuition. But cognitive load is not just a function of team size; it is a function of scope, interface complexity, and how much the team must understand about adjacent systems to do its own work. A small team with a poorly bounded domain and many external dependencies can be as cognitively overloaded as a large team.

The practical question for each mission team in Tim's model: is the team's cognitive load within a manageable range? Is the domain bounded well enough that the team can hold the whole thing in their heads? Are the interfaces to adjacent teams clean enough that the team does not need to understand those teams' internals to make progress?

Tim's corpus has no mechanism to assess this.

---

## 4. What Skelton & Pais Would Ask Tim

**Where are the platform teams?** Mission teams need shared infrastructure — CI/CD pipelines, observability, secrets management, compliance tooling. Who provides this, and how is its roadmap set to serve mission team needs rather than platform team preferences?

**How are domain boundaries set?** Tim's corpus defines how teams operate once formed. It says nothing about how mission charters are defined to match natural software domain boundaries. This is the most consequential design decision in the model.

**What happens when two mission teams need to collaborate?** Tim's model has clean escalation as a discipline. Skelton and Pais would say collaboration between teams should be explicit, time-boxed, and intentional — not a sign that something has gone wrong (as the escalation framing implies), but a recognized mode with its own operating norms.
