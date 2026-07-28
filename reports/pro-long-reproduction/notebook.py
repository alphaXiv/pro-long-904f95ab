# /// script
# requires-python = ">=3.12"
# dependencies = ["marimo>=0.14.0"]
# ///

import marimo

__generated_with = "0.23.15"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md(r"""
    # PRO-LONG reproduction: why the result is setup-blocked

    PRO-LONG gives a game-playing coding agent a complete structured history
    and lets it retrieve old evidence with grep and Python. This notebook
    explains the claim, the matched test, the Kubernetes evidence, and why
    no scientific comparison can be made from this attempt.

    **Verdict: not reproduced; both claims are unassessed.** The public
    ARC-AGI-3 credential was absent in every corrected job, so zero fresh
    episodes ran.
    """)
    return


@app.cell
def _():
    conditions = [
        {"condition": "Full log", "planned": 3, "executed": 0, "duration_s": 68},
        {"condition": "Last 25", "planned": 3, "executed": 0, "duration_s": 68},
        {"condition": "No log", "planned": 3, "executed": 0, "duration_s": 63},
        {"condition": "Stateless", "planned": 3, "executed": 0, "duration_s": 52},
    ]
    paper = {
        "full_log_pass_at_1": 41.2,
        "no_log_pass_at_1": 24.0,
        "tool_ladder": {"read": 23.1, "grep": 27.2, "python": 38.3, "write": 41.2},
        "workspace": {"full_persistent": 41.2, "full_stateless": 40.7,
                      "no_log_persistent": 24.0, "no_log_stateless": 19.9},
    }
    released = {
        "scorecards": 25,
        "trajectories": 25,
        "analyzer_logs": 25,
        "mean_official_score": 94.7115,
        "levels": 179,
        "actions": 11156,
        "grep_mentions": 481,
        "python_mentions": 3210,
        "log_mentions": 3271,
    }
    return conditions, paper, released


@app.cell
def _(conditions, mo):
    rows = "".join(
        f"| {x['condition']} | {x['planned']} | **{x['executed']}** | "
        f"{x['duration_s']}s |\n"
        for x in conditions
    )
    mo.md(
        f"""
        ## Primary evidence

        | Condition | Planned episodes | Fresh episodes executed | Job duration |
        |---|---:|---:|---:|
        {rows}

        Every terminal log names the same gate: `ARC_API_KEY not set`. The
        planned workload was `g50t`, `m0r0`, and `ls20`, 120 actions each,
        GPT-5.4 Codex, high reasoning, action cap 20, and three analyzer retries.
        """
    )
    return


@app.cell
def _(conditions, mo):
    selector = mo.ui.dropdown(
        options=[x["condition"] for x in conditions],
        value="Full log",
        label="Inspect a condition",
    )
    selector
    return (selector,)


@app.cell
def _(conditions, mo, selector):
    selected = next(x for x in conditions if x["condition"] == selector.value)
    mo.callout(
        mo.md(
            f"**{selected['condition']}** planned {selected['planned']} episodes, "
            f"executed **{selected['executed']}**, and completed its setup-gate "
            f"job in {selected['duration_s']} seconds."
        ),
        kind="warn",
    )
    return


@app.cell
def _(mo, paper):
    mo.md(
        f"""
        ## What would have been compared

        The paper reports **{paper['full_log_pass_at_1']}%** pass@1 for full-log
        GPT-5.5 and **{paper['no_log_pass_at_1']}%** for no-log. Its tool ladder
        is `{paper['tool_ladder']['read']} → {paper['tool_ladder']['grep']} →
        {paper['tool_ladder']['python']} → {paper['tool_ladder']['write']}%`
        as read, grep, Python, and write/edit are added.

        These are paper numbers, not observations from this attempt. Zero
        episodes means there is no denominator for score, levels, tokens,
        analyzer calls, or retrieval efficiency.
        """
    )
    return


@app.cell
def _(mo, released):
    mo.md(
        f"""
        ## Released-log audit: useful, but not a reproduction

        The pinned release contains {released['scorecards']} scorecards,
        {released['trajectories']} trajectories, and {released['analyzer_logs']}
        analyzer logs. Their official mean score is {released['mean_official_score']}
        across {released['levels']} levels and {released['actions']:,} actions.
        Analyzer text includes {released['grep_mentions']} grep/regex,
        {released['python_mentions']:,} Python, and {released['log_mentions']:,}
        `logs.txt` mentions.

        This confirms artifact completeness and visible programmatic retrieval.
        It cannot test matched controls or token efficiency because it reuses
        author trajectories.
        """
    )
    return


@app.cell
def _(mo):
    mo.md("""
    ## Compute and the executable next step

    OpenResearch Kubernetes was used on an NVIDIA RTX PRO 6000 Blackwell
    cluster. The workload is API-driven, so peak GPU allocation was 0;
    four CPU jobs ran concurrently. Queue-verified campaign wall time was
    223.362 seconds (0.062045 hours). The publication schema rejects zero, so
    `autoresearch.json` records its minimum valid `gpuCount` of 1; the run
    manifests and terminal logs remain the source of truth for allocation.

    The runtime is ready: Python 3.12.13, Node 22.17.1, and Codex CLI
    0.145.0 were printed in the successful logs, and OpenAI credentials were
    present. Adding `ARC_API_KEY` to the Kubernetes environment activates
    the four committed conditions without changing their fixed run command.
    """)
    return


if __name__ == "__main__":
    app.run()
