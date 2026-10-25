# Visual style menu
✅ proven in several finished films · 🟡 samples only · ⬜ new suggestion (unproven). Palettes are starting points; fonts should be OFL or otherwise commercially usable (verify). Examples are invented.

## ✅ 1. Text as matter (ink & paper)
Mood: rice paper, light ink, negative space, one touch of vermilion. Palette: paper `#F2ECDE`, ink `#1C1C20` (five ink tones via opacity .96/.82/.60/.34/.16), vermilion `#B02E22`. Fonts: LXGW WenKai, Noto Serif CJK, an OFL script or period serif for Latin. Tech: cached glyph particles + attraction/flocking/fluid; paper grain, ink bleed, light bloom, grain, vignette. Notes: letters loose and readable only on a closer look; big glyphs as structure, small as texture; don't split one glyph into parts; a fixed signature mark in one corner. Example: the words of a letter blow away as migrating birds.

## ✅ 2. Paper-white pixel mini-world (vignette)
Mood: cosy, playful, visibly procedural — a small lit patch of world. Palette: off-white paper `#EEE9DC`, 3–4 tones per material, one saturated key colour for the hero; night turns the paper deep blue, highlights stay, shadows not crushed. Fonts: a pixel font that covers CJK if needed (many don't). Tech: low-res grid ×4 nearest; noise-field boundary → ordered dither → 2–12 px multi-scale blocks scattering into the paper; several wind waves with a bright band. Notes: not a floating island with a dirt cross-section; gaps between tufts; tiny characters emote with symbols; integer scaling for chat versions. Example: a figure builds a snowman that the wind knocks over and that stands back up.

## ✅ 3. 3D flythrough / one take
Mood: awe, scale, speed, or nostalgia. Palette: deep space (black + gold/violet/cyan glow) or paper margins + an era's UI colours. Tech: numpy projection + smoothed camera + time remap + shutter streaks. Notes: forward only (QC: velocity along the view axis ≥0); the next stop visible ahead; same framing at start and end for a bookend; tilt-shift blur for elements that should be felt, not read (e.g. trademarks). Example: the camera flies through every page of a book and out of the back cover.

## ✅ 4. Motion graphics / flat vector characters
Mood: bright, dense, playful. Palette: light base + 2 accents + dark text (e.g. `#F7F4EC` / `#E8453C` / `#2E86DE` / `#1E1E28`). Tech: SVG rigs + cairosvg, PIL kinetic type, beat-synced SFX. Example: a coffee bean explains its journey to a cup.

## ✅ 5. Audio-visual (sound drives picture)
Mood: rational, elegant. Palette: black + gold/bone/cyan. Tech: picture and sound share the same oscillators/envelopes/FFT. Example: every note draws a glowing string.

## ✅ 6. Stills brought to life
Cinematic, letterboxed; Ken Burns, parallax, colour transitions. Only the user's own or licensed images; don't claim "all code" when external images are used. Example: a year of travel photos in 30 s.

## 🟡 7. One geometry, several renders (stone relief / particles / charcoal)
Compute the G-buffer once and swap shaders to show style samples.
## 🟡 8. Old map / hand-drawn chart
Parchment + dark brown ink + vermilion notes; lines grow, labels appear one by one.

## ⬜ New suggestions (test 5 s first)
Paper cut / pop-up book (hinged flat cards, page turn = scene change, paper foley) · watercolour/oil strokes (p5.brush or instanced strokes) · ASCII/terminal · neon/cyber (additive light, bloom, chromatic aberration) · claymation feel (12 fps poses + jitter + soft shadows) · isometric town · minimal geometry · data-journalism charts.

## General art rules
Float compositing, quantise last; fine grain against banding on light gradients, 10-bit if needed; scale line widths, font sizes, blur radii and particle sizes with resolution; no pure black/white; glow on its own additive layer; seeded or ffmpeg-applied grain to avoid flicker.
