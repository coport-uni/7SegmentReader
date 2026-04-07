# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a conventions repository that defines project-wide standards for Claude Code sessions. The primary artifact is `CommonClaude.md`.

## Key Conventions (from CommonClaude.md)

- **Code style**: MIT CommLab conventions — `lower_case` for variables/functions, `CamelCase` for classes, 80-column limit, 4-space indentation
- **Debug files**: Go in `claude_test/`, never in `tests/`. Update `claude_test/README.md` index when adding debug files.
- **Comments**: Complete sentences, context-only (no restating code). TODOs use `# TODO: (@owner) ...` format.
- **Docstrings**: Required on all public functions/classes (Google style with `Args:`, `Returns:`, `Raises:`).
- **Environment**: Docker container (Ubuntu 24.04, `--privileged`).
