from __future__ import annotations

import html

import streamlit as st

from config.settings import APP_BRAND_NAME, APP_LOGO_PATH, APP_TAGLINE

LANDING_NAV_KEY = "ail_landing_nav"


def _img(url: str, alt: str) -> str:
    return (
        f'<img src="{html.escape(url)}" alt="{html.escape(alt)}" '
        'loading="lazy" decoding="async" />'
    )


IMG_HERO_CLINICAL = (
    "https://images.unsplash.com/photo-1576091160550-2173dba999ef"
    "?auto=format&fit=crop&w=960&q=82"
)
IMG_LITERATURE = (
    "https://images.unsplash.com/photo-1481627834876-b7833e8f5570"
    "?auto=format&fit=crop&w=800&q=82"
)
IMG_RESEARCH_LAB = (
    "https://images.unsplash.com/photo-1555949963-aa79dcee981c"
    "?auto=format&fit=crop&w=800&q=82"
)
IMG_DATA_INSIGHTS = (
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71"
    "?auto=format&fit=crop&w=800&q=82"
)
IMG_EDUCATION = (
    "https://images.unsplash.com/photo-1523240795612-9a054b0db644"
    "?auto=format&fit=crop&w=800&q=82"
)


def split_hero_html(*, lead: str, pills: tuple[str, ...] | None = None) -> str:
    title = html.escape(APP_BRAND_NAME)
    tag = html.escape(APP_TAGLINE)
    lead_e = html.escape(lead)
    pills_html = ""
    if pills:
        parts = "".join(
            f'<span class="ail-landing-pill">{html.escape(p)}</span>' for p in pills
        )
        pills_html = f'<div class="ail-landing-pills">{parts}</div>'
    return (
        '<div class="ail-shell ail-landing-wrap">'
        '<div class="ail-landing-hero-split">'
        '<div class="ail-hero-split-text">'
        f"<h1>{title}</h1>"
        f'<p class="ail-landing-hero-tag">{tag}</p>'
        f'<p class="ail-landing-lead">{lead_e}</p>'
        f"{pills_html}"
        "</div>"
        '<div class="ail-hero-split-visual">'
        f'{_img(IMG_HERO_CLINICAL, "Healthcare professional in clinical environment")}'
        "</div></div></div>"
    )


def hero_metrics_strip_html() -> str:
    """Short credibility strip for the marketing overview."""
    return (
        '<div class="ail-shell ail-landing-wrap">'
        '<div class="ail-landing-metrics">'
        '<div class="ail-landing-metric">'
        '<span class="ail-landing-metric-value">10k+</span>'
        '<span class="ail-landing-metric-label">abstracts per indexed run</span>'
        "</div>"
        '<div class="ail-landing-metric">'
        '<span class="ail-landing-metric-value">30</span>'
        '<span class="ail-landing-metric-label">LDA topics (tunable)</span>'
        "</div>"
        '<div class="ail-landing-metric">'
        '<span class="ail-landing-metric-value">Live</span>'
        '<span class="ail-landing-metric-label">PubMed · Chroma · NLP pipeline</span>'
        "</div>"
        '<div class="ail-landing-metric">'
        '<span class="ail-landing-metric-value">Evidence-first</span>'
        '<span class="ail-landing-metric-label">traceable sources · transparent analytics</span>'
        "</div>"
        "</div></div>"
    )


def photo_story_section_html() -> str:
    tiles = [
        (
            IMG_LITERATURE,
            "Corpus intelligence",
            "Surface themes, venues, and time across large MEDLINE slices—built for evidence literacy, "
            "with charts you can interrogate and sources you can open.",
        ),
        (
            IMG_RESEARCH_LAB,
            "Text pipeline",
            "Tokenize and score the corpus; similarity and topic views are exploratory maps—not citations.",
        ),
        (
            IMG_DATA_INSIGHTS,
            "Charts",
            "Year, journal, keyword, and co-citation plots for seminar discussion—always alongside the papers.",
        ),
    ]
    cells = []
    for url, heading, body in tiles:
        cells.append(
            '<figure class="ail-photo-tile">'
            f"{_img(url, heading)}"
            "<figcaption>"
            f"<strong>{html.escape(heading)}</strong>"
            f"<span>{html.escape(body)}</span>"
            "</figcaption></figure>"
        )
    return (
        '<div class="ail-shell ail-landing-wrap">'
        '<p class="ail-landing-section-kicker">Overview</p>'
        '<h2 class="ail-landing-section-head">What the app delivers</h2>'
        f'<div class="ail-landing-photo-row">{"".join(cells)}</div>'
        "</div>"
    )


