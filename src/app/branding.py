"""App shell branding: logo, title, Home / Back, and logo-as-home via URL query."""

from __future__ import annotations

import base64
from typing import Any, Dict, Optional

import streamlit as st
import streamlit.components.v1 as components

from config.settings import (
    APP_BRAND_NAME,
    APP_LOGO_PATH,
    APP_TAGLINE,
    PAGE_ADMIN_DASHBOARD,
    PAGE_INSTRUCTOR_DASHBOARD,
    PAGE_LITERATURE,
    PAGE_STUDENT_HOME,
)

_AIL_PENDING_PAGE_KEY = "_ail_pending_page"


def default_dashboard_page(role: str) -> str:
    if role == "admin":
        return PAGE_ADMIN_DASHBOARD
    if role == "instructor":
        return PAGE_INSTRUCTOR_DASHBOARD
    return PAGE_STUDENT_HOME


def sidebar_nav_key(user: Dict[str, Any], *, auth_disabled: bool) -> Optional[str]:
    if auth_disabled:
        return None
    uid = int(user["id"])
    role = str(user.get("role", "student"))
    if role == "admin":
        return f"ail_page_nav_adm_{uid}"
    if role == "instructor":
        return f"ail_page_nav_ins_{uid}"
    if role == "student":
        return f"ail_page_nav_stu_{uid}"
    return None


def apply_query_param_logo_home(
    user: Dict[str, Any],
    nav_key: Optional[str],
    *,
    auth_disabled: bool,
) -> None:
    """If URL contains ail_home=1 (from clickable logo), go to role dashboard or web Home."""
    if st.query_params.get("ail_home") != "1":
        return
    try:
        del st.query_params["ail_home"]
    except Exception:
        pass

    if auth_disabled:
        st.session_state["ail_web_application_nav"] = "Home"
        st.session_state["_ail_page_snapshot"] = PAGE_LITERATURE
        st.rerun()
        return

    if nav_key:
        dest = default_dashboard_page(str(user.get("role", "student")))
        st.session_state[nav_key] = dest
        st.session_state["_ail_page_snapshot"] = dest
    st.rerun()


def record_nav_history(nav_key: Optional[str], page: str) -> None:
    if not nav_key:
        return
    prev = st.session_state.get("_ail_page_snapshot")
    if prev is not None and prev != page:
        hist = st.session_state.setdefault("ail_nav_history", [])
        if not hist or hist[-1] != prev:
            hist.append(prev)
        while len(hist) > 25:
            hist.pop(0)
    st.session_state["_ail_page_snapshot"] = page


def _go_home(user: Dict[str, Any], nav_key: Optional[str], *, auth_disabled: bool) -> None:
    if auth_disabled:
        st.session_state["ail_web_application_nav"] = "Home"
        st.session_state["_ail_page_snapshot"] = PAGE_LITERATURE
        return
    if nav_key:
        dest = default_dashboard_page(str(user.get("role", "student")))
        st.session_state[_AIL_PENDING_PAGE_KEY] = dest


def _go_back(nav_key: Optional[str]) -> None:
    if not nav_key:
        return
    hist = st.session_state.get("ail_nav_history", [])
    if not hist:
        return
    dest = hist.pop()
    st.session_state[_AIL_PENDING_PAGE_KEY] = dest


