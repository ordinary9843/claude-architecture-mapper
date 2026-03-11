import os
import sys
import glob
from anthropic import Anthropic

def get_auditor_prompt():
    return (
        "You are an expert Claude Code plugin auditor specializing in architecture mapping plugins. "
        "You evaluate skill files, reference rules, examples, and CLAUDE.md against official Anthropic "
        "best practices. Score each artifact A–F and produce a concise, actionable report."
    )

def get_rubric_content():
    rubrics = []
    ref_dir = os.path.join(os.path.dirname(__file__), "..", "skills", "map", "references")
    if not os.path.exists(ref_dir):
        return ""

    for md_file in glob.glob(os.path.join(ref_dir, "*.md")):
        with open(md_file, "r") as f:
            rubrics.append(f"--- REFERENCE: {os.path.basename(md_file)} ---\n{f.read()}\n")
    return "\n".join(rubrics)

def gather_artifacts():
    patterns = [
        "skills/**/SKILL.md",
        "skills/**/references/*.md",
        "skills/**/examples/*.md",
        "CLAUDE.md",
        "CLAUDE.local.md"
    ]

    files = []
    for pattern in patterns:
        files.extend(glob.glob(pattern, recursive=True))

    content = ""
    for f_path in sorted(set(files)):
        if os.path.isfile(f_path):
            with open(f_path, "r") as f:
                content += f"\n--- FILE: {f_path} ---\n{f.read()}\n"
    return content

def run_audit():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY not found. Skipping audit.")
        sys.exit(0)

    artifacts = gather_artifacts()
    if not artifacts.strip():
        print("No Claude Architecture Mapper artifacts found to audit.")
        sys.exit(0)

    client = Anthropic(api_key=api_key)

    system_prompt = get_auditor_prompt()
    rubrics = get_rubric_content()

    prompt = f"""
Audit the following Claude Architecture Mapper plugin artifacts.
Use these reference rules as your evaluation criteria:
<references>
{rubrics}
</references>

Here are the artifact files from the repository:
<artifacts>
{artifacts}
</artifacts>

Produce ONLY a markdown audit report with an A–F grade per file and an overall grade. No conversational preamble.
"""

    print("Running Architecture Mapper Audit via Anthropic API...")

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4000,
        system=system_prompt,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    report = response.content[0].text

    with open("audit_report.md", "w") as f:
        f.write(report)

    print(report)

    if "Grade F" in report or "Grade: F" in report:
        print("\nAudit failed with Grade F. Please fix the top issues before merging.")
        sys.exit(1)

if __name__ == "__main__":
    run_audit()
