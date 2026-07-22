# What the package does (PackageName)

## Summary
One or two factual sentences describing what this method/package computes — shown under the title on the card.

## Metadata
- Source: -
- Tags: Tag One, Tag Two
- Cover: -

## Description
> Built with [StatsClaw](https://github.com/statsclaw/statsclaw). See the package repository for authoritative documentation.

The big picture in markdown: the problem this package solves, the estimand, and the
modelling assumptions. Inline math like $\tau$ and display math are supported:
$$Y_{it} = \alpha_i + \xi_t + e_{it}$$

## Results
The estimand and the headline numbers a user should expect — point estimate(s),
standard errors / intervals, and how to read the output object.

## Inputs
What goes in: the data shape (panel / cross-section), the required columns, and the
question the method answers.

## Input example
```text
id,t,y,d
1,2018,3.4,0
1,2019,3.9,1
```

## Figures
- none

## Steps

### 1. prep — Load and shape the data
- Note: What this step does and why it matters before estimation.

```r
df <- read.csv("panel.csv")
```

### 2. estimation — Fit the estimator
- Note: Call the package's main entry point; describe the key arguments.
- Formula: \hat\tau = \bar Y_1 - \bar Y_0

## AI Notes
Never shown on the card. This is the corpus StatsOtter's AI learns from, so it
carries everything a future AI should know about this package — and it must
still be useful if every link above died tonight. A serious one runs 6-18 KB.

Fill the `###` sections below from the run's own artifacts (`comprehension.md`,
`spec.md`, `implementation.md`, `audit.md`, `ARCHITECTURE.md`) plus the
package's real source and docs. Drop a section rather than stub it with a
guess. Two hard rules: a URL may only ACCOMPANY knowledge, never replace it;
and never invent an API, argument, default, number or citation — anything
unverified goes under Open questions, explicitly marked.

### Method identity
What it computes, its lineage, the defining paper (authors, year, DOI), and the
canonical implementation with the exact version or commit this doc describes.

### When to use / when not to use
Decision rules concrete enough to apply to a dataset, and the competing designs
with what makes this one lose.

### Assumptions
Each assumption stated formally, then how to check it, then what breaks when it
fails.

### Estimand and estimator
The formal notation, the estimating equation, and what is identified under what.

### API reference
Every user-facing function: signature verbatim, a table of every argument with
type, default and meaning, and the fields of the returned object.

### Data requirements
Data shape, required columns and their semantics, sample-size and balance
guidance, missing-data behaviour.

### Worked example
Runnable code on a named dataset, the output it actually produced, and how to
read that output.

### Interpreting the output
What each number means, plausible ranges, thresholds, common misreadings.

### Diagnostics
The checks to run and what a failure looks like.

### Failure modes and fixes
Symptom → cause → fix, with error strings quoted exactly as the package emits
them.

### Alternatives and comparisons
Sibling methods, when each wins, and how the estimates typically differ.

### Performance and scale
Complexity, memory, practical limits, parallelism.

### Provenance
Every source actually read: URL or file path, what was taken from it, the
version or commit, and the date.

### Open questions
What is still unverified or contested, so the next pass extends this document
instead of rewriting it.
