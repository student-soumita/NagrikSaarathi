"""
Analytics and Metric Aggregation Service for NagrikSaarathi.

Strict Metric Definitions:
- Only counts sessions with explicit citizen consent (analytics_consent = True).
- Segregates simulated demo records from real production observations.
- Explicit numerators and denominators for all percentages and rates.
- Never stores or processes citizen personal information.
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models import (
    AssistedSession,
    FormField,
    GovernmentScheme,
    Language,
    SessionEvent,
    TranslationReview,
)
from backend.app.schemas.dashboard import (
    BarrierItem,
    BarrierMetricsResponse,
    FieldMetricItem,
    FieldMetricsResponse,
    LanguageMetricItem,
    LanguageMetricsResponse,
    RecoveryMetricsResponse,
    SummaryMetricsResponse,
    TranslationLanguageStatus,
    TranslationQualityResponse,
)


class AnalyticsService:
    @staticmethod
    def _apply_session_filters(
        query,
        include_demo: bool,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ):
        """Filter sessions by consent, demo flag, and optional date range."""
        query = query.where(AssistedSession.analytics_consent == True)  # noqa: E712
        if not include_demo:
            query = query.where(AssistedSession.is_demo == False)  # noqa: E712
        else:
            query = query.where(AssistedSession.is_demo == True)  # noqa: E712

        if start_date:
            query = query.where(AssistedSession.started_at >= start_date)
        if end_date:
            query = query.where(AssistedSession.started_at <= end_date)
        return query

    @classmethod
    def get_summary(
        cls,
        db: Session,
        include_demo: bool = True,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> SummaryMetricsResponse:
        """Calculate overall session status volume and completion/abandonment rates."""
        base_q = select(AssistedSession.status)
        filtered_q = cls._apply_session_filters(base_q, include_demo, start_date, end_date)
        statuses = db.execute(filtered_q).scalars().all()

        total = len(statuses)
        completed = statuses.count("completed")
        abandoned = statuses.count("abandoned")
        needs_help = statuses.count("needs_human_help")

        completion_rate = round((completed / total) * 100, 2) if total > 0 else 0.0
        abandonment_rate = round((abandoned / total) * 100, 2) if total > 0 else 0.0

        return SummaryMetricsResponse(
            total_consented_sessions=total,
            completed_sessions=completed,
            abandoned_sessions=abandoned,
            needs_human_help_sessions=needs_help,
            completion_rate_pct=completion_rate,
            abandonment_rate_pct=abandonment_rate,
            is_demo_data=include_demo,
            data_source_note=(
                "SIMULATED TEST DATA: This reflects synthetic test sessions."
                if include_demo
                else "REAL DATA: Aggregated observed barriers from consented citizen sessions."
            ),
        )

    @classmethod
    def get_barriers(
        cls,
        db: Session,
        include_demo: bool = True,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> BarrierMetricsResponse:
        """Aggregate barrier categories encountered across consented sessions."""
        query = (
            select(
                SessionEvent.barrier_category,
                func.count(SessionEvent.id).label("count"),
            )
            .join(AssistedSession, SessionEvent.session_id == AssistedSession.id)
            .where(SessionEvent.barrier_category.isnot(None))
        )
        query = cls._apply_session_filters(query, include_demo, start_date, end_date)
        query = query.group_by(SessionEvent.barrier_category).order_by(func.count(SessionEvent.id).desc())

        rows = db.execute(query).all()
        total_barriers = sum(r[1] for r in rows)

        items = [
            BarrierItem(
                barrier_category=cat,
                count=cnt,
                percentage_of_barriers=round((cnt / total_barriers) * 100, 2) if total_barriers > 0 else 0.0,
            )
            for cat, cnt in rows
        ]

        return BarrierMetricsResponse(
            total_barrier_events=total_barriers,
            items=items,
            is_demo_data=include_demo,
            data_source_note="Calculated strictly over events where a barrier was identified.",
        )

    @classmethod
    def get_language_metrics(
        cls,
        db: Session,
        include_demo: bool = True,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> LanguageMetricsResponse:
        """Break down session volume and barrier frequencies by language."""
        # Session counts by language
        sess_q = select(
            AssistedSession.selected_language,
            func.count(AssistedSession.id).label("sess_count"),
        )
        sess_q = cls._apply_session_filters(sess_q, include_demo, start_date, end_date)
        sess_q = sess_q.group_by(AssistedSession.selected_language)
        sess_counts = dict(db.execute(sess_q).all())

        # Event counts with barriers by language
        event_q = (
            select(
                SessionEvent.language_code,
                func.count(SessionEvent.id),
            )
            .join(AssistedSession, SessionEvent.session_id == AssistedSession.id)
            .where(SessionEvent.barrier_category.isnot(None))
        )
        event_q = cls._apply_session_filters(event_q, include_demo, start_date, end_date)
        event_q = event_q.group_by(SessionEvent.language_code)
        event_counts = dict(db.execute(event_q).all())

        # Fetch all languages for native names
        langs = db.execute(select(Language)).scalars().all()
        items: List[LanguageMetricItem] = []

        for lang in langs:
            s_cnt = sess_counts.get(lang.language_code, 0)
            e_cnt = event_counts.get(lang.language_code, 0)
            if s_cnt > 0 or e_cnt > 0:
                items.append(
                    LanguageMetricItem(
                        language_code=lang.language_code,
                        language_name=lang.english_name,
                        native_name=lang.native_name,
                        session_count=s_cnt,
                        barrier_event_count=e_cnt,
                    )
                )

        items.sort(key=lambda x: x.session_count, reverse=True)
        return LanguageMetricsResponse(
            total_languages_represented=len(items),
            items=items,
            is_demo_data=include_demo,
        )

    @classmethod
    def get_field_metrics(
        cls,
        db: Session,
        include_demo: bool = True,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> FieldMetricsResponse:
        """Find the most frequently affected form fields and their specific barriers."""
        query = (
            select(
                SessionEvent.field_key,
                AssistedSession.scheme_id,
                GovernmentScheme.display_name,
                SessionEvent.barrier_category,
                func.count(SessionEvent.id),
            )
            .join(AssistedSession, SessionEvent.session_id == AssistedSession.id)
            .join(GovernmentScheme, AssistedSession.scheme_id == GovernmentScheme.id)
            .where(SessionEvent.field_key.isnot(None))
        )
        query = cls._apply_session_filters(query, include_demo, start_date, end_date)
        query = query.group_by(
            SessionEvent.field_key,
            AssistedSession.scheme_id,
            GovernmentScheme.display_name,
            SessionEvent.barrier_category,
        )

        rows = db.execute(query).all()

        fields_map: Dict[str, Dict] = {}
        for f_key, sch_id, sch_name, bar_cat, count in rows:
            if f_key not in fields_map:
                fields_map[f_key] = {
                    "field_key": f_key,
                    "scheme_id": sch_id,
                    "scheme_name": sch_name,
                    "issue_count": 0,
                    "barrier_breakdown": {},
                }
            fields_map[f_key]["issue_count"] += count
            if bar_cat:
                fields_map[f_key]["barrier_breakdown"][bar_cat] = count

        items = [
            FieldMetricItem(
                field_key=v["field_key"],
                scheme_id=v["scheme_id"],
                scheme_name=v["scheme_name"],
                issue_count=v["issue_count"],
                barrier_breakdown=v["barrier_breakdown"],
            )
            for v in fields_map.values()
        ]
        items.sort(key=lambda x: x.issue_count, reverse=True)

        return FieldMetricsResponse(
            total_problematic_fields=len(items),
            items=items,
            is_demo_data=include_demo,
        )

    @classmethod
    def get_recovery_metrics(
        cls,
        db: Session,
        include_demo: bool = True,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> RecoveryMetricsResponse:
        """Calculate resolution rate after guidance is provided."""
        query = (
            select(
                SessionEvent.resolution_status,
                func.count(SessionEvent.id),
            )
            .join(AssistedSession, SessionEvent.session_id == AssistedSession.id)
            .where(SessionEvent.resolution_status.isnot(None))
        )
        query = cls._apply_session_filters(query, include_demo, start_date, end_date)
        query = query.group_by(SessionEvent.resolution_status)

        status_counts = dict(db.execute(query).all())
        resolved = status_counts.get("resolved", 0)
        unresolved = status_counts.get("unresolved", 0)
        escalated = status_counts.get("escalated", 0)
        total_attempts = resolved + unresolved + escalated

        rate = round((resolved / total_attempts) * 100, 2) if total_attempts > 0 else 0.0

        return RecoveryMetricsResponse(
            total_resolution_attempts=total_attempts,
            resolved_count=resolved,
            unresolved_count=unresolved,
            escalated_count=escalated,
            resolution_rate_pct=rate,
            is_demo_data=include_demo,
            data_source_note="Denominator is eligible resolution attempts where a resolution outcome was recorded.",
        )

    @classmethod
    def get_translation_quality(cls, db: Session) -> TranslationQualityResponse:
        """Audit translation coverage and human-review status across all 22 languages."""
        languages = db.execute(select(Language)).scalars().all()
        fields = db.execute(select(FormField)).scalars().all()
        reviews = db.execute(select(TranslationReview)).scalars().all()

        # Map (resource_key, language_code) -> status
        review_map = {
            (r.resource_key, r.language_code): r.translation_status
            for r in reviews
            if r.resource_type == "form_field"
        }

        total_fields = len(fields)
        lang_statuses: List[TranslationLanguageStatus] = []

        overall_app = 0
        overall_rev = 0
        overall_drf = 0
        overall_mis = 0

        for lang in languages:
            app_cnt = 0
            rev_cnt = 0
            drf_cnt = 0
            mis_cnt = 0

            for f in fields:
                has_label = lang.language_code in f.labels_by_language
                st = review_map.get((f.field_key, lang.language_code))

                if not has_label:
                    mis_cnt += 1
                elif st == "approved":
                    app_cnt += 1
                elif st == "reviewed":
                    rev_cnt += 1
                else:
                    drf_cnt += 1

            cov = round(((app_cnt + rev_cnt + drf_cnt) / total_fields) * 100, 2) if total_fields > 0 else 0.0

            overall_app += app_cnt
            overall_rev += rev_cnt
            overall_drf += drf_cnt
            overall_mis += mis_cnt

            lang_statuses.append(
                TranslationLanguageStatus(
                    language_code=lang.language_code,
                    native_name=lang.native_name,
                    approved_count=app_cnt,
                    reviewed_count=rev_cnt,
                    draft_count=drf_cnt,
                    missing_count=mis_cnt,
                    coverage_pct=cov,
                )
            )

        return TranslationQualityResponse(
            total_configured_languages=len(languages),
            total_registered_fields=total_fields,
            overall_approved_count=overall_app,
            overall_reviewed_count=overall_rev,
            overall_draft_count=overall_drf,
            overall_missing_count=overall_mis,
            languages=lang_statuses,
            summary_note=(
                "Distinguishes approved and reviewed native-speaker translations "
                "from draft or unverified machine translations."
            ),
        )
