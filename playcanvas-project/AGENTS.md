# AGENTS.md — Fidelity-First Repository Policy

> **This is a strict working policy for every AI agent editing this repository.**
> The objective is to reproduce **verified Fortnite assets and behavior**, not to make a game that merely looks or feels similar. Technical convenience, visual plausibility, and development speed never justify inventing missing original data.

## 1. Non-negotiable rules

1. **Never fabricate Fortnite data.** Do not invent or approximate assets, materials, textures, reticles, colors, geometry, dimensions, thickness, pivots, transforms, offsets, FOV values, timing, animation behavior, collisions, placement rules, or gameplay logic and present them as original.
2. **Research before implementation.** Search the repository's existing JSON files and `provenance.json` manifests first. Follow recorded source paths and verified dump references before starting a new search.
3. **A resource is not a behavior specification.** Possessing an original texture, mesh, animation, or material record does not establish how it was used in Fortnite.
4. **No evidence, no integration.** If any essential information is missing, do not wire a guess, placeholder, default asset, or approximately correct behavior into the live 3D experience. Preserve verified partial findings and clearly mark the implementation as blocked.
5. **Never forge certainty.** Do not claim that a source is original, a hash was checked, a version was confirmed, or a result was tested unless you actually verified it.
6. **Protect the architecture and existing behavior.** Keep concept-specific files together. Do not scatter configuration across unrelated global folders or change working gameplay during a structural refactor.
7. **Leave the repository understandable for the next agent.** AI agents are expected to maintain the codebase without relying on human cleanup. Every change must have an obvious home, clear dependencies, and traceable evidence.

These requirements override generic coding-agent habits such as filling gaps with sensible defaults, making a best-effort visual imitation, adding temporary placeholder art, or silently choosing approximate values.

## 2. Required workflow for every feature

Follow these steps **in order**:

1. **Understand the request and scope.** Identify the exact feature and which Fortnite version, character, asset variant, state, or mode the evidence applies to. If the source version is unknown, mark it unknown; do not assume a version.
2. **Inspect existing evidence.** Read the relevant concept directory, its local `provenance.json`, applicable parent manifests, and existing reference JSON. Avoid repeating previously documented research.
3. **Locate the original source.** Use recorded package paths (`archivePath`), exported object/package names, dependency references, and available authorized source dumps. A candidate path is a research lead, **not proof of an original binary match**.
4. **Verify source and dependencies.** Examine the source record or file directly. Check all source identifiers and hashes that can actually be checked. Trace materials, meshes, textures, skeletons, animation sequences, curves, socket/bone attachments, and any other dependencies the feature requires.
5. **Establish placement and behavior.** Determine the exact required information for the feature: coordinate system, unit conversion, scale, pivot, relative/world transforms, camera-space positioning, attachment, layering, collision geometry, visibility conditions, timing, state transitions, and interactions, **where applicable**. Use only verified values or reproducible derivations from verified evidence.
6. **Record evidence before runtime integration.** Create or update the relevant source-reference JSON and its nearby `provenance.json`, following existing formats. Record open questions explicitly outside the original source data; never insert fabricated source properties.
7. **Apply the integration gate.** Integrate the feature only if all data necessary for its intended behavior and rendering has been verified. Otherwise stop at the evidence/documentation stage and report precisely what prevents faithful integration.
8. **Implement with minimal change.** Follow the existing project architecture. Preserve unrelated gameplay and assets. Do not use default engine behavior as a substitute for unknown Fortnite behavior.
9. **Verify the implementation.** Run the relevant checks and, when possible, inspect the actual runtime. Test placements, animations, state changes, and visual output against available verified evidence. Report any test that could not be run.
10. **Report facts, not confidence theater.** State what was verified, what was implemented, which files changed, and what remains unknown or blocked.

Research thoroughly using **available, legitimate sources**, but do not promise that every missing asset can be found. A feature must remain blocked when the required evidence is not accessible. Never hide a research failure by inventing an equivalent.

## 3. Evidence and verification levels

Keep these concepts separate:

