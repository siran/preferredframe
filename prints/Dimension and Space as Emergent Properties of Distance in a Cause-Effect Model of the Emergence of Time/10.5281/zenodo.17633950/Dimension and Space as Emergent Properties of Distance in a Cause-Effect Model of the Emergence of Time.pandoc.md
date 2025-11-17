% Dimension and Space as Emergent Properties of Distance in a Cause-Effect Model of the Emergence of Time
% Anes Palma, An M. Rodriguez
% November 17, 2025

## One-Sentence Summary

Dimension and space emerge from causal distances inside a single stable Node,
via approximate metric embeddings.


## Abstract

We extend a previously introduced framework in which time and distance arise
from internal causal relations within a single stable Node. In this work we
clarify that no metric, geometric structure, or fixed dimensionality is assumed
at the fundamental level. The Node is an abstract collection of subnodes linked
by causal influence, and any notion of "space" arises only from the distances
induced by causal chains. We show that observers may assign an
effective spatial dimension whenever these causal distances can be
approximately embedded into a D-dimensional space with low distortion.
Crucially, no particular dimension $D$ is preferred or fundamental: the same
causal structure may support multiple effective dimensional interpretations,
and the true underlying dimensionality is undefined. This liberates spatial
dimension from preconceived geometric constraints and treats it as an emergent,
observer-dependent property of causal relations rather than a fixed feature of
spacetime.


## Keywords

emergent spacetime, causal sets, relational physics, dimension, embeddings,
metric structure


## Introduction

Standard physics assumes that spacetime possesses a fixed number of spatial
dimensions. Even in discrete or relational approaches, approaches typically
begin with a target dimension or with structures designed to reproduce a chosen
geometry, or expected behavior. In contrast, the Node framework introduces no
geometric background, no predefined dimensionality, and it's agnostic to any
behavior encoded in the causal network: a single stable Node N contains
subnodes related by a causal order. Time emerges as the experience of this
ordering, and distance arises from causal-chain length. Beyond this, no metric
axioms, symmetry requirements, or geometric constraints are imposed.

In this work we examine how spatial dimension can itself emerge from the causal
structure. We do not define a new metric, nor do we restrict the causal network
to mimic any specific geometry. Instead, we allow the induced distance function
to be arbitrary, possibly asymmetric, and shaped solely by the causal behavior
of subnodes. When observers attempt to represent these distances within
$\mathbb{R}^D$, the success or failure of low-distortion embeddings determines
the effective dimensionality they assign to the system. This dimensionality is
not fundamental but reflects the perceptual or operational fit between causal
relations and manifold-like structures.

Thus the Node framework removes the assumption that space must possess a single
fixed dimension. A causal structure may be compatible with multiple dimensional
embeddings, or with none. Dimension becomes an emergent and potentially
non-unique property reconstructed by observers, rather than a fundamental
attribute of the underlying system.


## Recap of the Node Framework


### Structure of the Node

- Stable Node: a single entity $N$ with fixed total property (e.g., energy).
- Subnodes: a set $\{n_i\} {i \in I}$ of internal components.
- Causality: a partial order $\succ$ where $n_i \succ n_j$ means causal
  influence.


### Distance from Minimal Chains

For subnodes $n_i, n_j$, a causal chain of length $k$ is:

$$
n_i \succ n_{a_1} \succ \dots \succ n_{a_{k-1}} \succ n_j
$$

Distance $d(n_i,n_j)$ is the minimal $k$ for which such a chain exists. If none
exists, the distance may be infinite or undefined.

The choice of minimality as a notion of distance is clearly arbitrary.


### Time as an Ordering of Events

The relation $n_i \prec n_j$ expresses causal precedence. Recurrent cycles
allow local "clock" definitions: the count of causal steps gives a measure of
duration.


## Formalizing Emergent Dimension


### Metric-Like Properties

The distance function $d$ behaves like a graph distance. It may not be
symmetric, but when finite it provides a metric-like structure.

**Proposition (Pseudo-Metric)**
If the causal relation is acyclic and well-defined, $d$ induces a pseudo-metric
on pairs with finite causal connection.


### Approximate Embeddings and Effective Dimension

At large scales, if causal distances embed faithfully into $\mathbb{R}^D$, the
perceived geometry is $D$-dimensional.

