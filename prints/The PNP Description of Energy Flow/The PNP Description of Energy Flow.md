% The PNP Description of Energy Flow
% Max Freet, Adrien Hale, An M. Rodríguez
% August 8, 2025

## Abstract

We formalize a scalar‐field‐based ontology of energy flow in the Point–Not–Point (PNP) framework.
All structure is modeled as oscillatory modes of a single real scalar field $U(x,t)$, with topological closure conditions defining observable form.
We derive, from $F = d(\star dU)$, the mode equations, closure constraints, and quantized winding numbers $(m,n)$.
Mode (1), the minimal self‐inverting oscillation, is shown to sustain a continuous energy flow with Möbius‐like phase inversion, without requiring vector potentials or a pre‐existing space.
Higher modes yield quantized circulation, topological charge, and helicity, reproducing key features of electromagnetic and quantum structures from first principles.
This work also provides a symbolic and conceptual description of the PNP framework, complementing our previously published PNP theory of gravitation.

## 1 Introduction

The PNP framework encodes electromagnetism and matter structure in a single scalar energy field $U$.
No gauge potentials or primitive background geometry are assumed.
Physical quantities emerge from the topology of closed oscillations in $U$.
In this view, “particles,” “waves,” and “fields” are relational expressions of $U$’s internal phase structure.

We develop here the mathematical description of PNP energy flow:
1. Scalar field formulation and its equivalence to source‐free Maxwell electrodynamics.
2. Mode closure conditions for self‐sustaining configurations.
3. Quantization of circulation and helicity from topology.
4. Ontological consequences: orientation, inside/outside, and even “space” are emergent.

## 2 Scalar field dynamics

Let $U: \mathbb{R}^3 \times \mathbb{R} \to \mathbb{R}$ be a smooth scalar field.
We define the field strength 2‐form:

$$
F = d(\star dU)
$$

The source‐free conditions are:

$$
dF = 0, \quad d\!\star F = 0
$$

Identifying:
$$
\mathbf{B} = \star dU, \qquad \mathbf{E} = \star d\!\star dU
$$
yields the standard Maxwell equations in vacuum.
Thus, all electromagnetic dynamics are encoded in $U$ without a vector potential.

Energy density and Poynting vector follow from the stress–energy tensor:

$$
u = \frac{\varepsilon_0}{2}(E^2 + c^2B^2), \quad
\mathbf{S} = \frac{1}{\mu_0} \mathbf{E} \times \mathbf{B}
$$

These quantities are completely determined by $U$.

## 3 Mode structure and closure

We define a **mode $(m,n)$** as a topologically closed oscillation of $U$ characterized by two winding numbers:
- $m$: loops around the major cycle of a toroidal embedding
- $n$: loops around the minor cycle

For a minimal spherical configuration (mode 1), use radial coordinate $r$:

$$
U(r,t) = A \sin(k r - \omega t)
$$

Boundary conditions for closure:

$$
U(0,t) = 0 = U(R,t)
$$

The standing‐wave condition is:

$$
k R = \pi
$$

The field completes half a wavelength across radius $R$, inverting phase at the center.

## 4 Orientation reversal and Möbius‐like phase inversion

At $r = 0$, $U$ and its gradient vanish:

$$
\nabla U = 0, \quad |U| = 0
$$

Define normalized orientation:

$$
\hat{n}(r) = \frac{\nabla U}{|\nabla U|}
$$

Approaching the node:

$$
\lim_{r \to 0^-} \hat{n} = -\lim_{r \to 0^+} \hat{n}
$$

This is continuous in phase space though discontinuous in naive vector representation — a Möbius‐like inversion in field orientation, not in physical space.
The energy flow inverts through a node, allowing a closed loop without a geometric twist.

## 5 Higher modes and topological invariants

For a toroidal configuration:

$$
U(\theta,\phi,t) = A \sin(m\theta + n\phi - \omega t)
$$

Here $(m,n)\in\mathbb{Z}^2$ are winding numbers.

**Topological charge**:
$$
Q = (m,n)
$$

**Helicity** (linking of field lines):
$$
H \propto \int \mathbf{A}\cdot\mathbf{B}\,d^3x \ \propto\ m n
$$

Higher modes correspond to more complex knotted and linked field structures.
Quantization of $(m,n)$ yields discrete circulation and helicity.

## 6 Ontological implications

Mode (1) shows that “flow” is definable purely from $U$’s oscillation pattern.
There is no requirement for a background space: the apparent “in” and “out” directions are projections of phase behavior.
Inside/outside, orientation, and geometric separation are emergent from the topology of $U$’s closed modes.

This supports a relational ontology:
- Space is the set of relations defined by $U$’s configuration.
- Orientation is a local property of phase transitions.
- Complex structure = nested, stable oscillations in $U$.

## 7 Conclusion

We have given a rigorous scalar‐field derivation of electromagnetic‐like dynamics from $F = d(\star dU)$ and classified the closed modes of $U$ by winding numbers $(m,n)$.
Mode (1) provides the minimal self‐inverting energy loop, while higher modes generate quantized topological invariants.
Orientation and space emerge as relational features of $U$’s phase structure.
This paper establishes the formal basis of the PNP ontology and complements our previously published PNP theory of gravitation.

## References

1. Palma, A., Rodríguez, A. M. & Freet, M., *Point–Not–Point: Deriving Maxwell Electrodynamics from a Scalar Energy Field and Explaining Particle–Wave Duality*, Aug 2025.
2. Binney, J., Tremaine, S., *Galactic Dynamics*, 2nd ed., Princeton Univ. Press, 2008.
3. Milgrom, M., *A modification of the Newtonian dynamics as a possible alternative to the hidden mass hypothesis*, ApJ 270, 365–370 (1983).
