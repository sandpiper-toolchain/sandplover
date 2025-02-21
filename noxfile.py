from __future__ import annotations

import os

import nox

ROOT = os.path.dirname(os.path.abspath(__file__))


@nox.session
def build(session: nox.Session) -> None:
    """Build sdist and wheel dists."""
    outdir = os.path.join(ROOT, "dist")
    session.install("build")
    session.run("python", "-m", "build", "--outdir", outdir)
    session.log(f"Built distributions can be found in {outdir}")
    return outdir


@nox.session
def install(session: nox.Session) -> None:
    """install the package"""
    arg = session.posargs[0] if session.posargs else build(session)

    session.install("-r", "requirements.txt")

    if os.path.isdir(arg):
        session.install("sandplover", f"--find-links={arg}", "--no-deps", "--no-index")
    elif os.path.isfile(arg):
        session.install(arg, "--no-deps")
    else:
        session.error("first argument must be either a wheel or a wheelhouse folder")


@nox.session
def test(session: nox.Session) -> None:
    """Run the tests."""
    session.install("pytest", "requirements.txt")
    install(session)

    session.run("pytest", "-vvv")


@nox.session
def coverage(session: nox.Session) -> None:
    """Run coverage"""
    session.install("coverage", "pytest", "-r", "requirements.txt")
    install(session)

    session.run(
        "coverage", "run", "-m", "pytest", "-vvv", env={"COVERAGE_CORE": "sysmon"}
    )

    if "CI" in os.environ:
        session.run("coverage", "xml", "-o", os.path.join(ROOT, "coverage.xml"))
    else:
        session.run("coverage", "report", "--ignore-errors", "--show-missing")


@nox.session
def lint(session: nox.Session) -> None:
    """Look for lint."""
    skip_hooks = ("file-contents-sorter",)
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files", env={"SKIP": ",".join(skip_hooks)})


@nox.session
def docs(session: nox.Session) -> None:
    """Build the docs."""
    session.install("-r", "requirements-docs.txt")
    install(session)

    os.makedirs("docs/build", exist_ok=True)
    session.run(
        "sphinx-build",
        *("-b", "html"),
        "-W",
        "--keep-going",
        "docs/source",
        "docs/build/html",
    )
    session.log("generated docs at build/html")
