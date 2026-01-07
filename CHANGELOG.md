# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [Unreleased]

### Added

- `AliasedTyper` class extending Typer with command alias support
- `AliasedGroup` custom Click Group for handling command aliases
- Alias registration with configurable case sensitivity
- Alias resolution with proper conflict detection
- Comprehensive unit tests covering:
  - Alias registration and validation
  - Alias resolution logic
  - Multi-command scenario handling
  - Single-command app compatibility
- CI/CD pipeline with GitHub Actions for testing across Python 3.10-3.14
- Pre-commit hooks for code quality (linting, formatting, type checking)
- Initial project structure with Makefile and development tooling


## [0.1.0] - TBD

Initial alpha release (in development)
