# NagrikSaarathi — Database ERD

> Entity-Relationship Diagram for the NagrikSaarathi database layer including Guided Self-Application mode.

```mermaid
erDiagram
    Language {
        int id PK
        string language_code UK
        string english_name
        string native_name
        string writing_system
        string direction "ltr | rtl"
        bool enabled
        bool supports_text
        bool supports_speech_recognition
        bool supports_text_to_speech
    }

    GovernmentScheme {
        int id PK
        string slug UK
        string display_name
        text description
        string department_name
        string official_source_url
        string source_document_reference "nullable"
        bool is_demo
        bool is_active
        string official_application_url "nullable"
        datetime last_verified_at "nullable"
        string verification_status "verified | pending_review | outdated"
        string verification_source_reference "nullable"
        json descriptions_by_language
        json application_instructions_by_language
        datetime created_at
        datetime updated_at
    }

    FormField {
        int id PK
        int scheme_id FK
        string field_key "unique per scheme"
        string field_type
        bool required
        int sort_order
        json labels_by_language
        json explanations_by_language
        json instructions_by_language
        json examples_by_language
        json validation_guidance_by_language
        json validation_rules
        string source_reference "nullable"
        string verification_status "verified | pending_review | outdated"
        datetime last_verified_at "nullable"
    }

    SchemeEligibilityRequirement {
        int id PK
        int scheme_id FK
        string criterion_key "unique per scheme"
        string criterion_type "age | income | academic | domicile | category..."
        string operator "lte | gte | eq | in | boolean"
        json threshold_value "structured rule thresholds"
        bool is_mandatory
        int sort_order
        json titles_by_language
        json descriptions_by_language
        string official_source_reference "nullable"
        string verification_status "verified | pending_review | outdated"
        datetime last_verified_at "nullable"
    }

    SchemeDocumentRequirement {
        int id PK
        int scheme_id FK
        string document_code "unique per scheme"
        string requirement_type "always_required | conditional | optional"
        json condition_rule "structured rule condition"
        bool is_mandatory
        int sort_order
        json titles_by_language
        json descriptions_by_language
        string issuing_authority "nullable"
        string validity_period_info "nullable"
        string official_source_url "nullable"
        string source_reference "nullable"
        string verification_status "verified | pending_review | outdated"
        datetime last_verified_at "nullable"
    }

    SchemeApplicationStep {
        int id PK
        int scheme_id FK
        int step_number "unique per scheme"
        string step_key
        json titles_by_language
        json instructions_by_language
        string official_action_url "nullable"
        string source_reference "nullable"
        string verification_status "verified | pending_review | outdated"
        datetime last_verified_at "nullable"
    }

    AssistedSession {
        string id PK "UUID"
        int scheme_id FK
        string selected_language
        string channel "web | assisted_desk"
        string status "in_progress | completed | abandoned | needs_human_help"
        bool analytics_consent
        bool is_demo
        datetime started_at
        datetime ended_at "nullable"
    }

    SessionEvent {
        int id PK
        string session_id FK
        string field_key "nullable"
        string event_type
        string barrier_category "nullable"
        string resolution_status "nullable"
        string language_code "nullable"
        datetime created_at
    }

    TranslationReview {
        int id PK
        string resource_type
        string resource_key
        string language_code
        string translation_status "draft | reviewed | approved"
        text reviewer_note "nullable"
        datetime updated_at
    }

    User {
        int id PK
        string identifier UK
        string email "nullable"
        string mobile "nullable"
        string hashed_password
        string role "citizen | official"
        string full_name "nullable"
        string department "nullable"
        bool is_active
        bool is_demo
        datetime created_at
        datetime last_login_at "nullable"
    }

    GovernmentScheme ||--o{ FormField : "has fields"
    GovernmentScheme ||--o{ SchemeEligibilityRequirement : "has eligibility criteria"
    GovernmentScheme ||--o{ SchemeDocumentRequirement : "has document requirements"
    GovernmentScheme ||--o{ SchemeApplicationStep : "has application steps"
    GovernmentScheme ||--o{ AssistedSession : "has sessions"
    AssistedSession ||--o{ SessionEvent : "has events"
```

## Privacy Guarantees

| Table | Privacy Guarantee |
|---|---|
| `assisted_sessions` | **Zero PII.** No form answers, documents, names, phones, addresses, or identity numbers. |
| `session_events` | **Structured events only.** Never stores actual values or documents entered by citizens. |
| Guided Self-Application | Fully operable without user registration; application answers remain in client-side memory. |
| All analytics | Created only after explicit `analytics_consent = true`. |
| Demo data | Always distinguished by `is_demo = true`. |
