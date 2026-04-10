from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.media_ingest.entities import CloudLink, CloudPlatform, CurationStatus, MediaResource, MediaType
from app.domain.media_ingest.repositories import MediaResourceRepository
from app.infrastructure.db.models import CloudLinkModel, MediaResourceModel


class SqlAlchemyMediaResourceRepository(MediaResourceRepository):
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, resource: MediaResource) -> MediaResource:
        model = MediaResourceModel(
            id=resource.id,
            canonical_title=resource.canonical_title,
            display_title=resource.display_title,
            media_type=resource.media_type.value,
            cover_url=resource.cover_url,
            scrape_profile=resource.scrape_profile,
            normalization_fingerprint=resource.normalization_fingerprint,
            curation_status=resource.curation_status.value,
            first_seen_at=resource.first_seen_at,
            last_seen_at=resource.last_seen_at,
            created_at=resource.created_at,
        )
        self.session.add(model)
        for link in resource.links:
            self.session.add(self._link_to_model(link))
        self.session.commit()
        loaded = self._load_model(resource.id)
        if loaded is None:
            raise ValueError("资源创建后加载失败。")
        return self._to_entity(loaded)

    def get_by_id(self, resource_id: UUID) -> MediaResource | None:
        model = self._load_model(resource_id)
        return self._to_entity(model) if model else None

    def get_by_fingerprint(self, fingerprint: str) -> MediaResource | None:
        stmt = (
            select(MediaResourceModel)
            .options(selectinload(MediaResourceModel.links))
            .where(MediaResourceModel.normalization_fingerprint == fingerprint)
        )
        model = self.session.scalar(stmt)
        return self._to_entity(model) if model else None

    def list_all(self) -> list[MediaResource]:
        stmt = select(MediaResourceModel).options(selectinload(MediaResourceModel.links)).order_by(MediaResourceModel.created_at)
        return [self._to_entity(model) for model in self.session.scalars(stmt)]

    def save(self, resource: MediaResource) -> MediaResource:
        model = self._load_model(resource.id)
        if model is None:
            raise ValueError("待保存的资源不存在。")

        model.canonical_title = resource.canonical_title
        model.display_title = resource.display_title
        model.media_type = resource.media_type.value
        model.cover_url = resource.cover_url
        model.scrape_profile = resource.scrape_profile
        model.normalization_fingerprint = resource.normalization_fingerprint
        model.curation_status = resource.curation_status.value
        model.first_seen_at = resource.first_seen_at
        model.last_seen_at = resource.last_seen_at

        existing_links = {link.id: link for link in model.links}
        for link in resource.links:
            link_model = existing_links.get(link.id)
            if link_model is None:
                self.session.add(self._link_to_model(link))
                continue
            link_model.platform = link.platform.value
            link_model.url = link.url
            link_model.extraction_code = link.extraction_code
            link_model.first_seen_at = link.first_seen_at
            link_model.last_seen_at = link.last_seen_at

        self.session.commit()
        loaded = self._load_model(resource.id)
        if loaded is None:
            raise ValueError("资源保存后加载失败。")
        return self._to_entity(loaded)

    def _load_model(self, resource_id: UUID) -> MediaResourceModel | None:
        stmt = (
            select(MediaResourceModel)
            .options(selectinload(MediaResourceModel.links))
            .where(MediaResourceModel.id == resource_id)
        )
        return self.session.scalar(stmt)

    @staticmethod
    def _link_to_model(link: CloudLink) -> CloudLinkModel:
        return CloudLinkModel(
            id=link.id,
            media_resource_id=link.media_resource_id,
            source_message_id=link.source_message_id,
            platform=link.platform.value,
            url=link.url,
            extraction_code=link.extraction_code,
            first_seen_at=link.first_seen_at,
            last_seen_at=link.last_seen_at,
        )

    @staticmethod
    def _to_entity(model: MediaResourceModel) -> MediaResource:
        return MediaResource(
            id=model.id,
            canonical_title=model.canonical_title,
            display_title=model.display_title,
            media_type=MediaType(model.media_type),
            cover_url=model.cover_url,
            scrape_profile=model.scrape_profile or {},
            normalization_fingerprint=model.normalization_fingerprint,
            curation_status=CurationStatus(model.curation_status),
            first_seen_at=model.first_seen_at,
            last_seen_at=model.last_seen_at,
            created_at=model.created_at,
            links=[
                CloudLink(
                    id=link.id,
                    media_resource_id=link.media_resource_id,
                    source_message_id=link.source_message_id,
                    platform=CloudPlatform(link.platform),
                    url=link.url,
                    extraction_code=link.extraction_code,
                    first_seen_at=link.first_seen_at,
                    last_seen_at=link.last_seen_at,
                )
                for link in model.links
            ],
            source_message_ids=[],
        )
