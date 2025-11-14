% A Cause-Effect Model for Emergent Time and Distance
% Anes Palma, An M. Rodriguez
% November 14, 2025

## One-Sentence Summary

A single stable Node with incomputable internal structure yields emergent time
from cause-effect ordering and distance from causal step counts.

## Abstract

We present a framework in which reality emerges from a single, stable Node
possessing an incomputable internal structure. This Node is fundamentally
unchanging in total energy, yet contains subnodes capable of creating
cause-effect relationships. These relationships define an ordering of
"before" and "after"-which we interpret as *time*. Distance likewise emerges
by counting the number of causal steps required for a subnode $i$ to affect a
subnode $j$. When access to $j$ is indirect or nonexistent, a round-trip chain
of cause and effect within the same subnode can serve to define both a clock and
a notion of distance. Despite its minimal assumptions, this scheme remains
consistent with the idea that space, time, and measurement originate from
interactions internal to a stable underlying structure.

## Keywords

cause-effect, emergent time, emergent distance, subnodes, order, stable Node


## Introduction

Conventional physics usually assumes a background spacetime and a global time
parameter. Foundational attempts to question these assumptions -- such as
Barbour’s timeless formulations [@barbour1999] , Wheeler’s information-based
proposals [@wheeler1992], and order-theoretic treatments like Kronheimer-Penrose
[@kronheimer1967] -- still rely on temporal orientation, geometric structure,
unexplained binary choice mechanisms, or on other pre-fabricated constructs like
mass, quantum models, or relativity. These approaches treat such constructs as
if they predate cause-effect itself, rather than being partial and yet
incomplete human attempts to explain it. Causal-set theory [@bombelli1987] takes
causal order as fundamental but forbids causal loops, which are essential in our
model once one accepts that a clock is a closed causal loop assumed to tick at a
constant rate relative to others. These assumptions differ sharply from the view
taken here.

We start from a more primitive basis, and from this primitive, ordering arises.

We posit a single, stable Node $N$, changeless in its global quantity (such as
total energy), yet containing an *incomputable*[^1] internal structure of
subnodes. These subnodes interact. A cause produces an effect. This is the only
requirement: without effects happening from causes there is none to ponder or
nothing to ponder about. Further, a subnode with no effects is operationally
equivalent to a dead end. This leads to the conclusion that closed causal loops
must exist within the Node. This is the primitive. No geometry. No manifold. No
metric. No temporal labels.

[^1]: In acknowledgement to Plato's cave allegory: we do not have direct access
to true reality. We do not forbid predictable cause-effect outcomes; we only
state that the full structure is inaccessible.

The aim of this model is not to specify a physical theory, but to construct the
minimal substrate on which any such theory may be built. We avoid introducing
mathematical structures such as graphs, sets with partial orders, state-update
maps, manifolds, or metrics. These constructs represent human idealizations
already dependent on time, space, or geometry. Instead, we work with the minimal
primitive: a cause produces an effect. From this, we show that notions of time
and distance arise as consequences of the causal substrate.

A cause-effect sequence becomes what we call *before* and *after*. Closed causal
cycles form clocks. Step counts in these cycles yield durations. Step counts
between subnodes yield distance. Spacetime is not a prior stage but an emergent
pattern within the stable Node.

This work develops this idea formally and operationally.
Time and distance appear as step counts in the internal cause-effect network.
Measurement arises from repeated causal loops within a single subnode.

**Key idea**

> "Time" emerges as the observed ordering of cause and effect among subnodes.
> Distance emerges by counting how many cause-effect steps occur between two
> subnodes (or within repeated interactions of the same subnode).


## Stable Node and Internal Structure

### Definition of the Node

Let us call this entire structure $\mathbf{N}$:

$$
\mathbf{N} = \{ n_i \mid i \in I \}
$$

where each $n_i$ is a subnode. The Node as a whole is stable: there is no net
change in total energy or other overall properties. Internally, however, the
subnodes can be arranged so that *local* causes produce *local* effects
elsewhere.

### Clarifying the term "ordering"

The subnodes of the Node admit an ordering in this sense: some subnodes can
affect others, forming causal sequences. We use the term “ordering” in its
primitive sense: an accessible sense of direction in the cause–effect relation.
In this ordering, cycles and self-loops are allowed and, as shown later,
naturally arise in a finite stable Node.


### Cause-Effect Relation

We formalize a cause-effect relation among the subnodes. If subnode $n_i$ can
trigger a change in subnode $n_j$, we write:

$$
n_i \succ n_j
$$

