# The 12 principles of animation + code recipes
Source: Frank Thomas & Ollie Johnston, *The Illusion of Life* (1981). Examples are invented.
Tools: `smoothstep(a,b,t)`, `ease_out(x)=1-(1-x)^3`, `ease_in(x)=x^3`, spring `x''=-k(x-x0)-c x'` (critical damping c=2√k; underdamped overshoots), and `scripts/timeremap.py`.

| # | Principle | In one line | Code recipe | Example (invented) |
|---|---|---|---|---|
| 1 | Squash & stretch | elastic things deform, volume stays | scale along velocity `sx=1+k·|v|, sy=1/sx`; on landing `sy<1, sx=1/sy`, rebound over 2–4 frames | a ball flattens and bounces (not paper or rigid bodies) |
| 2 | Anticipation | wind up before a big action | 0.15–0.6 s counter-move before the action plus a near-freeze (speed 0.05–0.1) | crouch before a jump; the frame "inhales" before a burst |
| 3 | Staging | show one thing at a time | negative space, brighten the focus, lower contrast or tilt-shift elsewhere, push in on key beats | push in 1.25–1.5× when a tiny figure acts |
| 4 | Straight ahead vs pose to pose | simulate vs interpolate keys | sims are straight ahead; characters/camera use keys + PCHIP (no overshoot) | hand-off from script to physics with pre-settle + smoothstep blend |
| 5 | Follow-through & overlap | parts keep moving after the body stops | appendages follow with delay + spring; phases offset | a scarf keeps swinging; grass tips rebound |
| 6 | Slow in & slow out | ease at both ends | easing everywhere, never linear; smoothstep between speed keys | camera pushes, cards sliding in, log-distance pull-back |
| 7 | Arcs | natural motion curves | quadratic/cubic Bézier or Catmull-Rom with sideways swirl | a paper plane's path |
| 8 | Secondary action | small supporting motions | independent small loops (blinks, tails, emoji, LEDs) with random phase | "…" or "!" popping above a head |
| 9 | Timing | frame counts set weight and mood | time remapping per section; characters "on twos" (12 fps poses) with a 24/30 fps camera | near-freeze → 3–4× surge; repeated actions not evenly spaced |
| 10 | Exaggeration | stronger than real to read | extra initial velocity, lower gravity, longer hang time; scale jumps, camera shake; global lift ≤0.07, no white-out | a splash twice as big and slower |
| 11 | Solid drawing | consistent volume, perspective, light | true projection in 2.5D; one light direction; brightness ∝ (REF/z)² with a cap | a rotating cube always lit from top-left |
| 12 | Appeal | likeable and readable | size contrast, readable key colour, clear silhouettes; randomise size/phase/frequency in crowds | a tiny figure found instantly by one bright colour |

Extras: motion blur by sub-samples (4 is enough) or streaks whose length follows speed; "boil" line jitter 8–12 reseeds/s, seeded per stroke; avoid twinning; motivated transitions (ink bloom, block dissolve, pass-through, scale jump, J/L-cuts) instead of generic dissolves/wipes.
