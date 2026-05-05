from __future__ import annotations

import html
import os
from typing import Any, Dict, Optional

import streamlit as st

from src.app.public_landing import (
    LANDING_NAV_KEY,
    bootstrap_context_html,
    hero_metrics_strip_html,
    platform_principles_ribbon_html,
    photo_story_section_html,
    register_context_html,
    render_public_landing_nav,
    sign_in_prompt_html,
    split_hero_html,
    subpage_html,
)
from src.db.app_database import (
    create_bootstrap_admin,
    get_user_by_id,
    init_app_database,
    register_pending_account,
    user_count,
    verify_credentials,
)

AUTH_USER_KEY = "ail_auth_user"
AUTH_DISABLE_ENV = "AIL_DISABLE_AUTH"
AUTH_VIEW_KEY = "ail_auth_view"


def _go_landing_overview(rerun: bool = True) -> None:
    st.session_state[LANDING_NAV_KEY] = "overview"
    if rerun:
        st.rerun()


def _render_subpage_access_footer(*, mode: str, button_key: str) -> None:
    """On marketing-only tabs: no auth forms—single professional CTA back to Overview."""
    st.divider()
    if mode == "bootstrap":
        title = "Administrator setup"
        copy = (
            "The first-administrator form is only on <strong>Overview</strong>. "
            "Use the button below when you are ready to create the account that will own this deployment."
        )
        label = "Return to setup overview"
    elif mode == "register":
        title = "Registration"
        copy = (
            "The registration form is only on <strong>Overview</strong> so Fields, Services, Contact, "
            "and About stay clean reference pages."
        )
        label = "Continue to registration"
    else:
        title = "Sign in"
        copy = (
            "Credentials are only collected on <strong>Overview</strong>. "
            "These tabs are documentation-only for a clearer, more professional first impression."
        )
        label = "Go to sign in"
    st.markdown(
        f'<div class="ail-subpage-cta-wrap">'
        f'<p class="ail-subpage-cta-title">{html.escape(title)}</p>'
        f'<p class="ail-subpage-cta-copy">{copy}</p>'
        "</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns([1, 1.15, 1])
    with c2:
        if st.button(label, type="primary", use_container_width=True, key=button_key):
            _go_landing_overview()


def auth_disabled() -> bool:
    return os.getenv(AUTH_DISABLE_ENV, "").strip().lower() in ("1", "true", "yes", "on")


def init_auth() -> None:
    if not auth_disabled():
        try:
            init_app_database()
        except Exception as ex:
            st.error(f"User database failed to initialize: {ex}")
            st.stop()


def get_session_user() -> Optional[Dict[str, Any]]:
    if auth_disabled():
        return None
    raw = st.session_state.get(AUTH_USER_KEY)
    if raw is None:
        return None
    uid = raw.get("id")
    if uid is None:
        return None
    fresh = get_user_by_id(int(uid))
    if fresh is None or not fresh.get("is_active", True):
        st.session_state.pop(AUTH_USER_KEY, None)
        return None
    st.session_state[AUTH_USER_KEY] = fresh
    return fresh


def login_username_password(username: str, password: str) -> tuple[bool, Optional[str]]:
    user, err = verify_credentials(username, password)
    if user is None:
        if err == "inactive":
            return False, "inactive"
        return False, "invalid"
    st.session_state[AUTH_USER_KEY] = user
    return True, None


def logout() -> None:
    st.session_state.pop(AUTH_USER_KEY, None)


def _auth_view() -> str:
    if AUTH_VIEW_KEY not in st.session_state:
        st.session_state[AUTH_VIEW_KEY] = "login"
    return str(st.session_state[AUTH_VIEW_KEY])


def _set_auth_view(view: str) -> None:
    st.session_state[AUTH_VIEW_KEY] = view
    st.session_state[LANDING_NAV_KEY] = "overview"


def render_bootstrap_page() -> None:
    render_public_landing_nav("boot")
    nav = str(st.session_state.get(LANDING_NAV_KEY, "overview"))
    if nav == "overview":
        st.markdown(
            split_hero_html(
                lead="No accounts exist yet. Create the first administrator to secure this workspace.",
                pills=("One-time setup", "Local sign-in", "You choose the password"),
            ),
            unsafe_allow_html=True,
        )
        st.markdown(bootstrap_context_html(), unsafe_allow_html=True)
    else:
        st.markdown(subpage_html(nav), unsafe_allow_html=True)
        _render_subpage_access_footer(mode="bootstrap", button_key="boot_sub_cta")
        return
    _, b_mid, _ = st.columns([1, 1.35, 1], gap="large")
    with b_mid:
        st.markdown('<p class="ail-auth-panel-title">Administrator account</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="ail-auth-panel-hint">You will use this username and password to sign in and manage users.</p>',
            unsafe_allow_html=True,
        )
        with st.form("bootstrap_form"):
            u = st.text_input("Admin username", placeholder="e.g. admin")
            d = st.text_input("Display name", placeholder="Your name")
            p1 = st.text_input("Password", type="password")
            p2 = st.text_input("Confirm password", type="password")
            ok = st.form_submit_button("Create administrator", type="primary", use_container_width=True)

    if ok:
        if p1 != p2:
            st.error("Passwords do not match.")
        else:
            success, msg = create_bootstrap_admin((u or "").strip(), p1, d)
            if success:
                st.success("Administrator created. Sign in below.")
                _set_auth_view("login")
                st.rerun()
            else:
                st.error(msg)


def render_register_page() -> None:
    render_public_landing_nav("reg")
    nav = str(st.session_state.get(LANDING_NAV_KEY, "overview"))
    if nav != "overview":
        st.markdown(subpage_html(nav), unsafe_allow_html=True)
        _render_subpage_access_footer(mode="register", button_key="reg_sub_cta")
        if st.button("Back to sign in", key="reg_back_sub"):
            _set_auth_view("login")
        return

    st.markdown(
        split_hero_html(
            lead="Request access. An administrator activates new accounts and assigns your role.",
            pills=("Students & staff", "Secure workspace", "Same portal after approval"),
        ),
        unsafe_allow_html=True,
    )
    st.markdown(hero_metrics_strip_html(), unsafe_allow_html=True)
    st.markdown(photo_story_section_html(), unsafe_allow_html=True)
    st.markdown(register_context_html(), unsafe_allow_html=True)

    c_feat, c_form = st.columns([1, 1], gap="large")
    with c_feat:
        st.markdown(
            '<div class="ail-landing-features">'
            '<div class="ail-landing-feature-card"><strong>Timing</strong>'
            "<p>No email from this app—ask your program how approvals work.</p></div>"
            '<div class="ail-landing-feature-card"><strong>Password</strong>'
            "<p>Do not reuse a bank or email password here.</p></div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c_form:
        st.markdown('<p class="ail-auth-panel-title">Create account</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="ail-auth-panel-hint">Choose a username and a strong password (8+ characters).</p>',
            unsafe_allow_html=True,
        )
        with st.form("register_form"):
            u = st.text_input("Username", key="reg_u")
            d = st.text_input("Display name", key="reg_d")
            p1 = st.text_input("Password", type="password")
            p2 = st.text_input("Confirm password", type="password")
            sub = st.form_submit_button("Register", type="primary", use_container_width=True)

    if sub:
        if p1 != p2:
            st.error("Passwords do not match.")
        else:
            uname = (st.session_state.get("reg_u") or u or "").strip()
            dname = (st.session_state.get("reg_d") or d or "").strip()
            ok, msg = register_pending_account(uname, p1, dname)
            if ok:
                st.session_state["ail_reg_ok"] = True
                _set_auth_view("login")
                st.rerun()
            else:
                st.error(msg)
    if st.button("Back to sign in", key="reg_back"):
        _set_auth_view("login")
        st.rerun()


def render_login_page() -> None:
    render_public_landing_nav("login")
    nav = str(st.session_state.get(LANDING_NAV_KEY, "overview"))
    if nav != "overview":
        st.markdown(subpage_html(nav), unsafe_allow_html=True)
        _render_subpage_access_footer(mode="login", button_key="login_sub_cta")
        return

    st.markdown(
        split_hero_html(
            lead="A workspace for healthcare AI literacy: pull structured PubMed slices, run transparent NLP, "
            "and guide learners through charts and Q&A grounded in what is actually loaded—so instruction stays "
            "anchored in sources you can open and verify.",
            pills=("AI in health literature", "Teaching-grade NLP", "Traceable sources"),
        ),
        unsafe_allow_html=True,
    )
    st.markdown(hero_metrics_strip_html(), unsafe_allow_html=True)
    st.markdown(photo_story_section_html(), unsafe_allow_html=True)
    st.markdown(platform_principles_ribbon_html(), unsafe_allow_html=True)
    if st.session_state.pop("ail_reg_ok", None):
        st.success("Registration saved. An administrator must activate your account before you can sign in.")

    c_feat, c_form = st.columns([1.2, 1], gap="large")
    with c_feat:
        st.markdown(
            '<div class="ail-landing-features">'
            '<div class="ail-landing-feature-card"><strong>Data</strong>'
            "<p>PubMed pull, shared Chroma store, or CSV upload depending on role.</p></div>"
            '<div class="ail-landing-feature-card"><strong>Plots</strong>'
            "<p>Journals, keywords, time, graph preview, Q&amp;A on whatever is loaded.</p></div>"
            '<div class="ail-landing-feature-card"><strong>Login</strong>'
            "<p>Org-issued credentials; self-register stays pending until an admin enables it.</p></div>"
            "</div>",
            unsafe_allow_html=True,
        )
    with c_form:
        st.markdown('<p class="ail-auth-panel-title">Sign in</p>', unsafe_allow_html=True)
        st.markdown(
            '<p class="ail-auth-panel-hint">Use the credentials from your administrator or instructor.</p>',
            unsafe_allow_html=True,
        )
        with st.form("login_form", clear_on_submit=False):
            u = st.text_input("Username", key="ail_login_username")
            p = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)

        if submitted:
            username = (u or "").strip()
            password = p or ""
            if not username or not password:
                st.error("Enter both username and password.")
            else:
                success, err = login_username_password(username, password)
                if success:
                    st.session_state["ail_post_login_rerun"] = True
                elif err == "inactive":
                    st.warning("Your account is not active yet. Contact an administrator.")
                else:
                    st.error("Unknown username or incorrect password.")

        if st.session_state.pop("ail_post_login_rerun", None):
            st.rerun()
        if user_count() > 0:
            if st.button("Create an account", use_container_width=True, key="go_register"):
                _set_auth_view("register")
                st.rerun()
    st.markdown(sign_in_prompt_html(), unsafe_allow_html=True)


def render_auth_screen() -> None:
    if user_count() == 0:
        render_bootstrap_page()
        return
    if _auth_view() == "register":
        render_register_page()
    else:
        render_login_page()

