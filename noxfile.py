from __future__ import annotations

import os

import nox


ROOT = os.path.dirname(os.path.abspath(__file__))


@nox.session
def build(session: nox.Session) -> None:
    """Build sdist and wheel dists."""
    session.install("pip", "build")
    session.install("setuptools")
    session.run("python", "--version")
    session.run("pip", "--version")
    session.run("python", "-m", "build")


@nox.session
def install(session: nox.Session) -> None:
    """install the package"""
    first_arg = session.posargs[0] if session.posargs else None

    if first_arg and not os.path.isfile(first_arg):
        session.error("path must be a source distribution file")
    session.install(first_arg or ".")


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
    session.install("pre-commit")
    session.run("pre-commit", "run", "--all-files")


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