def _logo_click_payload_svg() -> str:
    """Returns base64-encoded SVG for logo badge. Falls back to placeholder if file is not SVG."""
    if not APP_LOGO_PATH.is_file():
        # Minimal inline mark if asset missing
        return (
            "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NiA5NiI+"
            "PHJlY3Qgd2lkdGg9Ijk2IiBoZWlnaHQ9Ijk2IiByeD0iMjIiIGZpbGw9IiMwZDk0ODgiLz4"
            "8dGV4dCB4PSI0OCIgeT0iNTYiIGZpbGw9IiNmZmYiIGZvbnQtc2l6ZT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiPuKPsDwvdGV4dD48L3N2Zz4="
        )
    try:
        raw = APP_LOGO_PATH.read_bytes()
        # Check if it's actually an SVG file (starts with <svg or has SVG magic bytes)
        if raw.startswith(b"<svg") or raw.startswith(b"<?xml") or (len(raw) > 4 and raw[:4] == b"\x3c\x73\x76\x67"):
            return base64.b64encode(raw).decode("ascii")
    except Exception:
        pass
    
    # Fall back to placeholder SVG if file can't be read or is not SVG
    return (
        "PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA5NiA5NiI+"
        "PHJlY3Qgd2lkdGg9Ijk2IiBoZWlnaHQ9Ijk2IiByeD0iMjIiIGZpbGw9IiMwZDk0ODgiLz4"
        "8dGV4dCB4PSI0OCIgeT0iNTYiIGZpbGw9IiNmZmYiIGZvbnQtc2l6ZT0iNDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiPuKPsDwvdGV4dD48L3N2Zz4="
    )


def _render_clickable_logo_badge() -> None:
    """Logo navigates like Home: sets query param so the next run applies dashboard (iframe-safe)."""
    b64 = _logo_click_payload_svg()
    safe_name = (
        APP_BRAND_NAME.replace("&", "&amp;")
        .replace('"', "&quot;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )
    html = f"""
<div style="margin:0;padding:0;line-height:0;">
  <a id="ail-logo-home" href="#" title="{safe_name} — dashboard"
     style="display:inline-block;border-radius:14px;overflow:hidden;box-shadow:0 4px 14px rgba(13,148,136,0.25);">
    <img src="data:image/svg+xml;base64,{b64}" width="64" height="64" alt="{safe_name} home" style="display:block;"/>
  </a>
</div>
<script>
  const a = window.document.getElementById('ail-logo-home');
  if (a) {{
    a.addEventListener('click', function (e) {{
      e.preventDefault();
      try {{
        const top = window.parent || window;
        const u = new URL(top.location.href);
        u.searchParams.set('ail_home', '1');
        top.location.href = u.toString();
      }} catch (err) {{
        window.location.search = 'ail_home=1';
      }}
    }});
  }}
</script>
"""
    components.html(html, height=76, scrolling=False)


def render_branded_shell_header(
    user: Dict[str, Any],
    *,
    nav_key: Optional[str],
    auth_disabled: bool,
) -> None:
    st.markdown('<div class="ail-shell ail-brand-header">', unsafe_allow_html=True)
    c_logo, c_title, c_nav = st.columns([1.35, 4.2, 2.45], vertical_alignment="center")
    with c_logo:
        _render_clickable_logo_badge()
    with c_title:
        st.markdown(f"## {APP_BRAND_NAME}")
        st.caption(APP_TAGLINE)
    with c_nav:
        n1, n2 = st.columns(2, gap="small")
        with n1:
            st.button(
                "Home",
                key="ail_hdr_home_btn",
                type="primary",
                use_container_width=True,
                help="Go to your role dashboard (same as clicking the logo)",
                on_click=_go_home,
                kwargs={"user": user, "nav_key": nav_key, "auth_disabled": auth_disabled},
            )
        with n2:
            has_back = bool(nav_key and st.session_state.get("ail_nav_history"))
            st.button(
                "Back",
                key="ail_hdr_back_btn",
                type="secondary",
                use_container_width=True,
                disabled=not has_back,
                help="Return to the previous app area",
                on_click=_go_back,
                args=(nav_key,),
            )
        dn = user.get("display_name") or user.get("username") or "User"
        role = user.get("role", "guest")
        st.caption(f"{dn} · `{role}`")
    st.markdown("</div>", unsafe_allow_html=True)


def try_show_streamlit_logo() -> None:
    """Sidebar / header app mark when supported."""
    try:
        if APP_LOGO_PATH.is_file():
            st.logo(str(APP_LOGO_PATH), size="medium")
        else:
            st.logo(":material/health_metrics:", size="large")
    except Exception:
        pass