- **Source candidate:** A path, name, dump search result, or third-party claim suggests a match. It is not yet authenticated.
- **Resource verified:** The accessible file or source record has been inspected, its identity documented, and the applicable hashes verified. If only a derivative was inspected, say so.
- **Behavior verified:** The original usage, configuration, relationships, and applicable runtime conditions are supported by evidence, not inferred from appearances.
- **Integration verified:** The local implementation has been checked against verified source data and, where relevant, validated in a running scene.
- **Blocked / unknown:** Required evidence or validation is missing. This is an acceptable outcome; guessing is not.

Do **not** collapse these levels into one `verified` claim. In particular, a matching GLB/PNG hash verifies those **local bytes**, not necessarily the original `.uasset` bytes, original material/shader behavior, or Fortnite runtime placement.

## 4. Provenance and JSON contract

`provenance.json` files are part of the project's **evidence system**. Preserve their existing schemas, field names, meanings, and hierarchy. Do not replace them with a new invented format merely because a different one is convenient.

- The root `provenance.json` identifies the source dump and index instructions. Its `sourceDump.path` may refer to an external machine; **do not assume that path exists locally**.
- Local manifests commonly use `schemaVersion`, `folder`, `entries`, and `childManifests`. For each local file, preserve or update its actual `file`, `bytes`, `sha256`, and appropriate `status`.
- Source candidates may include `recordCandidates` containing `archivePath`, `kind`, `dumpLine`, `dumpByteOffset`, `dumpRowBytes`, `dumpRowSha256`, and `objectFields`. Record only values actually obtained from the source. Never invent a line number, byte offset, export name, source path, or digest.
- Intermediate assets may be described by `existingIntermediateExports`, with their own paths, sizes, digests, and `bytesMatchLocalFile`. A conversion must retain its chain of custody: **original package/source record → extracted or converted asset → file used by this project**.
- Distinguish digest semantics exactly: `sha256` is the SHA-256 of the named local file; `dumpRowSha256` is the SHA-256 of the **exact JSONL record bytes, including its line ending**, as described by the root manifest. Neither is automatically the hash of the original `.uasset` package.
- Do not infer ownership, authenticity, game version, or complete behavior from `archivePath` alone. Verify the source rather than elevating a `recordCandidates` entry into a confirmed original.
- When a new original reference record is found, save the factual export/reference data under the corresponding concept (usually its existing `reference/` directory), and register it in that directory's provenance manifest. Match the surrounding JSON structure where possible. Keep verified source fields separate from local implementation metadata.
- Hash the exact bytes after writing or moving any tracked file. Update the appropriate manifest entry, child-manifest links, and paths affected by the change. Never edit or rehash unrelated original assets without a justified reason.
- **Never fabricate a hash.** Calculate it from bytes you actually have. If the original bytes are unavailable, explicitly record that verification is unavailable; do not copy a derivative's hash into an original-file field.
- Maintain historical external paths as historical evidence, even if project directories have been reorganized. Do not rewrite an original Fortnite archive path to look like a local project path.

A missing source is not resolved by creating a JSON file containing guessed properties. JSON records must make future verification faster, not preserve assumptions as facts.

## 5. Strict 3D integration gate: examples

**Building / editing:** A verified edit texture or wall mesh alone does not authorize implementation. Before showing a supposed original editing interaction in the world, verify the relevant skin/mesh/material, geometry and thickness, UVs when relevant, whether the representation sits inside/on/outside the structure, pivot, dimensions, local orientation, alignment, animation, visibility states, collision or hit-testing behavior, and placement rules. Verify only the items genuinely required for that particular feature; do not invent any missing required item.

**Reticles / aiming:** An exact texture is insufficient if its original size, screen or camera position, scaling, state conditions, and applicable aiming behavior are unknown. Do not draw a generic crosshair as a substitute.

**Characters / emotes:** A verified animation clip is insufficient to infer skeleton compatibility, attachment offsets, root motion, blend transitions, sequencing, or effects. Validate the relationship before presenting it as faithful.

When data is incomplete, it is permitted to import and document verified **non-runtime** resources. It is **not** permitted to activate an approximate runtime version and call it original.

## 6. Repository layout and ownership

This is a PlayCanvas + TypeScript + Vite application, organized by **concept**, not by file type:

