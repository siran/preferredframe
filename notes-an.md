# Notes on a preferred frame (medium for light)
------------------------------------

The idea is to explore the vast information we've shared over email.

- [Notes on a preferred frame (medium for light)](#notes-on-a-preferred-frame-medium-for-light)
- [Main ideas](#main-ideas)
  - [Doppler explains everything](#doppler-explains-everything)
  - [Gravity as Dielectric](#gravity-as-dielectric)
  - [we just need to convince ourselves](#we-just-need-to-convince-ourselves)
- [next steps](#next-steps)
  - [analyze frequencies of data](#analyze-frequencies-of-data)
- [Pet Projects:](#pet-projects)
  - [Electro Magnetic Compass keychain](#electro-magnetic-compass-keychain)
  - [Energy generation using our movement relative to the medium](#energy-generation-using-our-movement-relative-to-the-medium)
  - [Energy generation using the hypothesis that light speed changes with a dielectric medium as gravity](#energy-generation-using-the-hypothesis-that-light-speed-changes-with-a-dielectric-medium-as-gravity)
  - [Casimir-force-driven motor (force felt by to parallel conducting plantes when brought close to each other)](#casimir-force-driven-motor-force-felt-by-to-parallel-conducting-plantes-when-brought-close-to-each-other)
  - [measure one-way speed of light](#measure-one-way-speed-of-light)
  - [Use 3b1b's library to do simulations of our measurements](#use-3b1bs-library-to-do-simulations-of-our-measurements)



# Main ideas
## Doppler explains everything
* Doppler explains the M&M experiment [^mm_doppler_osf]
* Doppler explains Figure 5 of An's Research Gate [^daily_variations_rg]

### Modern repetition of the Fizeau experiment
see [^modern_fizeau_experiment], mostly Figure 10 which shows that the Fizeau result is explained by dragging and not by relativiy (~=Frenel's Drag hypothesis [^fresnels_drag_from_sr_mathpages])

## Gravity as Dielectric

### questions
* why does a changing speed of light is experienced as a (gravitational) force?

moving away from a gravitational source, it's gravitational energy density diminishes and light speed increases.

a daily change in the maximum amplitude of the average of rotations (Fig 6 of [^daily]) means light is changing speed by 30%.

That means an increase in energy of everything.

Although this equation can't be trusted a priori withough further research with new hypothesis, at face value,

E = mc^2

would imply change of $\Delta E=E_2-E_1=m(1.3^2-1)=0.69$.

This seems to the "buoy analogy".

~I don't know of a material or method (hopefully, yet) that could take advantage of this change in energy.~


### Introduction
* There seems to be a medium that support light waves.
* The medium seems to be affected by energy density
  * in particular, gravitational energy density
  * gravity can be seen as a dielectric as per Maxwell eqs
    * dielectric constant K seems to be p^2 where p is energy density of space;
    * $c = c_o/\sqrt{p^2}$
    * $p = p* + p_{earth} + p_{moon} + ...$
    * however a hypothesis is to instead use the Barycenter [^barycenter] of the Solar System to calculate gravitational influence from the center of mass
      * see [Is it possible to calculate the barycenter of a planet with several moons](https://qr.ae/ps6SQe)
        * (this should be already available)

## We just need to convince ourselves
It is indeed difficult to convince the community as a whole since many (not all) are more interested in proving us wrong than to help us being right.

Others don't see it.

Other don't believe us, and they don't have to.

There should be a simple principle or effect that could prove first to us, withough a shred of doubt, the next logical step.

See for example (electro-magetic-compass-keychain)[(#electro-magetic-compass-keychain)

# Next steps

## Analyze frequencies of data

# Pet Projects:

## Electro Magnetic Compass keychain
I was thinking in a floating needle in the middle of a container.
    - The density of the fluid could be adjusted to allow free rotation of the needle (need to think what would cause this force... :/ );
    - since it's floating it might be super sensitive to gravity; the liquid should allow very easy movement with almost any resistance;
    - probably we can support the needle on one of its ends, and let it float at an angle;
    - the angle should change if we make it right.

## Energy generation using our movement relative to the medium

## Energy generation using the hypothesis that light speed changes with a dielectric medium as gravity

## Casimir-force-driven motor (force felt by to parallel conducting plantes when brought close to each other)
* we don't necessarily need to know the oscillation function, any oscillation could be useful if designed like a `check valve` or diode
* casimir's force seems to be proportional to energy density
* energy density varies as the Barycenter (solar system, earth-moon) moves around us
  * calculate coordinates of barycenter and fit to plots
    * earth-moon
    * earth-sun-moon

## Measure one-way speed of light
* we can use Intensity of power measured as a proxy to distance traveled by light , $\displaystyle I \propto \frac{1}{r^2}$
* intensity can be measured consecutively at the receiver's end, it should drop as $1/r^2$; can one way speed of light be inferred this way?

## Use 3b1b's library to do simulations of our measurements

## Replicate de Witte's experiment with fiber optic cables
 Roland De Witte's experiment [^de_witte_coaxial_xch]
 I believe this has already been done and reported for a M&M setup.

---
### References

[^mm_doppler_osf]: "Classical Doppler Shift Explains the
Michelson-Morley Null Result" https://osf.io/preprints/osf/vkb2z

[^daily_variations_rg]: "Daily variations of the amplitude of the fringe shifts observed when an air-glass Mach-Zehnder type interferometer is rotated" https://www.researchgate.net/publication/369529273_Daily_variations_of_the_amplitude_of_the_fringe_shifts_observed_when_an_air-glass_Mach-Zehnder_type_interferometer_is_rotated

[^modern_fizeau_experiment]: A moderm replication of the classical Fizeau experiment, clearly showing that the results can be explained by Galilean/classical physics of waves/Doppler http://labs.plantbio.cornell.edu/wayne/pdfs/FIZEAU.pdf

[^de_witte_coaxial_xch]: "The Roland De Witte 1991 Detection of Absolute Motion and Gravitational Waves" https://arxiv.org/abs/physics/0608205 An Rodriguez at the moment of this writing distances himself from the notion of "absolute movement". It may or may not exist; however the evidence I've seen only points to a signal traveling through a medium. In that respect, An Rodriguez does not rules out a mixture of media and waves as a practical explanation of the phisicality of all-there-is (doppler~galilean). There is no reason to believe - other than reasonable assumption - that there is no more detail to it.

[^barycenter]: `In astronomy, the barycenter (or barycentre; from Ancient Greek βαρύς (barús) 'heavy', and κέντρον (kéntron) 'center')[1] is the center of mass of two or more bodies that orbit one another and is the point about which the bodies orbit. A barycenter is a dynamical point, not a physical object. It is an important concept in fields such as astronomy and astrophysics. The distance from a body's center of mass to the barycenter can be calculated as a two-body problem. ` https://en.wikipedia.org/wiki/Barycenter_(astronomy)

[^fresnels_drag_from_sr_mathpages]: Fresnel's drag can be derived as an approximation to Special Relativity https://www.mathpages.com/home/kmath702/kmath702.htm
