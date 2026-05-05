from __future__ import annotations

from typing import Optional

import pandas as pd
import streamlit as st

from src.db.app_database import (
    admin_approve_user,
    admin_create_user,
    admin_delete_user,
    admin_reset_password,
    admin_set_active,
    admin_set_role,
    admin_set_supervised_by,
    list_instructors_for_select,
    list_users_admin,
)


def render_administration_panel(*, actor_id: int) -> None:
    st.markdown("### User administration")
    st.caption(
        "Approve self-service registrations, create accounts, assign roles (admin / instructor / student), "
        "reset passwords, and deactivate access. Changes apply immediately."
    )

    users = list_users_admin()
    pending = [u for u in users if not u["is_active"]]
    m1, m2, m3 = st.columns(3)
    m1.metric("Pending approval", len(pending))
    m2.metric("Total accounts", len(users))
    m3.metric(
        "Administrators",
        sum(1 for u in users if u["role"] == "admin" and u["is_active"]),
    )

    instructors = list_instructors_for_select()

    if pending:
        st.markdown("#### Pending registrations")
        for pu in pending:
            with st.expander(f"`{pu['username']}` — {pu['display_name']}"):
                role_pick = st.selectbox(
                    "Assign role on approval",
                    ["student", "instructor"],
                    key=f"adm_ap_role_{pu['id']}",
                )
                sup_id: Optional[int] = None
                if role_pick == "student" and instructors:
                    labels = ["(none yet)"] + [f"{x['username']} — {x['display_name']}" for x in instructors]
                    sup_pick = st.selectbox(
                        "Supervising instructor (optional)",
                        range(len(labels)),
                        format_func=lambda i: labels[i],
                        key=f"adm_ap_sup_{pu['id']}",
                    )
                    if sup_pick > 0:
                        sup_id = int(instructors[sup_pick - 1]["id"])
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("Approve & activate", key=f"adm_ap_ok_{pu['id']}", type="primary"):
                        ok, msg = admin_approve_user(
                            pu["id"], role_pick, actor_id, supervised_by_id=sup_id
                        )
                        if ok:
                            st.success("Account activated.")
                            st.rerun()
                        else:
                            st.error(msg)
                with c2:
                    if st.button("Reject (remove request)", key=f"adm_ap_del_{pu['id']}"):
                        ok, msg = admin_delete_user(pu["id"], actor_id)
                        if ok:
                            st.rerun()
                        else:
                            st.error(msg)

    st.markdown("#### Directory")
    df = pd.DataFrame(users)
    if not df.empty:
        df["active"] = df["is_active"].map({True: "yes", False: "no"})
        cols = ["id", "username", "display_name", "role", "active", "created_at", "last_login_at"]
        if "supervisor_username" in df.columns:
            cols.insert(5, "supervisor_username")
        show = df[[c for c in cols if c in df.columns]]
        st.dataframe(show, use_container_width=True, hide_index=True, height=min(420, 38 * (len(show) + 2)))
    else:
        st.info("No user records.")

    st.markdown("#### Create account")
    with st.form("adm_create_user"):
        nu = st.text_input("Username", placeholder="unique login")
        nd = st.text_input("Display name", placeholder="shown in the app")
        np = st.text_input("Initial password", type="password")
        nr = st.selectbox("Role", ["student", "instructor", "admin"])
        n_act = st.checkbox("Active immediately", value=True)
        n_sup = None
        if nr == "student" and instructors:
            lab = ["(none)"] + [f"{x['username']} — {x['display_name']}" for x in instructors]
            ix = st.selectbox(
                "Supervising instructor",
                range(len(lab)),
                format_func=lambda i: lab[i],
                key="adm_create_sup",
            )
            if ix > 0:
                n_sup = int(instructors[ix - 1]["id"])
        if st.form_submit_button("Create user"):
            ok, msg = admin_create_user(nu, np, nr, nd, is_active=n_act, supervised_by_id=n_sup)
            if ok:
                st.success("User created.")
                st.rerun()
            else:
                st.error(msg)

    st.markdown("#### Manage existing user")
    if not users:
        st.caption("No users to manage.")
        return
    options = {f"{u['username']} (id {u['id']})": u for u in users}
    pick = st.selectbox("User", list(options.keys()), key="adm_manage_pick")
    target = options[pick]
    uid = int(target["id"])
    st.caption(f"Role: **{target['role']}** · Active: **{'yes' if target['is_active'] else 'no'}**")

    c1, c2 = st.columns(2)
    with c1:
        _roles = ["admin", "instructor", "student"]
        _ri = _roles.index(target["role"]) if target["role"] in _roles else 0
        new_role = st.selectbox(
            "Set role",
            _roles,
            index=_ri,
            key=f"adm_role_{uid}",
        )
        if st.button("Apply role", key=f"adm_role_btn_{uid}"):
            ok, msg = admin_set_role(uid, new_role, actor_id)
            if ok:
                st.success("Role updated.")
                st.rerun()
            else:
                st.error(msg)
    with c2:
        if target["role"] == "student" and instructors:
            lab = ["(unassigned)"] + [f"{x['username']} — {x['display_name']}" for x in instructors]
            cur = target.get("supervised_by")
            default_i = 0
            if cur:
                for i, x in enumerate(instructors, start=1):
                    if int(x["id"]) == int(cur):
                        default_i = i
                        break
            sup_i = st.selectbox(
                "Student’s instructor",
                range(len(lab)),
                index=default_i,
                format_func=lambda i: lab[i],
                key=f"adm_stu_sup_{uid}",
            )
            new_sup = None if sup_i == 0 else int(instructors[sup_i - 1]["id"])
            if st.button("Save supervisor", key=f"adm_stu_sup_btn_{uid}"):
                ok, msg = admin_set_supervised_by(uid, new_sup, actor_id)
                if ok:
                    st.success("Supervisor updated.")
                    st.rerun()
                else:
                    st.error(msg)
        if target["is_active"]:
            if st.button("Deactivate account", key=f"adm_deact_{uid}"):
                ok, msg = admin_set_active(uid, False, actor_id)
                if ok:
                    st.success("User deactivated.")
                    st.rerun()
                else:
                    st.error(msg)
        else:
            if st.button("Activate account", key=f"adm_act_{uid}"):
                ok, msg = admin_set_active(uid, True, actor_id)
                if ok:
                    st.success("User activated.")
                    st.rerun()
                else:
                    st.error(msg)

    with st.form("adm_reset_pw"):
        st.markdown("**Reset password**")
        npw = st.text_input("New password (min 8 characters)", type="password", key=f"adm_npw_{uid}")
        if st.form_submit_button("Update password"):
            ok, msg = admin_reset_password(uid, npw, actor_id)
            if ok:
                st.success("Password updated.")
                st.rerun()
            else:
                st.error(msg)

    if uid != actor_id:
        if st.button("Delete user permanently", key=f"adm_rm_{uid}"):
            ok, msg = admin_delete_user(uid, actor_id)
            if ok:
                st.rerun()
            else:
                st.error(msg)
