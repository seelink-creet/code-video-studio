# Technique menu

Flags: **✅ proven in several finished films** · **🟡 tested in samples/tests, not fully delivered** · **⬜ unproven** (research only; do a 5 s technical test first and budget for trial and error).
Difficulty: ★ half a day · ★★ 1–2 days · ★★★ needs dedicated tuning or a new toolchain. "Example" entries are **invented illustrations**, not real works.

## A. Per-frame rendering (Python) — default route
| Technique | Good for | Diff. | Status | Example (invented) |
|---|---|---|---|---|
| PIL + numpy per frame, rawvideo pipe into ffmpeg | almost any 2D: paper, text, shapes, pixels, compositing | ★ | ✅ | ink dots grow into a line of text |
| OpenCV acceleration (lines, remap, blur, perspective) | many lines/particles/warps, much faster than pure PIL | ★ | ✅ | a thousand rays from the centre |
| Low-res grid × N nearest-neighbour | crisp pixel art | ★ | ✅ | 270×480 ×4 → 1080×1920 |
| Multiprocess chunk render + concat | faster, resumable long renders | ★ | ✅ | anything over 20 s |
| Supersample 2×/4× then downscale | thin lines, small text | ★ | ✅ | tiny distant text stays sharp |

## B. Simulation and procedural generation
| Technique | Good for | Diff. | Status | Example (invented) |
|---|---|---|---|---|
| Particles + forces (gravity, drag, wind, noise) | dust, sand, snow, smoke, scattered letters | ★ | ✅ | snowflakes pile into a character |
| Target attraction / morphing | text forming objects and back | ★★ | ✅ | a sentence gathers into a paper plane |
| Boids | flocks, schools, fireflies | ★ | ✅ | light dots turn like a school of fish |
| 2D fluid SPH/PBF (cKDTree) | pouring/splashing water or ink | ★★★ | ✅ | a glass of water tips over |
| Springs / cloth / PBD | paper, flags, ropes, grass | ★★ | ✅ | wind through grass with overshoot |
| Sound-driven visuals (phases, envelopes, FFT) | audio-visual pieces | ★★ | ✅ | each note draws a Lissajous curve |
| Procedural characters/sprites | small stories, promos | ★★ | ✅ | a pixel figure with a "!" above its head |
| Generative art (flow fields, L-systems, Voronoi, fBm) | abstract backgrounds, growth | ★★ | ✅ | branches grow from a corner |
| Numba/Taichi GPU sims | huge particle/fluid counts | ★★★ | ⬜ | a million-particle smoke |

## C. 2.5D / 3D
| Technique | Good for | Diff. | Status | Example (invented) |
|---|---|---|---|---|
| numpy perspective projection + camera path (PCHIP, smoothed heading) | flythroughs, pull-back reveals | ★★ | ✅ | flying through a tunnel of book pages |
| Flat cards in 3D (2.5D) | pages/posters/photos in space | ★★ | ✅ | postcards spiralling in the air |
| Per-pixel inverse mapping ("ray tracing" in numpy) | lensing, warped space, text on curved surfaces | ★★★ | ✅ | text orbiting a glowing sphere |
| G-buffer stylisation | one geometry, several looks | ★★ | 🟡 | one mountain as ink, charcoal and low-poly |
| three.js + Puppeteer/Playwright frame capture | real 3D, live scenes | ★★ | 🟡 | a cabin through day and night |
| Blender Python (`blender -b -P`) | real 3D, folding, cloth, realistic light | ★★★ | ⬜ | paper folding itself into a crane |

## D. Vector / motion graphics / layout frameworks
| Technique | Good for | Diff. | Status | Example (invented) |
|---|---|---|---|---|
| SVG rigged character → cairosvg → PIL | flat MG characters, explainers | ★★ | ✅ | a cartoon cat explains purring |
| PIL kinetic typography | slogans, captions, prices, promos | ★ | ✅ | numbers count 0→100 and bounce in |
| Charts / data viz (own drawing or matplotlib frames) | number stories | ★★ | ✅ | bars grow year by year |
| Remotion (React, `useCurrentFrame()`) | layout, templated batches, captions | ★★ | ⬜ | 10 product cards from one template (company use may need a paid licence) |
| HTML/CSS + GSAP (paused timeline, seek per frame) | web-style MG, titles | ★★ | ⬜ | no `Math.random`/`Date.now`; must be seekable |
| Motion Canvas / Revideo (TS) | explainers, code walkthroughs | ★★ | ⬜ | code highlighted line by line |
| Manim (Python) | maths/physics derivations | ★★ | ⬜ | a dissection proof of Pythagoras |
| Lottie (render frames from JSON) | icon/UI micro-animation | ★★ | ⬜ | a bouncing like icon |

## E. Shaders and generative-art frameworks
| Technique | Good for | Diff. | Status | Example (invented) |
|---|---|---|---|---|
| numpy "shaders" (vectorised per pixel) | glow, dispersion, post | ★★ | ✅ | white light splitting through a prism |
| GLSL fragment shaders (ModernGL / three.js / glslViewer) | noise, fractals, raymarching | ★★★ | ⬜ | an endless fractal tunnel |
| p5.js / Processing (headless frame saving) | generative art, watercolour brushes | ★★ | ⬜ | brush strokes filling a canvas (brushes can take seconds per frame without a GPU) |

## F. Other forms
| Technique | Good for | Diff. | Status | Example (invented) |
|---|---|---|---|---|
| Paper-white pixel mini-world (vignette, block dissolves) | cosy stories, game-like promos | ★★ | ✅ | a tiny figure finds a key under a tree |
| Text as matter (water, birds, stardust, carving) | poems, quotes, slogans | ★★ | ✅ | a line of verse falls as rain |
| Lyric-aligned MV (stem split → forced alignment → beat grid) | music videos | ★★★ | 🟡 | one shot per lyric line (song rights required) |
| ASCII / terminal animation | retro/geek | ★ | ⬜ | waves made of characters |
| Stills brought to life (Ken Burns, parallax) | portfolios, albums | ★ | ✅ | a year of travel photos in 30 s |
| TTS voice-over + captions | explainers, intros | ★ | ✅ | a 40 s narrated explainer |

## Choosing
- Ask what the viewer should feel: real physics only for weight and irreversibility; otherwise scripted motion + noise looks better and is easier to control (artistic truth over physical accuracy).
- No special request: the Python route (A + B). Heavy templated layout: Remotion/HTML (unproven, test first). Real 3D: try numpy 2.5D first, then Blender/three.js.
