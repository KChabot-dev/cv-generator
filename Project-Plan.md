## Current Phase

Implementation — Pydantic domain models and validation.

### Completed

- Python project bootstrap with uv
- Python 3.13 project environment and dependency locking
- Pydantic runtime dependency
- pytest, Ruff, and mypy development tooling
- Project-level tooling configuration
- Initial domain package and unit-test structure
- `CandidateIdentity`
- reusable `PartialDate`
- `EducationStatus`
- `EducationRecord` with consistency validation
- `ExperienceRecord`
- reusable partial-date comparison logic

### Next

- Complete and test `ExperienceRecord`
- Implement the remaining `CandidateProfile` structures
- Assemble the top-level `CandidateProfile`
- Add serialization/schema tests