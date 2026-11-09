---
name: compliance-mapper
description: Maps security findings to compliance frameworks (OWASP Top 10, CWE, NIST SP 800-53, PCI DSS, SANS/CWE Top 25, ISO 27001) and generates audit-ready compliance reports
trigger:
  - map findings to compliance frameworks
  - generate compliance report
  - check OWASP coverage
  - check CWE coverage
  - check NIST coverage
  - check PCI DSS compliance
  - produce audit-ready documentation
  - compliance scorecard
  - compliance gap analysis
  - framework mapping
---

# Compliance Mapper Skill

This skill maps security findings to compliance frameworks and produces structured compliance reports. It is **language-agnostic** -- it operates on findings data, not source code.

## Accepted Input

Findings can come from:
- Other skills: SAST scanner, DAST scanner, dependency audit, security config review, secrets scanner, API contract testing
- Manual input: user-provided finding descriptions
- JSON or structured data: imported finding lists

Each finding should have (at minimum): title, severity, description. Location, source skill, and evidence are optional but improve report quality.

## Workflow

### Step 1: Findings Ingestion

Parse and normalize all incoming findings into a consistent internal format:

- **Finding ID**: Sequential identifier (FINDING-001, FINDING-002, ...)
- **Title**: Short descriptive name
- **Severity**: Critical / High / Medium / Low / Info
- **Source**: Which skill or tool produced this finding (SAST, DAST, Dependency Audit, Config Review, Secrets Scanner, API Contract Testing, Manual)
- **Location**: File path and line number, URL endpoint, or configuration file
- **Description**: What the vulnerability is and why it matters
- **Evidence**: Code snippet, request/response pair, or configuration excerpt

When ingesting from other skills:
- Review the findings already present in the conversation context
- Parse severity from the skill's own severity ratings
- Preserve the original finding detail for the evidence field
- If no findings are available, prompt the user to run a security skill first or provide findings manually

### Step 2: Framework Mapping

For each finding, use the Read tool to load the reference files and map to all applicable frameworks:

1. **OWASP Top 10 (2021)**: Assign the A01-A10 category. Use keyword matching against the finding title and description. Refer to `references/owasp_mapping.md` for category definitions and keyword associations.

2. **CWE**: Assign specific CWE ID(s). Match based on vulnerability type. Refer to `references/cwe_catalog.md` for the full catalog. A single finding may map to multiple CWEs.

3. **NIST SP 800-53 Rev 5**: Assign the control family and specific control(s). Refer to `references/nist_pci_mapping.md` for the mapping from vulnerability types to NIST controls.

4. **PCI DSS v4.0**: Assign the requirement number. Refer to `references/nist_pci_mapping.md` for the mapping from vulnerability types to PCI DSS requirements.

5. **SANS/CWE Top 25**: If the CWE is in the SANS/CWE Top 25 Most Dangerous Software Weaknesses list, note the ranking.

6. **ISO 27001:2022**: Assign the Annex A control reference based on the vulnerability domain (access control, cryptography, operations security, etc.).

### Step 3: Coverage Analysis

For each framework, determine coverage status:

- **Tested with findings**: Categories/controls where vulnerabilities were found
- **Tested clean**: Categories/controls that were tested and no issues found (infer from which skills were run and what they cover)
- **Not tested**: Categories/controls with no coverage from any skill or input

Build a coverage matrix showing the intersection of skills run vs framework categories covered. Identify blind spots where no testing has been performed.

### Step 4: Compliance Scorecard

Calculate posture metrics for each framework:

**OWASP Top 10:**
- X/10 categories with findings
- Severity breakdown per category (Critical/High/Medium/Low counts)
- Overall OWASP risk rating

**CWE Top 25:**
- X/25 weaknesses found
- List of found weaknesses with severity

**NIST SP 800-53:**
- Controls failing vs passing vs not tested
- Per-family status (AC, AU, CM, IA, SC, SI, etc.)
- Overall NIST posture rating

**PCI DSS v4.0:**
- Requirements met vs failing vs not applicable
- Per-requirement status with finding references
- SAQ eligibility impact notes

### Step 5: Report Generation

Produce the full compliance report in markdown. Use the Read tool to load templates from `references/report_templates.md`:

1. **Executive Summary**
   - Overall risk level (Critical/High/Medium/Low) based on highest severity finding and finding volume
   - Total findings count by severity
   - Top 3 most critical findings with brief descriptions
   - Per-framework compliance posture summary
   - Key recommendations (top 3-5 actions)

2. **Findings Table**
   - All findings in a table with columns: ID, Title, Severity, Source, OWASP, CWE, NIST, PCI DSS
   - Sorted by severity (Critical first)

3. **Framework-Specific Sections**
   - One section per framework with category/control details
   - Show which findings map to each category
   - Include pass/fail/not-tested status for each category

4. **Remediation Priority Matrix**
   - Score each finding on: severity, exploitability, compliance impact
   - Group into priority tiers: Immediate / Short-term / Medium-term / Long-term
   - Include effort estimates

5. **Gap Analysis**
   - What was not tested
   - Which framework categories have no coverage
   - Recommendations for additional testing

## Output Format

The report MUST be output as structured markdown directly in the conversation. Do not create files unless the user explicitly requests a file be written.

## Important Notes

- This skill does NOT scan code. It maps existing findings to frameworks.
- When no findings are provided, instruct the user to run security scanning skills first.
- Always cite the specific framework version (OWASP 2021, NIST Rev 5, PCI DSS v4.0).
- Be conservative in "pass" assessments -- if a category was not explicitly tested, mark it as "Not Tested" rather than "Pass".
- Multiple findings can map to the same framework category.
- A single finding can map to multiple frameworks and multiple categories within a framework.
