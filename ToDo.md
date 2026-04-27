# ToDo

## GitHub README.md 작성

### 배경
CommonClaude.md 내용을 설명하는 README.md를 작성한다.
IDECommand.png, ShortCut.png 내용을 포함한다.

### 할 일

- [x] CommonClaude.md에 영어 작성 규칙 추가
- [x] README.md 작성 (영어)
  - [x] CommonClaude.md 내용 요약 및 설명
  - [x] IDE 명령어 정보 (IDECommand.png 참고)
  - [x] 단축키 정보 (ShortCut.png 참고)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## CLAUDE.md 규칙을 Claude Code Hooks로 구현

### 배경
CLAUDE.md에 정의된 코딩 규칙(린트, 디버그 파일 배치, 작업관리 등)을 Claude Code hooks로 자동 강제하여, "읽고 따르는" 수준에서 "시스템이 자동 검증하는" 수준으로 강화한다.

### 할 일

- [x] `ruff.toml` 생성 (line-length=80, indent-width=4)
- [x] `.claude/hooks/` 디렉토리 생성
- [x] `pre-write-guard.sh` 작성 — tests/에 디버그 파일 쓰기 차단 (§2)
- [x] `post-write-lint.sh` 작성 — Python 파일 ruff check + format 피드백 (§5)
- [x] `post-write-debug-remind.sh` 작성 — claude_test/ 파일 추가 시 README 리마인더 (§2)
- [x] `.claude/settings.json` 작성 — Hook 설정 + Stop prompt hook (§3 ToDo/이슈 확인)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## README.md에 /output-style 명령어 및 Hook 설명 추가

### 배경
README.md의 IDE Commands 표에 `/output-style`이 누락되어 있고, 직전에 추가된 Claude Code hooks 자동 강제 메커니즘에 대한 설명이 README에 없어 사용자가 프로젝트의 규칙 강제 방식을 이해하기 어렵다.

### 할 일

- [x] IDE Commands 표에 `/output-style` 행 추가
- [x] `Automated Enforcement (Hooks)` 섹션 신규 추가 (Convention Summary와 IDE Commands 사이)
- [x] GitHub 이슈 등록
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## Concept.md 내용 정리

### 배경
사용자가 Concept.md에 CommonClaude 개선 아이디어(ECC에서 선별 흡수할
Rule 재구조화, Token 최적화, Search-first, Learned Patterns 마이그레이션
등)를 작성하였다. 이를 읽고 섹션별로 구조화하여 사용자가 전체 구상을
한눈에 파악할 수 있도록 정리한다.
실제 적용은 본 작업 범위에서 제외하며, 이후 별도 세션에서 새 ToDo로
착수한다.

### 할 일

- [x] Concept.md 전체 내용 읽기
- [x] 6개 섹션으로 구조화된 요약 제공
      (철학 진단 / Rule 관점 / Rule 외 / 제외 항목 /
      Continuous-Learning 마이그레이션 Phase 0–5 / 최종 적용 순서)
