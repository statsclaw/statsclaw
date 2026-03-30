#!/usr/bin/env bash
# validate-structure.sh — Verify all internal cross-references in the StatsClaw framework
# Called by the CI workflow. Exits non-zero if any reference is broken.
set -uo pipefail

ERRORS=0
WARNINGS=0

error() { echo "::error::$1"; ERRORS=$((ERRORS + 1)); }
warn()  { echo "::warning::$1"; WARNINGS=$((WARNINGS + 1)); }
info()  { echo "  ✓ $1"; }

echo "═══════════════════════════════════════════════════"
echo "  StatsClaw Structure Validation"
echo "═══════════════════════════════════════════════════"
echo ""

# ─────────────────────────────────────────────────────
# 1. Required top-level files
# ─────────────────────────────────────────────────────
echo "▶ Checking required top-level files..."
for f in CLAUDE.md README.md CONTRIBUTING.md ROADMAP.md .gitignore; do
  if [ -f "$f" ]; then
    info "$f exists"
  else
    error "Missing required file: $f"
  fi
done
echo ""

# ─────────────────────────────────────────────────────
# 2. Agent completeness
# ─────────────────────────────────────────────────────
echo "▶ Checking agent definitions..."
EXPECTED_AGENTS="leader planner builder tester scriber simulator reviewer shipper"
for agent in $EXPECTED_AGENTS; do
  if [ -f "agents/${agent}.md" ]; then
    info "agents/${agent}.md"
  else
    error "Missing agent definition: agents/${agent}.md"
  fi
done

# Check for unexpected agent files (not necessarily an error, just a warning)
for f in agents/*.md; do
  [ -f "$f" ] || continue
  basename="${f#agents/}"
  basename="${basename%.md}"
  if ! echo "$EXPECTED_AGENTS" | grep -qw "$basename"; then
    warn "Unexpected agent file: $f (not in expected list)"
  fi
done
echo ""

# ─────────────────────────────────────────────────────
# 3. Skill completeness
# ─────────────────────────────────────────────────────
echo "▶ Checking skill definitions..."
for dir in skills/*/; do
  [ -d "$dir" ] || continue
  if [ -f "${dir}SKILL.md" ]; then
    info "${dir}SKILL.md"
  else
    error "Missing skill definition: ${dir}SKILL.md"
  fi
done
echo ""

# ─────────────────────────────────────────────────────
# 4. Template completeness
# ─────────────────────────────────────────────────────
echo "▶ Checking template files..."
EXPECTED_TEMPLATES="context status credentials mailbox lock log-entry ARCHITECTURE"
for tmpl in $EXPECTED_TEMPLATES; do
  if [ -f "templates/${tmpl}.md" ]; then
    info "templates/${tmpl}.md"
  else
    error "Missing template: templates/${tmpl}.md"
  fi
done
echo ""

# ─────────────────────────────────────────────────────
# 5. Cross-references in CLAUDE.md
# ─────────────────────────────────────────────────────
echo "▶ Checking file references in CLAUDE.md..."
# Extract backtick-quoted paths referencing known directories
# Skip glob patterns (containing *) and directory-only references (ending with /)
for dir in agents skills templates profiles; do
  grep -oP "\`${dir}/[^\`]+\`" CLAUDE.md | tr -d '`' | sort -u | while read -r ref; do
    # Skip glob patterns and directory references
    case "$ref" in
      *\**|*/) continue ;;
    esac
    if [ -f "$ref" ]; then
      info "CLAUDE.md → $ref"
    else
      error "CLAUDE.md references non-existent file: $ref"
    fi
  done
done
echo ""

# ─────────────────────────────────────────────────────
# 6. Cross-references in agent files
# ─────────────────────────────────────────────────────
echo "▶ Checking file references in agent definitions..."
for agent in agents/*.md; do
  [ -f "$agent" ] || continue
  grep -oP '\`(agents|skills|templates|profiles)/[^`]+\`' "$agent" 2>/dev/null | tr -d '`' | sort -u | while read -r ref; do
    case "$ref" in *\**|*/) continue ;; esac
    if [ ! -f "$ref" ]; then
      error "$agent references non-existent file: $ref"
    fi
  done
done
echo ""

# ─────────────────────────────────────────────────────
# 7. Cross-references in skill files
# ─────────────────────────────────────────────────────
echo "▶ Checking file references in skill definitions..."
find skills -name 'SKILL.md' | while read -r skill; do
  grep -oP '\`(agents|skills|templates|profiles)/[^`]+\`' "$skill" 2>/dev/null | tr -d '`' | sort -u | while read -r ref; do
    case "$ref" in *\**|*/) continue ;; esac
    if [ ! -f "$ref" ]; then
      error "$skill references non-existent file: $ref"
    fi
  done
done
echo ""

# ─────────────────────────────────────────────────────
# 8. Agent file structure (required sections)
# ─────────────────────────────────────────────────────
echo "▶ Checking agent file structure..."
REQUIRED_SECTIONS="Role:Allowed Reads:Allowed Writes:Must-Not Rules"
for agent in agents/*.md; do
  [ -f "$agent" ] || continue
  IFS=':' read -ra SECTIONS <<< "$REQUIRED_SECTIONS"
  for section in "${SECTIONS[@]}"; do
    if grep -q "^## $section" "$agent" || grep -q "^## ${section}$" "$agent"; then
      : # ok
    else
      warn "$agent missing recommended section: ## $section"
    fi
  done
done
echo ""

# ─────────────────────────────────────────────────────
# 9. No runtime artifacts committed
# ─────────────────────────────────────────────────────
echo "▶ Checking for committed runtime artifacts..."
if [ -d ".repos" ] && [ "$(find .repos -type f 2>/dev/null | head -1)" ]; then
  error ".repos/ directory contains files — runtime artifacts must not be committed"
else
  info "No runtime artifacts in .repos/"
fi
echo ""

# ─────────────────────────────────────────────────────
# 10. Profile files exist
# ─────────────────────────────────────────────────────
echo "▶ Checking language profiles..."
PROFILE_COUNT=$(find profiles -name '*.md' -type f 2>/dev/null | wc -l)
if [ "$PROFILE_COUNT" -ge 1 ]; then
  info "Found $PROFILE_COUNT language profiles"
else
  error "No profiles found in profiles/"
fi
echo ""

# ─────────────────────────────────────────────────────
# Summary
# ─────────────────────────────────────────────────────
echo "═══════════════════════════════════════════════════"
if [ "$ERRORS" -eq 0 ]; then
  echo "  ✅ All checks passed ($WARNINGS warnings)"
  exit 0
else
  echo "  ❌ $ERRORS errors, $WARNINGS warnings"
  exit 1
fi
