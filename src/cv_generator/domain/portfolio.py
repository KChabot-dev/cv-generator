from cv_generator.domain.common import DomainModel


class PortfolioDocument(DomainModel):
    source_id: str
    content: str


class PortfolioContext(DomainModel):
    documents: list[PortfolioDocument]