meaning "$n_i$ is the cause, $n_j$ is the effect." This relation is "partial"
in the sense of incomplete specification, not in the mathematical sense of a
"partial order": not all pairs of subnodes need to be causally related. It is
also not necessarily symmetric; if $n_i$ affects $n_j$, it does not
automatically mean $n_j$ affects $n_i$.

We emphasize that $\succ$ is not a partial order in the strict mathematical
sense. Cycles, including $n_i \succ n_a \succ \dots \succ n_i$, are permitted
and expected. Such cycles are essential for constructing clocks and durations.
The relation is “partial” only in the informal sense that not all subnode
interactions must be specified or accessible.

### Emergent Time as Ordering

From the ordering relation $\succ$, we interpret $n_i \succ n_j$ as "$n_i$ occurs
*before* $n_j$" in the emergent sense. A chain

$$
n_i \succ n_a \succ n_b \succ n_j
$$

implies a sequence of cause-effect steps linking $n_i$ to $n_j$. Thus, even
without referencing an external clock, we can consistently define an ordering
akin to time.


## Constructing a Clock

### Local Clock from Self-Interaction

A single subnode $n_i$ can be used to build a rudimentary “clock’’ by the
following repeated loop:

1. **Cause in $n_i$:** $n_i$ emits a perturbation or signal.
2. **Propagation:** The perturbation travels through a chain of subnodes
   (possibly including $n_i$ itself multiple times).
3. **Return to $n_i$:** Eventually the effect reappears in $n_i$, closing the
   loop.

We then count the discrete causal steps (or observe a repeated pattern of
changes in $n_i$) to define a repeatable unit. This cyclical process *is* the
“tick’’ of the clock.

### Cause-Effect Duration

If subnode $n_i$ directly affects subnode $n_j$, we define a one-step
cause-effect delay (one “unit’’). If a signal must travel a longer chain:

$$
n_i \succ n_a \succ n_b \succ \dots \succ n_j
$$

then the chain length can be counted, giving more units. In practice, each step
might be weighted by a factor (e.g., different subnode couplings), but the
essential notion is that *time* emerges from counting these intervals.


## Emergent Distance

### Definition of Distance

Distance between two subnodes $n_i$ and $n_j$ can be defined as the causal step
count for $n_i$ to affect $n_j$. If the minimal chain from $n_i$ to $n_j$ has
length $L_{ij}$, then

$$
d(n_i, n_j) \propto L_{ij}
$$

Here, $L_{ij}$ might be 1 if they are “adjacent’’ in causal terms or larger if
the signal must traverse many intermediate subnodes.

### Local vs. Non-Local Interactions

- **Local:** If $n_i$ can directly trigger $n_j$ with minimal intermediaries,
  $d(n_i, n_j)$ is small.
- **Non-Local:** If there is no straightforward path from $n_i$ to $n_j$, then
  the distance is undefined or effectively infinite.

Sometimes we lack direct access to $n_j$. Then we measure distance via a
round-trip within $n_i$ itself:

$$
n_i \succ \dots \succ n_i
$$

Count the steps in the loop. A subnode can gauge an apparent distance to
something else by noticing changes in its own state after some chain of events.


## Reflections and Chains

Signals or perturbations may:

* Travel directly from $n_i$ to $n_j$ if they are adjacent in the cause-effect
  diagram.
* Pass through multiple intermediaries $(n_a, n_b, \dots)$.
* Reflect back to the original subnode $n_i$, closing a loop used for timing.

Regardless of path complexity, each segment corresponds to a well-defined
cause-effect step. Summing or concatenating these steps yields a measure of
duration and thus a notion of distance.


## Discussion

### Why the Node is "Stable"

Although we speak of cause-effect steps and subnode interactions, the Node $N$
as a whole remains changeless in its global property (energy, etc.). The
cause-effect network represents internal rearrangements of that fixed total.
Nothing external changes (the Node is considered to be it-all, in the sense that
nothing 'external' to it can exist; the Node is causally isolated by
definition); the entire structure is a tapestry of possible cause-effect
pathways, but locally perceived as sequences of transformations.

### On the Existence of Closed Causal Loops

Because the Node is globally stable, its total quantity (such as total energy)
admits only finite redistribution among its subnodes. Any subdivision of the
Node into finitely many interacting subnodes must exhibit causal structure in
the operational sense: every cause produces some effect. When the number of
available subnodes and causal channels is finite while the propagation of
effects continues indefinitely, repetition becomes unavoidable. From this it
follows that at least one closed causal chain must exist.

This statement is not a mathematical proof but an operational observation:
persistent cause–effect propagation within a finite, stable structure cannot
avoid returning, directly or indirectly, to a previously affected subnode. A
closed causal loop is therefore not an added assumption but an inevitable
feature of any finite, stable Node that supports ongoing causal activity.

