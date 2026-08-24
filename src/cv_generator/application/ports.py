from typing import Protocol

from cv_generator.domain.candidate import CandidateProfile
from cv_generator.domain.draft import CVDraft
from cv_generator.domain.evidence import EvidenceMap
from cv_generator.domain.job import JobSpec
from cv_generator.domain.planning import CVContentPlan
from cv_generator.domain.portfolio import PortfolioContext


class JobAnalyzer(Protocol):
    def analyze(self, job_text: str) -> JobSpec:
        ...

class EvidenceMatcher(Protocol):
    def match(
        self,
        job_spec: JobSpec,
        portfolio_context: PortfolioContext,
    ) -> EvidenceMap:
        ...

class CVPlanner(Protocol):
    def plan(
        self,
        candidate_profile: CandidateProfile,
        job_spec: JobSpec,
        evidence_map: EvidenceMap,
    ) -> CVContentPlan:
        ...

class CVWriter(Protocol):
    def write(
        self,
        candidate_profile: CandidateProfile,
        evidence_map: EvidenceMap,
        content_plan: CVContentPlan,
    ) -> CVDraft:
        ...