def platform_principles_ribbon_html() -> str:
    """
    Replaces the old two-column + photo band. Single full-width ribbon: no stock imagery,
    aligned with the hero gradient for a more deliberate, product-like feel.
    """
    cols = [
        (
            "Source-grounded analysis",
            "Every chart and similarity view is computed from the documents you import into this "
            "workspace—abstracts, uploads, and the shared index you control—not from the open web.",
        ),
        (
            "Responsible data access",
            "PubMed retrieval is built around NCBI E-utilities etiquette: identify yourself with a contact email, "
            "batch politely, and treat this as teaching and research support—not a library substitute.",
        ),
        (
            "Role-aware by design",
            "Administrative, instruction, and learner surfaces are separated on purpose, so data loading, shared "
            "indices, and practice files stay in the right hands without extra policy prose on the home page.",
        ),
    ]
    col_html = ""
    for title, body in cols:
        col_html += (
            '<div class="ail-landing-ribbon-col">'
            f'<h3 class="ail-landing-ribbon-h3">{html.escape(title)}</h3>'
            f'<p class="ail-landing-ribbon-p">{html.escape(body)}</p>'
            "</div>"
        )
    return (
        '<div class="ail-shell ail-landing-wrap">'
        '<div class="ail-landing-principles-ribbon">'
        '<p class="ail-landing-ribbon-kicker">Platform principles</p>'
        '<h2 class="ail-landing-ribbon-title">Built so cohorts can trust what is on screen</h2>'
        f'<div class="ail-landing-ribbon-grid">{col_html}</div>'
        '<p class="ail-landing-ribbon-foot">MedCorpus Insight supports literacy and discussion; it does not issue '
        "clinical guidance, replace full-text licenses, or bypass your institution’s policies.</p>"
        "</div></div>"
    )


def sign_in_prompt_html() -> str:
    return (
        '<div class="ail-shell ail-landing-wrap">'
        '<p class="ail-landing-closing">Sign in below to open your workspace and literature tools.</p>'
        "</div>"
    )


def register_context_html() -> str:
    return (
        '<div class="ail-shell ail-landing-wrap">'
        '<div class="ail-landing-register-context">'
        '<div class="ail-reg-context-visual">'
        f'{_img(IMG_EDUCATION, "Students and educators")}'
        "</div>"
        "<div>"
        "<h3>Registering</h3>"
        "<p>New signups sit <strong>inactive</strong> until an admin flips role and supervisor. "
        "No mail from this app.</p>"
        '<ul class="ail-reg-list">'
        "<li>Pick a username your school will recognize.</li>"
        "<li>Password is hashed in SQLite on this machine.</li>"
        "<li>Ping your admin if you are stuck waiting.</li>"
        "</ul>"
        "</div></div></div>"
    )


def bootstrap_context_html() -> str:
    return (
        '<div class="ail-shell ail-landing-wrap">'
        '<div class="ail-landing-band ail-landing-band--compact">'
        "<h3>First admin</h3>"
        "<p>Empty DB: whoever you create here owns user CRUD and instructor assignments. "
        "Lose the password and you are fixing SQLite by hand.</p>"
        "</div></div>"
    )


def subpage_html(nav: str) -> str:
    if nav == "fields":
        return _fields_page_html()
    if nav == "services":
        return _services_page_html()
    if nav == "contact":
        return _contact_page_html()
    if nav == "about":
        return _about_page_html()
    return ""


