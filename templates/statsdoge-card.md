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
Everything a future AI should learn from this package: full parameter tables with
defaults, edge cases, numerical-stability notes, benchmarks, and design decisions.
This section is exhaustive and never appears on the card.
