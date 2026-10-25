# Music and sound

## 1. Ask the user (with options)
> How should it sound?
> A **pick an existing library track** (real-band feel, least effort) [default] — I'll make 2–3 candidate previews on the same picture for you to choose from
> B **compose in code** (MIDI + instrument samples; hits every visual beat precisely, needs more rounds)
> C **pure synthesis** (chip/electronic; fits pixel or tech styles)
> D your own music (confirm you have the rights)
> Also: **paid/licensed** or **free/open** sources? (section 2; for commercial work prefer paid or CC0/CC BY)
SFX default: synthesized by motion type (`scripts/sfx_synth.py`), plus real recordings (wind, rain, cloth, footsteps, breath) where texture matters.

## 2. Two sourcing directions
**Never hard-code a specific track or recording in the skill**: search per film and verify every licence.

### 2a. Paid / licensed libraries
- Kinds: subscription stock sites (music + SFX), per-track licensed music stores, one-off SFX packs, platforms' built-in commercial libraries.
- Check what the licence covers: **use** (personal / commercial / client work / paid ads), **platforms**, **term** (perpetual vs only while subscribed), **territory**, editing allowed, credit required, whether client projects need a separate licence.
- Keep evidence: receipts, licence certificates or the licence page at download time (PDF/screenshot with date and track ID), archived with the film and listed in `LICENSES`. Use them to dispute content-ID claims.
- Platform built-in music usually only works on that platform.

### 2b. Free / open sources
| Licence | Commercial? | Requirement | Verdict |
|---|---|---|---|
| CC0 / public domain | yes | none (credit is polite) | first choice |
| CC BY | yes | **credit required**: author, title, licence, link, in the author's format | usable |
| CC BY-SA | yes | credit + **derivatives under the same licence** (your soundtrack/film may have to be SA) | use with care; avoid for client/commercial work |
| CC BY-NC (incl. NC-SA, NC-ND) | **no** | — | not for commercial projects |
| CC BY-ND | depends | **no modification** (cutting, varispeed, mixing count) | practically unusable |
| "Royalty-free" | read the terms | every site differs; some forbid scripted downloads or resale | read per site |
Typical source kinds: composers' own sites publishing CC BY music, open music archives, public-domain classical recordings, Wikimedia Commons, CC0 SFX sites, free game-dev SFX packs, open instrument sample libraries (CC0 / CC BY).

**Rule**: for every asset open its licence page (licences change; mirrors mislabel), record "name / author / source URL / licence / date checked / modified?" in the project's `LICENSES.csv`, and put CC BY credit lines in the post (description, end card or pinned comment as the author requires). Unclear licence → don't use it.

## 3. Composing in code (B)
- pretty_midi score → instrument samples (prefer CC0, then CC BY with credit).
- **(Optional) open-source sampler**, e.g. the Python sampler in the open-source project lemo-opuscar (github.com/lemomo-ai/lemo-opuscar, MIT). It renders code-written MIDI with real instrument samples, so it sounds much better than generic GM synth. Not required; alternatives: sfizz with SFZ libraries, FluidSynth + a good SoundFont, or library music (option A).
- Avoid generic GM sounds. Some sample files are named an **octave lower** than they sound; measure with pyin/yin.
- Harmony must develop: change key/harmony/orchestration per section; **never loop one progression for the whole film**.
- 20–120 Hz about −3 dB relative to the rest; pads not below MIDI 48.
- Sound follows speed ramps: near-freeze → sustained tone / inhale / near silence; surge → swell + timpani **rolls** (not hits). Render held chords separately and varispeed them so later notes don't drift.

## 4. Fitting a library track (A)
- Prefer **one continuous take**: offset the track so its own section entry lands on the key visual beat: `music_fit.py fit --entry <track time> --beat <video time>`.
- If you must cut: on bar lines only, between harmonically similar bars, 20–30 ms crossfades; common three-part cut: track opening → cut into a fuller section on the impact → cut into the track's real ending so the final cadence lands under the title/hold.
- Carve a hole in the music during wind-ups so the impact lands.
- `music_fit.py analyse` lists candidate entries (bar lines with energy jumps) and breathing points for near-freezes. Mark edited CC BY tracks "(edited)".

## 5. SFX
By motion type (landing, whoosh, freeze, light/glass, click, shatter, charge, final collapse), 3+ variants rotated, never the same one twice in a row · no spring glides or cartoon Doppler (wobble ≤±0.5 st); charge-ups use sustained tones, not rising glides; pitched SFX on the music's pentatonic · no knock/tap transition sounds; use J-cuts (sound 0.3–0.5 s early) and L-cuts · equal-power ~0.6 s crossfades of ambience at cuts; passing time = one bed fades out as another fades in · recordings: find usable in-points from a 50 ms RMS envelope (onsets ≥20 dB below peak), declick transients, fade reversed breaths ~120 ms at the end.

## 6. Narrative pieces: four layers
Dialogue/VO > foley (every hand action) > ambience bed > music (sparse, underneath). VO ~10 dB above music; sidechain the music under VO and key foley. TTS (e.g. edge-tts, recent version): a natural voice, ~15–20% slower; split at commas and insert real pauses if pause tags aren't supported; check the TTS service's commercial terms. Real recorded voice for intimacy.

## 7. Mix and master
Default **−14 LUFS** (−16 for quiet, dynamic pieces), **true peak ≤ −1 dBTP**. Two-pass loudnorm (linear) + limiter; **AAC raises true peak, so measure after encoding** and back off the gain (`scripts/master_audio.py`). SFX bus 3–6 dB under music; a 1–2 dB music dip on impacts. If you cannot hear: level curves, onset and pitch detection, separate SFX/music stems; ask the user to listen once on headphones and name only "which second feels wrong".

## 8. Credit-line templates
- CC BY music: `"Title" by Author — licensed under CC BY 4.0 — source URL (edited)` (if the author gives a format, **copy it exactly**)
- CC BY samples: `Instrument samples: Library by Author — CC BY 3.0`
- CC0: optional `Additional sounds: source site`
- Fonts: `Font by Author — SIL Open Font License 1.1`