def _fields_page_html() -> str:
    blocks = [
        (
            "Clinical & biomedical NLP",
            "Scientific abstracts use domain-specific vocabulary, acronyms, and citation patterns. The stack favors "
            "interpretable signals—token statistics, controlled keyword extraction, and topic models—over opaque "
            "scores so instructors can explain what each view is measuring.",
        ),
        (
            "Health-AI literacy & safety framing",
            "Designed for seminars that connect machine learning in medicine to evidence quality: limitations of "
            "retrieval, dataset shift, fairness, and when automation is inappropriate. Visualizations are framed as "
            "discussion aids, not clinical decision support.",
        ),
        (
            "Corpus-scale literature review",
            "When cohorts need a shared picture of a subdomain—venues, publication years, keyword drift, and "
            "co-citation structure—aggregates update as new rows are ingested. Every chart ties back to rows you "
            "can inspect in the workspace.",
        ),
        (
            "Health informatics pedagogy",
            "Students practice loading data, validating minimum corpus size, and interpreting LDA and similarity "
            "layouts as exploratory—not confirmatory—tools. Role separation keeps PubMed access and shared indexing "
            "under instructor or admin control.",
        ),
    ]
    cards = "".join(
        '<div class="ail-landing-feature-card ail-subpage-card">'
        f"<strong>{html.escape(t)}</strong>"
        f"<p>{html.escape(b)}</p>"
        "</div>"
        for t, b in blocks
    )
    outcomes = (
        "<h3 class=\"ail-subpage-h3\">Typical instructional outcomes</h3>"
        "<ul class=\"ail-reg-list ail-subpage-list\">"
        "<li>Learners articulate what an embedding similarity map does and does not prove about two papers.</li>"
        "<li>Cohorts compare keyword trends across years and relate them to known shifts in a subfield.</li>"
        "<li>Students practice responsible PubMed querying with email identification and batch limits.</li>"
        "<li>Discussions explicitly separate exploratory NLP output from peer-reviewed conclusions.</li>"
        "</ul>"
    )
    return (
        '<div class="ail-shell ail-landing-wrap ail-subpage-root">'
        '<p class="ail-landing-section-kicker">Fields</p>'
        '<h2 class="ail-landing-section-head">Domains this platform is built around</h2>'
        '<p class="ail-subpage-lead">MedCorpus Insight is strongest where programs need a <strong>repeatable, '
        "source-grounded</strong> workflow: structured literature, transparent NLP, and role-aware access—not "
        "consumer-style chat over the open web.</p>"
        f'<div class="ail-landing-features">{cards}</div>'
        '<div class="ail-landing-band ail-landing-band--compact ail-subpage-band">'
        f"{outcomes}"
        "</div>"
        "</div>"
    )