- [x] GitHub 이슈 등록 (#12)
- [x] 커밋 및 푸시
- [x] GitHub 이슈 업데이트

---

## CommonClaude Improvement Track (from Concept.md)

### Background
Concept.md proposes seven incremental improvements adopted selectively
from ECC to strengthen CommonClaude while preserving its minimalist
philosophy. This entry decomposes that plan into seven independently
executable, independently rollbackable tasks. Each task gets its own
GitHub issue and its own commit. User approval is required at every
checkpoint marked **[APPROVAL]**. Phase 4 (continuous accumulation) is
a standing practice that begins once Tasks 1-7 land, and is therefore
not a discrete task here.

### Diagnosis Baseline (captured 2026-04-22)
- ToDo.md Completed: 4 top-level doc/setup tasks. Sample below the
  10-item threshold for pattern extraction; Task 5 will follow the
  "insufficient sample -> Phase 2 only" branch (Concept.md L99-101).
- CLAUDE.md: sections Overview, Environment, §1-§5 present. Missing:
  priority-override statement, Exceptions subsections, Research
  Before Coding section, Learned Patterns Reference section.
- Hooks present: pre-write-guard, post-write-lint,
  post-write-debug-remind, Stop prompt. Missing: Bash secret scan,
  Read env-file guard.
- MCP: no MCP config exists in repo. Task 3 is effectively null op
  unless the user decides to add filesystem MCP.

### Task 1. Restructure CLAUDE.md rule layer
Risk: low. Rollback: `git revert`.
Bundled with Tasks 2 and 4 under issue #14 per user decision.
- [x] Add priority-override statement near the top of CLAUDE.md
      ("Project-level CLAUDE.md rules override this global file")
- [x] Add Exceptions subsection under §2 Debug Files (waive 80-col
      and docstring requirements inside `claude_test/`)
- [x] Add Exceptions subsection under §4 Testing (allow magic
      numbers in one-off exploratory scripts when intent comment
      is present at file top)
- [x] **[APPROVAL]** Bundled approval granted 2026-04-22
- [x] GitHub issue register and cross-link (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 2. Add token-optimization env vars
Risk: low. Rollback: `git revert`.
Bundled with Tasks 1 and 4 under issue #14 per user decision.
- [x] Add `env` block to `.claude/settings.json` with
      `MAX_THINKING_TOKENS=10000` and
      `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50`
- [x] Verify existing `hooks` block is untouched
- [x] **[APPROVAL]** Values confirmed as-is per user 2026-04-22
- [x] GitHub issue register (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 3. MCP reconfiguration decision
Risk: low (decision only). Rollback: n/a (no repo change).
Resolved by user 2026-04-22: keep Context7 MCP as-is. No repo MCP
config is introduced. This task closes without file changes.
- [x] User decision: keep Context7 MCP, add nothing else
- [ ] GitHub issue register and close immediately as "no change"

### Task 4. Add Search-first section to CLAUDE.md
Risk: low. Rollback: `git revert`.
Bundled with Tasks 1 and 2 under issue #14 per user decision.
- [x] Draft a new §6 "Research Before Coding" covering doc lookup,
      prior-implementation search, and the rule against guessing
      APIs from memory
- [x] **[APPROVAL]** Bundled approval granted 2026-04-22
- [x] GitHub issue register (#14)
- [x] Commit and push (aa15cb9)
- [x] GitHub issue update (#14 closed)

### Task 5. Phase 0-1 diagnosis and (abridged) pattern extraction
Risk: low. Rollback: discard draft file.
Tracked under issue #16.
- [x] Document diagnosis outcome: sample < 10, Phase 1 extraction
      skipped per Concept.md L99-101 (recorded in #16 body)
- [x] Produce a short seed list of candidate patterns from the
      four Completed tasks plus current session — five
      workflow-level lessons L1-L5 (recorded in #16 body)
- [x] Superseded by #19 which applied the full §10 Bootstrap
      extraction across all ToDo.md Completed items; seed list
      content preserved in LearnedPatterns.md §4 Workflow Lessons
      (commit 24b6349). #16 closed 2026-04-22.

### Task 6. Create LearnedPatterns.md and wire it into CLAUDE.md
Risk: low. Rollback: delete file + `git revert` CLAUDE.md.
- [ ] Create `LearnedPatterns.md` seeded with Task 5 output and
      the section skeleton (§1-§5) from Concept.md L131-164
- [ ] Add §7 "Learned Patterns Reference" to CLAUDE.md instructing
      Claude to consult `LearnedPatterns.md` before drafting ToDo
- [ ] **[APPROVAL]** Show both artifacts
- [ ] GitHub issue register
- [ ] Commit and push
- [ ] GitHub issue update

### Task 7. Add secret-scan and env-file-guard hooks
Risk: medium (false positives can block legitimate work).
Rollback: disable in `settings.json` + `git revert` scripts.
- [x] Write `.claude/hooks/pre-bash-secret-scan.sh` blocking
      Bash commands that contain `sk-`, `ghp_`, `AKIA`, or
      obvious password literals (expanded to cover more vendor
      prefixes and `api_key=` / `access_token=` / etc.)
- [x] Write `.claude/hooks/pre-read-env-guard.sh` blocking
      reads of `.env`, `.pem`, `.key` (renamed from
      `pre-read-envfile-guard.sh` per user 2026-04-22)
- [x] ~~Add fixture scripts under `claude_test/`~~ dropped per
      user 2026-04-22; manual verification scenarios used instead
- [x] Wire both hooks into `.claude/settings.json` under
      `PreToolUse` with matchers `Bash` and `Read` respectively
- [x] **[APPROVAL]** Demonstrated block behaviour live in session
- [x] GitHub issue register (#15)
- [x] Commit and push (72fef2c — landed alongside Task 5 update)
- [x] GitHub issue update (#15 closed)

### Task Ordering and Independence
- Tasks 1, 2, 4 are independent and may be executed in any order.
- Task 3 is a decision gate and can run in parallel with others.
- Task 5 must precede Task 6.
- Task 7 is self-contained but its fixtures must land together
  with the hook scripts.

### Out of Scope
- Phase 4 ongoing accumulation: standing workflow, begins after
  Tasks 1-7 land.
- Phase 5 Stop-hook extension: deferred until pattern accumulation
  demonstrates a real need.

### Meta-task checklist (this drafting session)
- [x] GitHub umbrella issue registered (#13)
- [x] Commit and push draft (84d99f5)
- [x] User approved plan; Tasks 1+2+4 bundle executed in aa15cb9
- [x] Umbrella issue updated to reflect bundle closure

---

## Task 7 execution: secret-scan and env-file-guard hooks

### Background
Executing Task 7 from the umbrella plan (#13). Scope refinements
agreed with the user on 2026-04-22:
- Rename `pre-read-envfile-guard.sh` -> `pre-read-env-guard.sh`
  to match the user's preferred filename.
- Expand Bash scan to include `api_key=` literal in addition to
  `sk-`, `ghp_`, `AKIA`, `password=`.
- Drop `claude_test/` fixtures; use manual verification scenarios
  supplied by the assistant.

Verification strings such as `sk-test1234567890abcdef` are
illustrative test tokens, not real credentials.

### Work items
- [x] Write `.claude/hooks/pre-bash-secret-scan.sh`
- [x] Write `.claude/hooks/pre-read-env-guard.sh`
- [x] `chmod +x` both scripts
- [x] Register both hooks in `.claude/settings.json`
- [x] Manual verification: `sk-*`, `ghp_*`, `password=`, `api_key=`
      blocked via Bash; `.env` blocked via Read; benign `ls`
      command and `README.md` read pass through
- [x] GitHub issue register (#15)
- [x] Commit and push (72fef2c)
- [x] GitHub issue update and tick remaining Task 7 boxes

### Side fix
- [x] Install `jq` via apt; the existing three hooks also depend on
      it and were silently no-op'd before this fix.

### Scope notes
Bash pattern set finalized as: `sk-`, `ghp_`, `gho_`, `ghu_`, `ghs_`,
`github_pat_`, `AKIA*`, `AIza*`, `xox[baprs]-*`, `glpat-*`, plus
generic literal assignments `password=`, `api_key=`, `access_token=`,
`secret_key=`, `auth_token=`. Expanded beyond the original five per
user direction "암호 뿐만 아니라 API 키도 거부하도록".

---

## CLAUDE.md §7 — Learned Patterns Bootstrap rule

### Background
Splits Task 6 of the umbrella plan (#13) into Part A (rule) and
Part B (generate the file). User directed adding the bootstrap
procedure to `CLAUDE.md` now, so future sessions know how to
generate `LearnedPatterns.md` from `ToDo.md` when it is absent.
Tracked under issue #17.

### Rule outline
- Classify `[x]` items into §1-§5 plus §99 fallback.
- Each entry: Problem / Cause / Fix / Rule (one-liner each).
- Append `(from ToDo#N)` for traceability.
- `ToDo.md` stays append-only; `LearnedPatterns.md` is a new
  file in repo root; content in English; ambiguous items go
  to §99 rather than being guessed.

### Work items
- [x] Add §7 "Learned Patterns Bootstrap" to `CLAUDE.md`
- [x] GitHub issue register (#17)
- [x] Commit and push (4628a61)
- [x] GitHub issue update (#17 closed)

---

## CLAUDE.md restructure — Rule Priority, Exceptions, Learned Patterns Reference

### Background
User direction 2026-04-22: promote the existing `## Priority`
subsection and the two `### Exceptions` subsections to proper
numbered top-level sections, and add a new `Learned Patterns
Reference` section (distinct from the generation-rule §7
`Learned Patterns Bootstrap` that just landed). Tracked under
issue #18. No file change until the diff preview is approved.

### Work items
- [x] Draft proposed numbering map and new-section text
- [x] GitHub issue register (#18)
- [x] **[APPROVAL]** User approved 2026-04-22
- [x] Apply restructure (renumber §1-§7, add §1 Rule Priority,
      add §8 Exceptions, add §9 Learned Patterns Reference,
      move former §7 to §10 Learned Patterns Bootstrap)
- [x] Update internal cross-references (§1 Structure ->
      §2 Structure; §1 Documentation -> §2 Documentation;
      §1 Language rule -> §2 Language rule)
- [x] Commit and push (b2a39a1)
- [x] GitHub issue update (#18 closed)

---

## CLAUDE.md §8 — ToDo.md checkbox update exception

### Background
User direction 2026-04-22: the append-only rule in §4 Task
Management Rule 2 and the "do not modify ToDo.md" constraint in
§10 Learned Patterns Bootstrap were written to preserve history,
not to prohibit progress marking. Every task-completion step
flips a `[ ]` to `[x]`; this behavior needs an explicit carve-out
so future sessions do not misread the rule. Tracked under issue
#20.

### Work items
- [x] Add `ToDo.md checkbox updates` subsection under §8
- [x] GitHub issue register (#20)
- [x] Commit and push (17dee39)
- [x] GitHub issue update (#20 closed)

---

## Task 6 Part B — generate LearnedPatterns.md

### Background
Executes the §10 Learned Patterns Bootstrap procedure (added in
commit 4628a61, §7 at the time, §10 after restructure b2a39a1) to
materialize `LearnedPatterns.md` in the repo root. Classifies every
`[x]` item across `ToDo.md` into §1-§5 plus §99 per the bootstrap
rules. Task 5 seed list (#16) feeds into §4 Workflow Lessons but
the full analysis scans every Completed item, not just that seed.
Tracked under issue #19.

### Work items
- [x] Classify every `[x]` item in `ToDo.md` per CLAUDE.md §10
- [x] Write `LearnedPatterns.md` in repo root with 15 patterns
      across §1-§5 plus a §99 Uncategorized residual
- [x] GitHub issue register (#19)
- [x] Commit and push (24b6349)
- [x] GitHub issue update (#19 closed)

---

## Concept.md coverage verification

### Background
User asked whether every recommendation in `Concept.md` has been
reflected in the repo. This task cross-checks Concept.md's two parts
(Part 1 items 1-7, Part 2 Phase 0-5) and the final application order
L197-204 against landed commits, surfacing any gaps for decision.
Tracked under issue #21.

### Work items
- [x] Map each Concept.md recommendation to a commit or decision
- [x] Produce Done / Partial / Deferred table
- [x] Identify remaining gaps for user decision
- [x] GitHub issue register (#21)
- [ ] Commit and push
- [ ] GitHub issue update

---

## 7segment_reader.py robustness on SegmentTest folder

### Background
`7segment_reader.py` was tuned to decode `camera_samples/dev_video6_640x480.jpg`
but failed on most of the 31 photos in `SegmentTest/`. User goal: reach
at least 90% accuracy across that folder while keeping the reference
sample working.

Three failure modes were identified and addressed in `7segment_reader.py`:

1. **Hollow strict mask** -- bright LED segments saturate the camera
   (R = G = B = 255) so `R - max(G, B) > 100` only marks the segment
   outline. Segment-region sampling on a hollow ring under-counts.
   Fix: `fill_small_holes` seals enclosed background components below
   200 px (segment-internal voids ~80-150 px) while preserving genuine
   digit interiors (digit 0 ~700-940 px, digit 8 halves ~240-340 px).
2. **Italic font slant misaligns sample regions** -- vertical segments
   like b, c, e, f drift horizontally over a digit's height. Fix: the
   new `segment_ratio` shears each row of vertical-segment regions by
   `slant * (h/2 - y)` (slant = 0.25), and translates horizontal
   regions uniformly by the slant computed at their vertical centre so
   bleed from segment c into segment d is suppressed for digits like 7.
   `ON_THRESHOLD` lowered from 0.35 to 0.28 to absorb residual misalignment.
3. **Decimal probe over-gated on the row median** -- italic segment c
   tails creeping into other digits' lower-right probe windows raised
   the row median, blocking legitimate dot insertion.
   Fix: `DOT_RATIO_OVER_MEDIAN` lowered from 2.0 to 1.5.

Ground truth correction made during verification: `2026-04-27-165347.jpg`
ground truth corrected from `22.08` to `22.88` after inspecting the
strict-mask intermediate (segment g of digit 3 is clearly lit).

### Work items
- [x] Establish ground truth for all 31 SegmentTest images
- [x] Add `fill_small_holes` and call it from `read_display`
- [x] Add `segment_ratio` with per-row shearing for vertical segments
      and uniform shift for horizontal segments
- [x] Tune `ON_THRESHOLD` (0.35 -> 0.28) and `DOT_RATIO_OVER_MEDIAN`
      (2.0 -> 1.5)
- [x] Verify `>= 90%` exact-match accuracy on SegmentTest folder
      (achieved 28/31 = 90.3% both rows; V 30/31 = 96.8%, A 29/31 = 93.5%)
- [x] Verify reference image `dev_video6_640x480.jpg` still decodes
      to V=00.01 / A=0.000
- [x] GitHub issue register (#5)
- [ ] Commit and push
- [ ] GitHub issue update

---

## Export SegmentTest ground truth vs prediction as CSV

### Background
After landing the robustness changes (issue #5), the user asked for a
CSV summary so the per-image ground truth and prediction can be
inspected outside the eval script.

### Work items
- [x] Extend `claude_test/eval_segmenttest.py` to also write a CSV
- [x] Generate `segmenttest_results.csv` at the repo root
- [ ] GitHub issue register
- [ ] Commit and push
- [ ] GitHub issue update

---

## README.md — 7-Segment Reader pipeline section

### Background
User asked to document the `7segment_reader.py` pipeline in `README.md`
using the step-by-step debug images (strict mask, loose mask, decoded
overlay) generated for `SegmentTest/2026-04-27-165316.jpg`. The
existing README describes the CommonClaude conventions; the new
section is appended without disturbing that content.

### Work items
- [x] Persist the four pipeline images (input + three masks) under
      `docs/pipeline/` so they survive future `--debug` overwrites
- [x] Append a `## 7-Segment Display Reader (7segment_reader.py)`
      section to `README.md` between Cowork Session Rules and
      References, embedding the four images and walking through each
      stage (red score, STRICT + hole-fill, LOOSE, blob clustering,
      italic-aware segment sampling, decimal probe)
- [x] Link the SegmentTest accuracy CSV
- [ ] GitHub issue register
- [ ] Commit and push
- [ ] GitHub issue update

---

> NOTE: Entries below this line reference issues on
> `coport-uni/7SegmentReader`, not on `coport-uni/CommonClaude`.
> The local repo was bootstrapped from CommonClaude conventions but
> the project-specific work targets 7SegmentReader.

---

## Multi-camera device identifier (camera_finder.py)

### Background
컨테이너에 RealSense, Logitech C922, HikVision (v4l2loopback)이 동시에
연결되어 `/dev/video0..20`에 11개 노드가 노출됨. 어느 device가 어느 물리
카메라인지 시각적으로 매핑할 도구가 필요. OpenCV로 각 노드 한 프레임씩
캡처하여 device 경로명을 그대로 파일명에 박아 저장.

### Work items
- [x] `camera_finder.py` 작성 — V4L2 backend, warmup 5 frames, output
      `camera_samples/dev_videoN_WxH.jpg`
- [x] `python3-venv` 셋업 + `opencv-python-headless` 설치 (PEP 668 우회)
- [x] 1차 실행: 11개 중 5개 device 성공 (RealSense ×2, HikVision ×3),
      C922(/dev/video6,7) open-failed
- [x] Sub-issue #1 (C922 정상화) 별도 처리 후 closed
- [x] 2차 실행: 6/11 success — `dev_video6_640x480.jpg` 추가 확보
- [x] GitHub issue register (#2)
- [x] Commit and push
- [x] GitHub issue update

---

## 7-segment LED reader for DC power supply (7segment_reader.py)

### Background
`camera_samples/dev_video6_640x480.jpg` (C922 촬영 DC power supply LED
디스플레이)에서 V/A 값 자동 인식. 사용자가 ssocr 후보를 검토했으나, 글레어 /
tilt 조건상 OpenCV 전처리가 정확도의 80%를 결정하므로 hand-rolled
7-segment decoder가 더 적합하다고 판단 (plan 승인 후 구현). 이슈 #3.

### Work items
- [x] OCR 후보 평가 + plan 작성/승인
      (`/root/.claude/plans/camera-samples-...quilt.md`)
- [x] 1차 시도: HSV `inRange` 기반 mask → 글레어 미제거 + decimal point
      검출 실패
- [x] 2차 시도: `red_score = R - max(G, B)` 도입 → strict (score>100) /
      loose (score>60) 듀얼 threshold로 digit과 dim feature 분리
- [x] connected components 기반 digit blob 검출 + 7-segment lookup table
      디코더 (`SEGMENT_TO_DIGIT`, `SEGMENT_REGIONS`)
- [x] decimal point 검출: digit bbox 우하단 below-baseline probe의
      loose-mask pixel count → row 내 outlier (max ≥ median × 2)가 점 위치
- [x] `dev_video6_640x480.jpg`에서 `{"V": 0.01, "A": 0.0}` 정확 인식
- [x] `ruff check` / `ruff format` clean (E501·N806·I001 수정 후)
- [x] GitHub issue register (#3)
- [x] Commit and push
- [x] GitHub issue update

---

## Update ToDo.md and LearnedPatterns.md (session retrospective)

### Background
이번 세션 (camera_finder.py + 7segment_reader.py)에서 OpenCV LED 색
분리, decimal point 검출, 컨테이너 venv 셋업 등에서 얻은 교훈을
`LearnedPatterns.md`에 추가하고, 두 작업의 entry를 `ToDo.md`에 등록한다.
`.gitignore`도 신규 작성 (`.venv/`, `debug/`, `SegmentTest/`,
`__pycache__/`, `.ruff_cache/` 제외). 이슈 #4.

### Work items
- [x] `.gitignore` 신규 작성
- [x] `ToDo.md`에 위 두 작업 + 본 회고 entry 추가
- [x] `LearnedPatterns.md`에 §2 G5, §3 Q3·Q4·Q5, §4 W6·W7, §5 E4 추가
- [x] GitHub issue register (#4)
- [x] Commit and push
- [x] GitHub issue update