```text
src/
  main.ts                       # Application entry point
  inspector.ts                  # Optional development inspector
  app/
    engine/                     # Scene composition and lifecycle
    camera/                     # Camera behavior and camera references
    player/                     # Player movement and movement control
    skins/                      # Individual skins, meshes, textures, rig logic
    animations/
      movement/                 # Locomotion clips, mapping, related settings
      emotes/                   # Emotes and their assets
      sprays/                   # Spray actions and associated resources
      reference/                # Related original animation exports
    entorno/
      map/                      # World ground/map logic
      lighting/                 # Lighting
      shadows/                  # Shadows
    builds/                     # Build pieces, edit-mode assets, related data
    HUD/                        # FPS display and settings UI
```

**Responsibilities:**

- `src/main.ts` boots the PlayCanvas application; `src/app/engine/scene.ts` composes systems and manages scene lifecycle. **PlayCanvas is the rendering engine**. Do not build a redundant custom engine or turn `scene.ts` into a giant gameplay module.
- Keep the logic, assets, and reference configuration for each feature together, e.g. skin-specific configuration inside that skin's directory, camera settings inside `camera/`, and building evidence inside `builds/`.
- `player/` controls actual displacement; `animations/movement/` handles its visual animation mapping. Do not mix simulation and presentation just because they both involve movement.
- Do not create placeholder `physics`, `weapons`, `materials`, or other systems before they have a real, verified responsibility. If physics becomes necessary, use the appropriate supported PlayCanvas functionality and place feature-specific behavior with its owner.
- Maintain existing naming conventions unless a rename is explicitly requested; do not reorganize unrelated folders as a side effect.

### When a new feature has no obvious home

First examine nearby concepts and dependencies. **Ask the user where new code and assets should live when the choice changes the architecture.** If the user explicitly delegates the choice, or work must continue without an answer and a location is unambiguous, choose the smallest coherent location within the existing concept structure and explain it in the change summary. Do not create a new top-level directory by default. If architectural ambiguity would create meaningful risk, stop that part and request direction instead of guessing.

## 7. Code quality and change discipline

- Work as a long-term maintainer: modular responsibilities, clear names, minimal coupling, reusable helpers only when justified, and no dead code or duplicate implementations.
- Prefer small, reviewable changes. Do not overwrite entire files to make localized edits, and do not introduce unrelated refactors.
- Read the current source before editing. Respect existing conventions and TypeScript strictness. Keep build-time imports and resource URLs valid after file moves.
- Preserve existing gameplay constants, timing, animation mapping, and visual results unless an explicitly requested change is supported by verified evidence.
- Treat existing local-project behavior as **project behavior**, not proof that Fortnite originally behaved that way. Existing code and third-party tutorials are not primary evidence of original mechanics.
- Never silently replace missing original assets with generic PlayCanvas components, procedural textures, placeholder meshes, guessed materials, or similarly named assets.
- Keep source files, original exports, and local conversions distinguishable. Prefer non-destructive operations on archived assets.
- Update the local `provenance.json` whenever tracked files or paths change. Preserve the source chain rather than silently normalizing it.

## 8. Project commands and verification

Use the scripts defined in `package.json`:

```bash
bun install
bun run typecheck
bun run lint
bun run fmt
bun run build
bun run dev
```

Run the applicable checks before finishing; ideally typecheck, lint, format check, and build. Where browser/runtime access exists, test the affected feature in PlayCanvas and compare against verified original references. Do **not** claim success for commands or visual checks you could not execute.

The repository includes `.agents/skills/` and `.claude/skills/` for PlayCanvas workflows (including GLB inspection, runtime inspection, and visual verification). Use relevant skills when available, but **skills and engine examples are implementation aids, not evidence of original Fortnite data or behavior**.

`src/inspector.ts` exists but is not automatically wired to the Vite dev server in this repository version. Do not assume it is active.

## 9. Completion report — mandatory

Conclude each change with a brief, factual report:

1. **Implemented:** Features and file paths that actually changed.
2. **Original evidence:** Exact source paths and records used, verified hashes, and any required reproducible conversions.
3. **Verification:** Commands, tests, and comparisons that actually ran, plus failures or unavailable checks.
4. **Unknown or blocked:** Missing assets, properties, positioning, behavior, or original-version evidence; explain why no approximation was introduced.
5. **Architecture:** Any new folder or significant ownership decision, and why it fits the existing structure.

**Final principle: a faithful, incomplete implementation is better than a convincing but invented one. No data means no claim; no verified behavior means no faithful runtime implementation.**
