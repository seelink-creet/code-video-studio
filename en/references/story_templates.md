# Beat-sheet templates
Pick one per theme and write it as | time | picture | camera/speed | sound | for the user to edit. Examples are invented.

**T1 Carrier object + meaningful text + transformation + afterglow (20–30 s).** An everyday physical object (water, candle, sand, snow, paper, smoke) + a text that is its metaphor (prefer public domain) + one irreversible change + a quiet ending (key line + small signature). Beats: hook/still 15–25% (frame 0 already moving) · disturbance 10–15% · event 20–25% (near-freeze → burst) · transformation 20–30% · afterglow 15–20% (quiet, but audible on a phone speaker). Check: metaphor is consistent; no big action at the very end; key line readable at final resolution.

**T2 Bookend.** First and last frames share camera and framing, but the meaning has changed. Example: a lit window at the start, the same window dark with a new plant on the sill at the end. Check with `qc_motion.py --bookend 0 <end>`.

**T3 Stop-and-go flythrough (30–60 s).** Hook 0–3 s → departure along a guide (a thread, a beam, a river) 1→3× → 4–6 stops, each a 0.6–1.5 s near-stop to read one thing (tilt-shift focus) → lowest point near-freeze 0.05× → 3–4× burst → return or pull-back reveal (log ease-out) → afterglow. Check: forward-only camera; next stop visible ahead; the music's section entry lands on the reveal.

**T4 Mini-world in three acts (40–60 s).** Everyday + small comedy (0–30%) → gaining a treasure (hold it up + sparkle) → crisis: light drained, treasure taken, night falls (30–60%) → charge (near-freeze) → one strike (~0.25 s) → light returns (60–85%) → recovery + small twist + quiet hold (85–100%). Check: motion and sound in the first 6 s; uneven action spacing; push in on key beats; gags need no text.

**T5 Promo with CTA (30–45 s).** Hook → 3–6 selling-point scenes (≤5 s each, one action per shot) → climax → title + CTA as a separate transparent layer (edit text without re-rendering). Keep all copy in one config file; state whether visuals are dramatisations.

**T6 Explainer (20 s–3 min).** Misconception/question hook → idea 1 → idea 2 → counter-intuitive point (near-stop) → one-line summary → return to the opening image. Write the voice-over first; time picture to measured TTS. Cite data sources.

**T7 Portfolio / montage (45 s–3 min).** Cut by the music: opening hit on frame 0 → A → climax → near-stop → surge → return to the opening image + credit. All hits from one timeline; target 0-frame cue error.

**T8 Beat / lyric MV.** Analyse the track once (beats, bars, sections, energy, vocal alignment) and trust that one analysis; cut on beats in high energy, on phrases in calm parts; one shot per lyric, motivated transitions; lyrics are not the star. Confirm song rights.

General: one action per shot; no unexplained still over 2.5 s; the ending continues the climax's motion and logic; mark 2–3 near-freeze → surge points and 1–2 beats the music must hit.