**Definition (Effective Dimensionality)**
Let $\mathbf{N}$ be the set of subnodes with distance $d$.
A finite subset $S \subset \mathbf{N}$ embeds in $\mathbb{R}^D$ with fidelity
$\epsilon \ge 0$ if there exists
$$
\Phi : S \to \mathbb{R}^D
$$
such that for all $n_{i_p}, n_{i_q} \in S$:
$$
\bigl|\|\Phi(n_{i_p}) - \Phi(n_{i_q})\| - d(n_{i_p}, n_{i_q})\bigr| \le \epsilon.
$$
If arbitrarily large subsets embed with arbitrarily small $\epsilon$, the system
is effectively $D$-dimensional.


### Non-Unique Dimensionality

The Node framework places no requirement that a single dimension describe the
entire causal structure. Different regions may admit embeddings into different
Euclidean spaces.

**Theorem (Non-Uniqueness of Effective Dimension)**

Let $(\mathbf{N}, d)$ be the causal pseudo-metric defined by minimal causal
chains. If there exist two subsets $S_1, S_2 \subset \mathbf{N}$ and integers
$D_1 \neq D_2$ such that each admits arbitrarily low-distortion embeddings

$$
\Phi_k : S_k \to \mathbb{R}^{D_k}, \qquad k = 1,2,
$$

then the Node has no single effective dimension. Dimension is not a property of
the causal structure itself but of the embedding chosen by the observer.

**Corollary (Dimensional Degeneracy)**

If an observer samples only a subsystem whose causal distances embed well into
$\mathbb{R}^D$, the observer will infer dimension $D$ even when the full Node
admits no finite-dimensional embedding.

This makes clear why different theoretical frameworks may assign dimensions
such as $3$, $4$, $7$, $10$, or $11$ without contradiction: each describes a
different effective embedding of a different causal sector.


### Connections to Manifold-Like Behavior

Discrete causal structures often approximate manifolds at large scales. Our
definition captures this without assuming smoothness. If embeddings exist with
small distortion for $D=3$ or $4$, the system is effectively 3D or 4D.


## Discussion

The key implication of this extension is that spatial dimension is not a
primitive feature of the Node. The causal structure alone determines the
distances between subnodes, and any geometric interpretation is secondary.
Observers may assign an effective $D$ only when the induced distances admit a
low-distortion embedding into $\mathbb{R}^D$. Different regions or different
coarse descriptions may support different dimensional interpretations, and no
single "true" dimension exists at the fundamental level.

This view separates the Node framework from causal-set or quantum-gravity
approaches that aim to reproduce general relativity or assume a target
dimensionality. We do not require acyclicity, Lorentzian structure, or metric
conditions, and we allow causal loops. Distance asymmetry may occur, and if
such asymmetry prevents low-distortion embedding, that simply reflects that the
underlying causal relations do not support a geometric interpretation in that
domain.

What emerges is space as an effective construct: a manifold-like representation
chosen by observers because large causal regions admit faithful metric
embeddings. Dimension is therefore not fundamental, not unique, and not
guaranteed. It is an attribute of an embedding, not of the Node itself.



### Beyond Geometry: Matter and Fields

Additional physical properties (mass, charge, fields) might also emerge if
incorporated into the causal structure. Future work may define embeddings
preserving additional attributes, leading to emergent gauge fields or matter
excitations.



## Conclusions

Dimension arises rather than being postulated. Effective dimensionality follows
from approximate embeddings of causal distances into $\mathbb{R}^D$. Thus time,
distance, space, and dimension emerge from deeper causal relations within a
single stable Node.

Observers impose geometry because large causal regions admit faithful metric
embeddings.


## About Author(s)

An M. Rodriguez, https://orcid.org/0009-0009-9098-9468, an@preferredframe.com


## References

[]{#NodePaper} Palma, A., Rodriguez, A.M., *A Cause-Effect Model for Emergent
Time and Distance*. Preferred Frame. DOI: https://doi.org/10.5281/zenodo.17613401

(pre-print) Palma, A., Rodriguez, A.M., *Dimension and Space as Emergent
Properties of Distance in a Cause-Effect Model of the Emergence of Time*.
ResearchGate. DOI: https://doi.org/10.13140/RG.2.2.26399.68003