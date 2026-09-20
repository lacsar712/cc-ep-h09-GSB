import hashlib

import pytest
from pydantic import ValidationError

from app.cqrs import DomainError, start_run
from app.schemas import StartRunCommand


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


def test_start_run_rejects_empty_dataset_sha(db):
    with pytest.raises(DomainError):
        start_run(
            db,
            actor="researcher",
            project="p1",
            name="n1",
            dataset_content_sha256="",
            code_commit_sha="abc1234",
            description=None,
        )


def test_start_run_rejects_empty_code_commit_sha(db):
    with pytest.raises(DomainError):
        start_run(
            db,
            actor="researcher",
            project="p1",
            name="n1",
            dataset_content_sha256=sha("ds"),
            code_commit_sha="",
            description=None,
        )


def test_start_run_rejects_invalid_dataset_sha(db):
    for bad in ["abc123", "z" * 64, "a" * 63, "a" * 65]:
        with pytest.raises(DomainError):
            start_run(
                db,
                actor="researcher",
                project="p1",
                name="n1",
                dataset_content_sha256=bad,
                code_commit_sha="abc1234",
                description=None,
            )


def test_start_run_rejects_invalid_code_commit_sha(db):
    for bad in ["abc12", "g" * 40, "a" * 41, "not-a-sha"]:
        with pytest.raises(DomainError):
            start_run(
                db,
                actor="researcher",
                project="p1",
                name="n1",
                dataset_content_sha256=sha("ds"),
                code_commit_sha=bad,
                description=None,
            )


def test_start_run_valid_creation(db):
    dataset_sha = sha("ds-valid")
    run = start_run(
        db,
        actor="researcher",
        project="p1",
        name="n1",
        dataset_content_sha256=dataset_sha.upper(),
        code_commit_sha="A1B2C3D4E5F6789012345678ABCDEF0123456789",
        description="d",
    )
    assert run.status == "running"
    assert run.version == 1
    # normalized to lowercase
    assert run.dataset_content_sha256 == dataset_sha
    assert run.code_commit_sha == "a1b2c3d4e5f6789012345678abcdef0123456789"


def test_schema_rejects_empty_dataset_sha():
    with pytest.raises(ValidationError):
        StartRunCommand(
            project="p1",
            name="n1",
            dataset_content_sha256="",
            code_commit_sha="abc1234",
        )


def test_schema_rejects_empty_code_commit_sha():
    with pytest.raises(ValidationError):
        StartRunCommand(
            project="p1",
            name="n1",
            dataset_content_sha256=sha("ds"),
            code_commit_sha="",
        )


def test_schema_rejects_omitted_fingerprints():
    with pytest.raises(ValidationError):
        StartRunCommand(project="p1", name="n1")


def test_schema_accepts_valid_fingerprints():
    cmd = StartRunCommand(
        project="p1",
        name="n1",
        dataset_content_sha256=sha("ds"),
        code_commit_sha="abc1234",
    )
    assert len(cmd.dataset_content_sha256) == 64
    assert cmd.code_commit_sha == "abc1234"