def _services_page_html() -> str:
    ingest = [
        (
            "PubMed (E-utilities)",
            "Batch retrieval with ranked PMIDs, optional caps, and a required contact channel for NCBI policy. "
            "Results land in a session or can be written to the shared Chroma collection by authorized roles.",
        ),
        (
            "CSV & JSON ingest",
            "Column-oriented templates for title, abstract, metadata, and identifiers. Validates minimum row counts "
            "before expensive NLP so failed runs fail fast with clear messages.",
        ),
        (
            "ChromaDB persistence",
            "Embeddings and document metadata live in a local persistent store you operate. Instructors refresh "
            "analytics against the full collection; students can query the class index read-only.",
        ),
    ]
    analytics = [
        (
            "Lexical & topical views",
            "Top keywords, per-year keyword profiles, and LDA-backed topic summaries with coherence-oriented defaults "
            "for biomedical text.",
        ),
        (
            "Corpus structure",
            "Journal and year distributions, co-citation sketches, and similarity tables intended for classroom "
            "critique—not automated literature decisions.",
        ),
        (
            "Grounded Q&A",
            "Question answering is constrained to documents currently loaded in the active workspace so answers "
            "remain inspectable and attributable.",
        ),
    ]
    admin = [
        (
            "Accounts & roles",
            "SQLite-backed users with admin, instructor, and student roles. Registration can require manual "
            "activation so cohort membership stays under institutional control.",
        ),
        (
            "Activity awareness",
            "Lightweight event logging for PubMed pulls, uploads, and refresh operations—useful for auditing "
            "teaching use without third-party telemetry.",
        ),
    ]

    def _group(title: str, pairs: list[tuple[str, str]]) -> str:
        cards = "".join(
            '<div class="ail-landing-feature-card ail-subpage-card">'
            f"<strong>{html.escape(a)}</strong><p>{html.escape(b)}</p></div>"
            for a, b in pairs
        )
        return (
            f'<h3 class="ail-subpage-h3">{html.escape(title)}</h3>'
            f'<div class="ail-landing-features ail-subpage-service-grid">{cards}</div>'
        )

    body = _group("Ingest & storage", ingest) + _group("Analytics & exploration", analytics) + _group(
        "Administration & governance", admin
    )
    return (
        '<div class="ail-shell ail-landing-wrap ail-subpage-root">'
        '<p class="ail-landing-section-kicker">Services</p>'
        '<h2 class="ail-landing-section-head">End-to-end capabilities</h2>'
        '<p class="ail-subpage-lead">Everything below ships in the same application your learners already open in '
        "the browser—no separate notebook cluster required for the core teaching loop.</p>"
        f'<div class="ail-subpage-services-wrap">{body}</div>'
        '<div class="ail-landing-band ail-subpage-note">'
        "<p><strong>Scope note.</strong> Licensing for full-text PDFs, institutional subscriptions, and IRB-covered "
        "human-subjects data remain outside this tool. MedCorpus Insight focuses on metadata-rich abstracts and "
        "tabular uploads you are entitled to use.</p>"
        "</div></div>"
    )


def _contact_page_html() -> str:
    return (
        '<div class="ail-shell ail-landing-wrap ail-subpage-root">'
        '<p class="ail-landing-section-kicker">Contact</p>'
        '<h2 class="ail-landing-section-head">How your organization should engage</h2>'
        "<p class=\"ail-subpage-lead\">This deployment does not expose a product helpdesk or outbound email queue. "
        "Routing questions through your existing academic and IT channels keeps responsibilities clear.</p>"
        '<div class="ail-landing-band-grid">'
        "<div>"
        "<h3>Program administration</h3>"
        "<p>For <strong>account activation</strong>, role changes, instructor assignment, or syllabus alignment, "
        "contact the administrator who owns this instance. They control SQLite user records and can explain local "
        "policy (guest mode, password rules, retention).</p>"
        "</div>"
        "<div>"
        "<h3>Teaching staff</h3>"
        "<p>For <strong>class logistics</strong>—which corpus to study, how uploads are reviewed, or how students "
        "should cite retrieved PMIDs—use your course lead. Instructors typically manage PubMed pulls and the shared "
        "Chroma index.</p>"
        "</div>"
        "</div>"
        '<div class="ail-landing-band ail-landing-band--compact">'
        "<h3>IT & research computing</h3>"
        "<p>Host patching, HTTPS termination, backups of <code>data/</code> (SQLite and Chroma), secrets handling, "
        "and compliance frameworks (FERPA, GDPR, institutional AI policies) belong with your platform team. "
        "Document where this app runs and who can access the filesystem.</p>"
        "</div>"
        '<div class="ail-landing-band ail-subpage-note">'
        "<p><strong>Emergencies.</strong> If credentials are compromised, admins should deactivate accounts in the "
        "permissions console and rotate passwords at the database level per your security runbook.</p>"
        "</div></div>"
    )


