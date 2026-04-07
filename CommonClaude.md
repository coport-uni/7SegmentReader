# CommonClaude.md

This file contains the project-wide conventions that **all Claude Code sessions** must follow when working in this repository.

## Environment

This project runs inside a **Docker container** with [Claude Code](https://claude.ai/code) as the primary development tool.

| Item              | Detail                                         |
|-------------------|-------------------------------------------------|
| Runtime           | Docker container (`--privileged`)               |
| OS                | Ubuntu 24.04 (Noble)                            |
| Dev tool          | Claude Code (CLI / VS Code extension)           |


## 1. MIT Code Convention

All code follows the [MIT CommLab Coding and Comment Style](https://mitcommlab.mit.edu/broad/commkit/coding-and-comment-style/).

### Naming

- **Variables and classes** are nouns; **functions and methods** are verbs.
- Names must be pronounceable and straightforward.
- Name length is proportional to scope: short for local, descriptive for broad.
- Avoid abbreviations unless self-explanatory. If unavoidable, define them in a comment block.
- Python conventions:

| Element    | Style        | Example               |
|------------|--------------|-----------------------|
| Variable   | `lower_case` | `joint_angle`         |
| Function   | `lower_case` | `send_action`         |
| Class      | `CamelCase`  | `FairinoFollower`     |
| Constant   | `lower_case` | `_settle_mid_s`       |
| Module     | `lowercase`  | `fairino_follower`    |

### Structure

- **80-column limit** for all new code.
- One statement per line.
- Indent with **4 spaces** (never tabs).
- Place operators on the **left side** of continuation lines so the reader can see at a glance that a line continues.
- Group related items visually with alignment.

### Spacing

- One space after commas, none before: `foo(a, b, c)`.
- One space on each side of `=`, `==`, `<`, `>`, etc.
- Be consistent with arithmetic operators within a file.

### Comments

- Use **complete sentences**.
- Only comment for **context** or **non-obvious choices**. Never restate what the code already says.
- Outdated comments are worse than none. Keep them current or delete them.
- TODO format:
  ```python
  # TODO: (@owner) Implement 2-step predictor-corrector
  # for stability. Adams-Bashforth causes shocks.
  ```

### Documentation

- All public functions and classes must have **docstrings** (PEP 257 / Google style).
- A docstring states **what** and **why**, not **how**.
- Include `Args:`, `Returns:`, and `Raises:` sections when applicable.

---

## 2. Debug File Management

All debug, exploratory, and throwaway test scripts must be saved in `claude_test/`, **not** in `tests/`.

### Rules

| Location        | What goes there                                      |
|-----------------|------------------------------------------------------|
| `tests/`        | Production-quality tests that are part of CI/CD.     |
| `claude_test/`  | Debug scripts, one-off experiments, diagnostic code. |

### When writing debug code

1. Create the file directly in `claude_test/` (e.g., `claude_test/debug_servo_timing.py`).
2. Add a one-line docstring at the top explaining the purpose.
3. If the debug script leads to a real fix, move the relevant parts into a proper test under `tests/` and delete or archive the debug version.

### README

`claude_test/README.md` is the index. When adding a new debug file, add a row to the table in that README describing what the file does and what was learned.

---

## 3. Task Management

### Rules

1. **ToDo.md 작성**: 사용자가 요구하는 모든 작업에 대해 `ToDo.md` 파일을 작성하고, 작업을 시작하기 전에 사용자와 내용을 확인한다.
2. **GitHub 이슈 등록**: 가능한 경우 `gh` CLI를 활용하여 Todo 목록과 내용을 GitHub 이슈로 등록한다.

### Workflow

1. 사용자의 작업 요청을 받으면 `ToDo.md`에 할 일 목록을 정리한다.
2. 사용자에게 `ToDo.md` 내용을 확인받는다.
3. 확인이 완료되면 `gh issue create` 명령으로 GitHub 이슈를 생성한다.
4. 작업 진행 중 완료된 항목은 `ToDo.md`에서 체크 표시한다.
