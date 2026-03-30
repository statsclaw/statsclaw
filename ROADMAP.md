# StatsClaw Roadmap

> **Vision**: Input a paper, a conversation, or a set of formulas — get a production-ready statistical package.

StatsClaw is building toward a world where statisticians and econometricians can publish their methods as installable packages without writing boilerplate. This roadmap tracks where we are and where we're headed.

---

## Phase 1: Foundation (Current)

- [x] Multi-pipeline agent architecture (leader, planner, builder, tester, scriber, reviewer, shipper)
- [x] Pipeline isolation (code / test / simulation never see each other's specs)
- [x] 8 language profiles (R, Python, TypeScript, Stata, Go, Rust, C, C++)
- [x] Workspace repo for runtime state and audit trails
- [x] Issue patrol — scan and auto-fix GitHub issues
- [x] Simulation study workflows (Monte Carlo, DGP, coverage)
- [ ] Comprehensive test suite for the framework itself
- [x] CI/CD pipeline for StatsClaw repo

## Phase 2: Paper-to-Package Pipeline

- [ ] PDF/LaTeX paper ingestion — extract algorithms, theorems, estimators
- [ ] Formula-to-code translation with mathematical verification
- [ ] Auto-generate unit tests from paper's simulation section
- [ ] Auto-generate vignettes/tutorials from paper's examples
- [ ] Support for common paper formats (arXiv, NBER, journal PDFs)

## Phase 3: Interactive Specification

- [ ] Long-form conversation mode — refine specs through dialogue
- [ ] LaTeX formula input → structured spec generation
- [ ] Visual diagram support (DAGs, model diagrams)
- [ ] Interactive simulation design — choose DGP parameters conversationally
- [ ] Incremental refinement — update package from follow-up papers

## Phase 4: Multi-Language & Ecosystem

- [ ] Cross-language package generation (same estimator → R + Python + Stata)
- [ ] CRAN/PyPI/npm submission automation
- [ ] Dependency management across ecosystems
- [ ] pkgdown / Quarto documentation site generation
- [ ] Stata SSC submission support

## Phase 5: Community & Scale

- [ ] Plugin architecture — community-contributed profiles and skills
- [ ] Shared estimator registry — browse and build on existing implementations
- [ ] Collaborative workflow — multiple contributors on one package
- [ ] Benchmark suite — auto-compare new estimator against existing methods
- [ ] Continuous integration for generated packages

## Phase 6: Intelligence

- [ ] Automatic literature review — find related estimators and compare
- [ ] Numerical stability analysis built into code generation
- [ ] Performance profiling and optimization suggestions
- [ ] Auto-detect edge cases from mathematical properties

---

## How to Influence This Roadmap

This roadmap is community-driven. You can shape it:

- **Feature requests**: [Open an issue](../../issues/new?template=feature-request.yml) with your idea
- **Paper-to-Package requests**: [Submit a paper](../../issues/new?template=paper-to-package.yml) you want turned into a package
- **Discussions**: Join the [Ideas discussion board](../../discussions/categories/ideas) to brainstorm
- **Direct contributions**: See [CONTRIBUTING.md](CONTRIBUTING.md) to get started

Every feature request and discussion thread feeds back into this roadmap. We review and prioritize monthly.