def _about_page_html() -> str:
    return (
        '<div class="ail-shell ail-landing-wrap ail-subpage-root">'
        '<p class="ail-landing-section-kicker">About</p>'
        '<h2 class="ail-landing-section-head">MedCorpus Insight</h2>'
        '<p class="ail-subpage-lead">A teaching-oriented workspace for <strong>healthcare AI literacy</strong>: '
        "connecting structured literature access, transparent NLP, and cohort-ready dashboards so discussions stay "
        "anchored in inspectable evidence rather than generic model output.</p>"
        '<div class="ail-landing-band-grid">'
        "<div>"
        "<h3>Mission</h3>"
        "<p>Lower the operational friction for running a serious literature lab inside a course: reproducible pulls, "
        "shared vector indexes for authorized roles, and plots that instructors can critique live with students.</p>"
        "</div>"
        "<div>"
        "<h3>Architecture (high level)</h3>"
        "<ul class=\"ail-reg-list\">"
        "<li><strong>Client:</strong> Streamlit UI with role-aware navigation.</li>"
        "<li><strong>Data:</strong> SQLite for accounts; Chroma for embeddings and document payloads you choose to "
        "index.</li>"
        "<li><strong>NLP:</strong> scikit-learn and domain-appropriate models for keywords, topics, and similarity—"
        "tuned for batch jobs on abstract text.</li>"
        "<li><strong>Sources:</strong> PubMed via NCBI E-utilities when enabled; CSV/JSON otherwise.</li>"
        "</ul>"
        "</div>"
        "</div>"
        '<div class="ail-landing-band ail-landing-band--compact">'
        "<h3>Trust & limitations</h3>"
        "<p>MedCorpus Insight does not replace PubMed, licensed full-text, biostatistical review, or human judgment. "
        "It standardizes a <em>pedagogical</em> pipeline: what you load is what you analyze; what you analyze is what "
        "you show in class.</p>"
        "</div>"
        '<div class="ail-landing-band ail-subpage-note">'
        "<p><strong>Openness.</strong> Your institution hosts the runtime; there is no mandatory cloud vendor for "
        "core storage beyond what you configure for embeddings if you change defaults.</p>"
        "</div></div>"
    )


def _ensure_landing_nav_default() -> None:
    if LANDING_NAV_KEY not in st.session_state:
        st.session_state[LANDING_NAV_KEY] = "overview"


def render_public_landing_nav(button_prefix: str) -> None:
    """Professional top bar: brand left, unified nav right."""
    _ensure_landing_nav_default()
    nav = str(st.session_state[LANDING_NAV_KEY])
    with st.container(border=True):
        c_logo, c_brand, c_nav = st.columns(
            [0.8, 2.2, 4.8],
            gap="small",
            vertical_alignment="center",
        )
        with c_logo:
            if APP_LOGO_PATH.is_file():
                try:
                    st.image(str(APP_LOGO_PATH), width=52)
                except (UnicodeDecodeError, Exception):
                    st.markdown('<p style="font-size:1.75rem;margin:0;">🏥</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p style="font-size:1.75rem;margin:0;">🏥</p>', unsafe_allow_html=True)
        with c_brand:
            st.markdown(
                '<div class="ail-nav-brand-block">'
                f'<strong class="ail-nav-brand-title">{html.escape(APP_BRAND_NAME)}</strong>'
                f'<span class="ail-nav-brand-tag">{html.escape(APP_TAGLINE)}</span>'
                "</div>",
                unsafe_allow_html=True,
            )
        with c_nav:
            label_by_key = {
                "overview": "Home",
                "fields": "Domains",
                "services": "Solutions",
                "contact": "Contact",
                "about": "About Us",
            }
            st.markdown('<div class="ail-public-nav-btnbar">', unsafe_allow_html=True)
            nav_cols = st.columns(len(label_by_key), gap="small", vertical_alignment="center")
            for col, (key, label) in zip(nav_cols, label_by_key.items()):
                with col:
                    if st.button(
                        label,
                        key=f"{button_prefix}_lnav_btn_{key}",
                        type="primary" if nav == key else "secondary",
                        use_container_width=True,
                    ):
                        if nav != key:
                            st.session_state[LANDING_NAV_KEY] = key
                            st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