Closed loops are central in this framework because they provide the mechanism
for constructing clocks. A loop allows a subnode to register recurrence, and
the count of repeated traversals yields a notion of duration. The existence of
at least one such loop is thus a structural consequence of stability and finite
causal subdivision.

### Consistency with Physical Theories

* **General Physical Compatibility:** By not specifying the exact subnode
  coupling, emergent geometry or fields can arise. Standard concepts (mass,
  charge, etc.) may be grafted onto these cause-effect relationships.
* **Signal-Based Metric:** Physics often uses light signals or wave propagation
  to define time and distance operationally. This model generalizes that idea to
  any cause-effect path in the abstract Node.

## Related Work

It is useful to position our work in relation to other approaches that appear
similar in surface structure but differ in their foundational assumptions. We
consider everything to rest on the most basic relationship (cause -> effect),
with all other notions emerging only after clarifying what “time” and “distance”
mean in such a setting.

We offer short notes contrasting our model with several influential frameworks:

Causal-set theory [@bombelli1987] formalizes spacetime as a discrete partial
order but assumes a temporal orientation, excludes causal loops, and
reconstructs a Lorentzian manifold of fixed dimension. These assumptions are
stronger than those used here. Our model admits causal cycles and derives time
from them, rather than treating temporal order as a predefined primitive or
axiom.

Order-based treatments of spacetime, such as Kronheimer–Penrose
[@kronheimer1967], introduce a pre-existing “chronology” or “causally precedes”
relation as fundamental. In contrast, our model derives such relations from a
single primitive — cause produces effect — without assuming past, future,
monotonicity, or topology.

Information-theoretic approaches, including Wheeler’s “It from Bit”
[@wheeler1992] and Lloyd’s computational universe [@lloyd2002], place binary
decisions or computational operations at the foundation. We instead ask what
substrate makes any such operation possible to manifest in the first place;
cause-effect is not a decision, but the precondition for anything to occur. We
also avoid physical constructs (photons, particles, geometry) as primitives,
since these already presuppose structure.

Barbour’s relational timeless formulation [@barbour1999] questions global time
but still presumes structural relations between physical configurations
(astronomy, physical evidence), treating change as differences between states
and linking it to the Principle of Least Action. In our view, this Principle is
itself a manifestation of the deeper rule of cause-effect.

These and other works motivate but do not mirror the present approach. Here,
time, distance, and measurement emerge strictly from the combinatorial structure
of causal steps in a closed, stable Node.


## Conclusion

We have outlined a model in which:

1. A single, stable Node houses an incomputable internal structure of subnodes.
2. Subnodes interact via cause-effect relationships, establishing an intrinsic
   order.
3. *Time* emerges from the local ordering of cause and effect.
4. *Distance* emerges by counting how many steps are required for a subnode $i$
   to affect another subnode $j$ (or itself again in a loop).

This framework reproduces the key operational features of measurement: we build
clocks from repeated cause-effect loops, and we measure distances by the causal
chains needed to propagate signals. Hence, familiar constructs of time and space
follow naturally from the stable Node’s internal logic of cause and effect.

The framework supplies a pre-geometric canvas upon which any physical model may
be formulated, provided it admits causal influence.


## About Author(s)

An M. Rodriguez, an@preferredframe.com, https://orcid.org/0009-0009-9098-9468


## References

{#barbour1999} Barbour, J. (1999). *The Nature of Time*. arXiv:0903.3489 [gr-qc]

{#wheeler1992} Wheeler, J. A. (1992). *It from Bit: Recent thinking about the
nature of the physical world*. Annals of the New York Academy of Sciences,
656(1), 1–24. https://doi.org/10.1111/j.1749-6632.1992.tb17083.x

{#kronheimer1967} Kronheimer, E., & Penrose, R. (1967). *On the structure of
causal spaces*. Mathematical Proceedings of the Cambridge Philosophical Society,
63(1), 481–501. https://doi.org/10.1017/S030500410004144X

{#bombelli1987} Bombelli, L., Lee, J., Meyer, D., & Sorkin, R. D. (1987).
*Space-time as a causal set*. Physical Review Letters, 59(5), 521–524.
https://doi.org/10.1103/PhysRevLett.59.521

{#lloyd2002} Lloyd, S. (2002). *Computational capacity of the universe*.
Physical Review Letters, 88(23), 237901.
https://doi.org/10.1103/PhysRevLett.88.237901

Palma, A., Rodriguez, An M. (2025). *A cause–effect model for emergent time and
distance*. https://doi.org/10.13140/RG.2.2.35753.30569 (pre-print)