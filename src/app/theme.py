import streamlit as st


def inject_app_theme() -> None:
    st.markdown(
        """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;1,400&display=swap');

:root {
  --ail-bg-0: #f7faf9;
  --ail-bg-1: #eef6f4;
  --ail-bg-2: #e8f2f0;
  --ail-ink: #0c1f1d;
  --ail-ink-muted: #5c726e;
  --ail-teal: #0d9488;
  --ail-teal-deep: #0f766e;
  --ail-teal-glow: rgba(13, 148, 136, 0.12);
  --ail-card: #ffffff;
  --ail-border: rgba(13, 148, 136, 0.14);
  --ail-shadow: 0 4px 24px rgba(12, 31, 29, 0.06);
  --ail-shadow-lg: 0 20px 50px rgba(12, 31, 29, 0.08);
}

html, body, [class*="css"] {
  font-family: 'Plus Jakarta Sans', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}

[data-testid="stAppViewContainer"] {
  background-color: var(--ail-bg-0) !important;
  background-image:
    radial-gradient(ellipse 100% 60% at 100% -10%, var(--ail-teal-glow), transparent 55%),
    radial-gradient(ellipse 70% 50% at -5% 110%, rgba(15, 118, 110, 0.08), transparent 50%),
    radial-gradient(circle at 1px 1px, rgba(13, 148, 136, 0.045) 1px, transparent 0) !important;
  background-size: auto, auto, 22px 22px !important;
}

[data-testid="stHeader"] {
  background: linear-gradient(180deg, rgba(247, 250, 249, 0.92) 0%, rgba(247, 250, 249, 0.65) 100%) !important;
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--ail-border);
}

section[data-testid="stSidebar"] {
  background: linear-gradient(195deg, #0c4a6e 0%, #115e59 48%, #134e4a 100%) !important;
  border-right: 1px solid rgba(255, 255, 255, 0.1);
  box-shadow: 4px 0 32px rgba(12, 74, 110, 0.15);
  color: #ecfdf5;
}
/* Do not use sidebar * { color } — it makes text invisible on white inputs / file upload. */
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
  color: #a7f3d0 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span {
  color: #a7f3d0 !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
  color: #f0fdfa !important;
}
section[data-testid="stSidebar"] .stRadio label {
  color: #f0fdfa !important;
}
section[data-testid="stSidebar"] hr {
  border-color: rgba(255, 255, 255, 0.14) !important;
}
section[data-testid="stSidebar"] .stButton button {
  border-radius: 10px !important;
  font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stButton button[kind="secondary"],
section[data-testid="stSidebar"] .stDownloadButton button {
  color: #0f172a !important;
}
section[data-testid="stSidebar"] .stButton button[kind="primary"] {
  color: #ffffff !important;
}
/* Typed text + light widgets on white backgrounds */
section[data-testid="stSidebar"] [data-baseweb="input"] input,
section[data-testid="stSidebar"] [data-baseweb="textarea"] textarea,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] input[type="text"],
section[data-testid="stSidebar"] input[type="number"],
section[data-testid="stSidebar"] input[type="email"],
section[data-testid="stSidebar"] input[type="password"],
section[data-testid="stSidebar"] input[type="search"] {
  color: #0c1f1d !important;
  -webkit-text-fill-color: #0c1f1d !important;
  caret-color: #0c1f1d !important;
  border-radius: 10px !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] label,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] p,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] span,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] small,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] section,
section[data-testid="stSidebar"] [data-testid="stFileUploader"] div[class*="upload"] {
  color: #0f172a !important;
}
section[data-testid="stSidebar"] [data-testid="stFileUploader"] a {
  color: #0d9488 !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
  color: #0f172a !important;
}

.block-container {
  padding-top: 1.25rem !important;
  padding-bottom: 3.5rem !important;
  max-width: 1240px !important;
}

h1 {
  font-weight: 700 !important;
  letter-spacing: -0.03em !important;
  color: var(--ail-ink) !important;
  font-size: 1.95rem !important;
}
h2, h3 {
  font-weight: 600 !important;
  letter-spacing: -0.02em !important;
  color: #134e4a !important;
}

[data-testid="stCaptionContainer"] {
  color: var(--ail-ink-muted) !important;
}

.stTabs [data-baseweb="tab-list"] {
  gap: 8px;
  background: rgba(255, 255, 255, 0.75);
  padding: 8px 10px;
  border-radius: 14px;
  border: 1px solid var(--ail-border);
  box-shadow: var(--ail-shadow);
}
.stTabs [data-baseweb="tab"] {
  border-radius: 10px !important;
  font-weight: 600 !important;
  padding: 10px 18px !important;
}
.stTabs [aria-selected="true"] {
  background: linear-gradient(145deg, #14b8a6 0%, #0d9488 45%, #0f766e 100%) !important;
  color: #fff !important;
  border-radius: 10px !important;
  box-shadow: 0 4px 16px rgba(13, 148, 136, 0.35) !important;
}
.stTabs [aria-selected="false"] {
  color: #475569 !important;
}

div[data-testid="stMetric"] {
  background: linear-gradient(165deg, #ffffff 0%, #f8fcfb 100%);
  border: 1px solid var(--ail-border);
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: var(--ail-shadow);
  border-left: 4px solid var(--ail-teal);
}
div[data-testid="stMetric"] label {
  color: var(--ail-ink-muted) !important;
  font-weight: 600 !important;
  text-transform: uppercase !important;
  font-size: 0.68rem !important;
  letter-spacing: 0.06em !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
  color: var(--ail-teal-deep) !important;
  font-weight: 700 !important;
}

div[data-testid="stExpander"] {
  border: 1px solid var(--ail-border) !important;
  border-radius: 14px !important;
  overflow: hidden;
  box-shadow: var(--ail-shadow);
  background: rgba(255, 255, 255, 0.6) !important;
}

/* App shell cards (portal) */
.ail-shell {
  max-width: 1140px;
  margin: 0 auto;
}
.ail-brand-header {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.92) 0%, rgba(248, 252, 251, 0.75) 100%);
  border: 1px solid var(--ail-border);
  border-radius: 18px;
  padding: 16px 20px 18px 20px;
  margin-bottom: 18px;
  box-shadow: var(--ail-shadow);
}
.ail-hero {
  background: linear-gradient(125deg, #0f766e 0%, #0d9488 38%, #0e7490 72%, #155e75 100%);
  color: #fff;
  border-radius: 20px;
  padding: 32px 36px;
  margin-bottom: 24px;
  box-shadow: var(--ail-shadow-lg), 0 0 0 1px rgba(255, 255, 255, 0.12) inset;
  position: relative;
  overflow: hidden;
}
.ail-hero::after {
  content: "";
  position: absolute;
  top: -40%;
  right: -15%;
  width: 55%;
  height: 140%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 65%);
  pointer-events: none;
}
.ail-hero h1 {
  color: #fff !important;
  font-size: 1.55rem !important;
  margin: 0 0 10px 0 !important;
  position: relative;
  z-index: 1;
}
.ail-hero p {
  color: rgba(255, 255, 255, 0.92) !important;
  margin: 0;
  font-size: 1rem;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}
.ail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}
.ail-card {
  background: linear-gradient(180deg, #ffffff 0%, #fafdfc 100%);
  border: 1px solid var(--ail-border);
  border-radius: 16px;
  padding: 20px 22px;
  box-shadow: var(--ail-shadow);
  transition: box-shadow 0.2s ease, transform 0.2s ease;
}
.ail-card:hover {
  box-shadow: 0 8px 32px rgba(12, 31, 29, 0.09);
}
.ail-card-label {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: var(--ail-ink-muted);
  margin-bottom: 8px;
}
.ail-card-value {
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--ail-teal-deep);
  line-height: 1.1;
}
.ail-card-sub {
  font-size: 0.82rem;
  color: var(--ail-ink-muted);
  margin-top: 8px;
}
.ail-section-title {
  font-size: 1.08rem;
  font-weight: 700;
  color: #134e4a;
  margin: 28px 0 14px 0;
  padding-bottom: 10px;
  border-bottom: 2px solid rgba(13, 148, 136, 0.35);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);
}
.ail-row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18px;
}
@media (max-width: 900px) {
  .ail-row-2 { grid-template-columns: 1fr; }
}
.ail-pill {
  display: inline-block;
  font-size: 0.74rem;
  font-weight: 600;
  padding: 5px 12px;
  border-radius: 999px;
  background: linear-gradient(135deg, #ccfbf1, #99f6e4);
  color: #115e59;
  margin-right: 6px;
  margin-bottom: 6px;
}
.ail-status-ok {
  border-left: 4px solid #10b981;
}
.ail-status-info {
  border-left: 4px solid var(--ail-teal);
}
.ail-table-wrap {
  overflow-x: auto;
  border: 1px solid var(--ail-border);
  border-radius: 14px;
  background: #fff;
  box-shadow: var(--ail-shadow);
}

.ail-landing-wrap {
  max-width: 1140px;
  margin: 0 auto 8px auto;
}
.ail-landing-hero-split {
  display: grid;
  grid-template-columns: 1.05fr 0.95fr;
  gap: 0;
  border-radius: 24px;
  overflow: hidden;
  margin-bottom: 12px;
  box-shadow: var(--ail-shadow-lg), 0 0 0 1px rgba(255, 255, 255, 0.08) inset;
  min-height: 300px;
}
@media (max-width: 900px) {
  .ail-landing-hero-split { grid-template-columns: 1fr; min-height: 0; }
}
.ail-hero-split-text {
  background: linear-gradient(145deg, #083932 0%, #0d9488 48%, #0f766e 100%);
  color: #fff;
  padding: 44px 40px 40px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  position: relative;
}
.ail-hero-split-text::before {
  content: "";
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 70% at 100% 0%, rgba(255,255,255,0.1), transparent 55%);
  pointer-events: none;
}
.ail-hero-split-text h1,
.ail-hero-split-text .ail-landing-lead,
.ail-hero-split-text .ail-landing-pills {
  position: relative;
  z-index: 1;
}
.ail-hero-split-text h1 {
  color: #fff !important;
  font-size: clamp(1.75rem, 3.8vw, 2.35rem) !important;
  margin: 0 0 14px 0 !important;
  letter-spacing: -0.045em !important;
  line-height: 1.15 !important;
  font-weight: 700 !important;
}
.ail-hero-split-text .ail-landing-hero-tag {
  display: block;
  font-size: 0.88rem !important;
  line-height: 1.45 !important;
  color: rgba(255, 255, 255, 0.88) !important;
  margin: -6px 0 14px 0 !important;
  max-width: 36rem;
}
.ail-hero-split-text .ail-landing-lead {
  color: rgba(255, 255, 255, 0.94) !important;
  font-size: 1.06rem;
  line-height: 1.68;
  margin: 0;
  max-width: 32rem;
}
.ail-hero-split-visual {
  position: relative;
  min-height: 280px;
  background: #0c4a6e;
}
.ail-hero-split-visual img {
  width: 100%;
  height: 100%;
  min-height: 280px;
  object-fit: cover;
  display: block;
}
.ail-landing-section-kicker {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: #0d9488;
  margin: 28px 0 6px 0;
}
.ail-landing-section-head {
  font-size: clamp(1.2rem, 2.2vw, 1.45rem);
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 20px 0;
  letter-spacing: -0.02em;
  line-height: 1.3;
}
.ail-landing-photo-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 8px;
}
@media (max-width: 900px) {
  .ail-landing-photo-row { grid-template-columns: 1fr; }
}
.ail-photo-tile {
  margin: 0;
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  box-shadow: var(--ail-shadow);
  aspect-ratio: 4 / 3;
  border: 1px solid var(--ail-border);
}
.ail-photo-tile img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.35s ease;
}
.ail-photo-tile:hover img {
  transform: scale(1.04);
}
.ail-photo-tile figcaption {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  padding: 20px 18px 16px;
  background: linear-gradient(180deg, transparent 0%, rgba(8, 28, 26, 0.75) 45%, rgba(6, 22, 20, 0.92) 100%);
  color: #f8fafc;
}
.ail-photo-tile figcaption strong {
  display: block;
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 6px;
  letter-spacing: -0.02em;
}
.ail-photo-tile figcaption span {
  display: block;
  font-size: 0.8rem;
  line-height: 1.5;
  color: rgba(248, 250, 252, 0.88);
}

/* Replaces the old “band + photo” block on sign-in overview */
.ail-landing-principles-ribbon {
  position: relative;
  border-radius: 22px;
  padding: 32px 36px 30px;
  margin: 8px 0 24px 0;
  background: linear-gradient(135deg, #0a5c52 0%, #0d9488 42%, #0e7490 100%);
  color: #ecfdf5;
  box-shadow: var(--ail-shadow-lg), 0 0 0 1px rgba(255, 255, 255, 0.1) inset;
  overflow: hidden;
}
.ail-landing-principles-ribbon::after {
  content: "";
  position: absolute;
  top: -35%;
  right: -8%;
  width: 50%;
  height: 95%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 62%);
  pointer-events: none;
}
.ail-landing-ribbon-kicker {
  position: relative;
  z-index: 1;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  font-size: 0.7rem;
  color: rgba(236, 253, 245, 0.88);
  margin: 0 0 10px 0;
  font-weight: 700;
}
.ail-landing-ribbon-title {
  position: relative;
  z-index: 1;
  color: #fff !important;
  font-size: clamp(1.2rem, 2.1vw, 1.5rem) !important;
  font-weight: 700 !important;
  margin: 0 0 22px 0 !important;
  letter-spacing: -0.03em !important;
  line-height: 1.25 !important;
  max-width: 40rem;
}
.ail-landing-ribbon-grid {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 22px 32px;
}
@media (max-width: 900px) {
  .ail-landing-ribbon-grid { grid-template-columns: 1fr; }
}
.ail-landing-ribbon-col {
  background: rgba(0, 0, 0, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 14px;
  padding: 16px 18px 18px 18px;
  backdrop-filter: blur(4px);
}
.ail-landing-ribbon-h3 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #fff !important;
  margin: 0 0 8px 0;
  letter-spacing: -0.02em;
}
.ail-landing-ribbon-p {
  margin: 0;
  font-size: 0.86rem;
  line-height: 1.6;
  color: rgba(236, 253, 245, 0.94) !important;
}
.ail-landing-ribbon-foot {
  position: relative;
  z-index: 1;
  margin: 22px 0 0 0;
  padding-top: 18px;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  font-size: 0.8rem;
  line-height: 1.55;
  color: rgba(255, 255, 255, 0.82) !important;
}

.ail-landing-band {
  background: linear-gradient(165deg, #f0fdfa 0%, #ecfeff 55%, #f8fafc 100%);
  border: 1px solid var(--ail-border);
  border-radius: 22px;
  padding: 36px 40px 32px;
  margin: 20px 0 24px 0;
  box-shadow: var(--ail-shadow);
}
.ail-landing-band--compact {
  padding: 24px 28px;
  margin-bottom: 20px;
}
.ail-landing-band--compact h3 {
  margin-top: 0;
}
.ail-landing-band h3 {
  font-size: 1.08rem;
  color: #134e4a;
  margin: 0 0 10px 0;
  letter-spacing: -0.02em;
}
.ail-landing-band p {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.65;
  color: #475569;
}
.ail-landing-band-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 28px 36px;
  margin-bottom: 28px;
}
@media (max-width: 800px) {
  .ail-landing-band-grid { grid-template-columns: 1fr; }
}
.ail-landing-band-aside {
  display: grid;
  grid-template-columns: minmax(0, 220px) 1fr;
  gap: 24px;
  align-items: center;
  padding-top: 24px;
  border-top: 1px solid rgba(13, 148, 136, 0.2);
}
@media (max-width: 640px) {
  .ail-landing-band-aside { grid-template-columns: 1fr; }
}
.ail-landing-band-aside img {
  width: 100%;
  border-radius: 14px;
  object-fit: cover;
  aspect-ratio: 4/3;
  box-shadow: var(--ail-shadow);
}
.ail-landing-band-aside-text h4 {
  margin: 0 0 8px 0;
  font-size: 1rem;
  color: #134e4a;
}
.ail-landing-band-aside-text p {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.6;
  color: #64748b;
}
.ail-landing-closing {
  text-align: center;
  font-size: 0.88rem;
  font-weight: 600;
  color: #475569;
  margin: 8px 0 20px 0;
  letter-spacing: 0.02em;
}

.ail-landing-metrics {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 8px;
}
@media (max-width: 900px) {
  .ail-landing-metrics { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
.ail-landing-metric {
  background: linear-gradient(165deg, #ffffff 0%, #f8fcfb 100%);
  border: 1px solid var(--ail-border);
  border-radius: 16px;
  padding: 16px 18px;
  box-shadow: var(--ail-shadow);
  text-align: center;
}
.ail-landing-metric-value {
  display: block;
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--ail-teal-deep);
  letter-spacing: -0.03em;
  line-height: 1.15;
}
.ail-landing-metric-label {
  display: block;
  margin-top: 6px;
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--ail-ink-muted);
  line-height: 1.35;
}

.ail-nav-brand-block {
  display: flex;
  flex-direction: column;
  gap: 2px;
  justify-content: center;
  min-height: 52px;
  min-width: 0;
}
.ail-nav-brand-title {
  font-size: 1.08rem;
  font-weight: 700;
  color: #134e4a;
  letter-spacing: -0.02em;
}
.ail-nav-brand-tag {
  font-size: 0.7rem;
  font-weight: 500;
  color: #64748b;
  line-height: 1.3;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.ail-public-nav-btnbar .stButton button {
  border-radius: 10px !important;
  min-height: 36px !important;
  font-size: 0.84rem !important;
  font-weight: 600 !important;
  white-space: nowrap !important;
}
.ail-public-nav-btnbar .stButton button[kind="secondary"] {
  border: 1px solid rgba(12, 31, 29, 0.12) !important;
  background: #ffffff !important;
  color: #0f172a !important;
}
.ail-public-nav-btnbar .stButton button[kind="primary"] {
  border: 1px solid #0d9488 !important;
  background: #ffffff !important;
  color: #0f172a !important;
  box-shadow: 0 0 0 2px rgba(13, 148, 136, 0.14) !important;
}

.ail-subpage-root .ail-subpage-lead {
  font-size: 1.02rem;
  line-height: 1.65;
  color: #475569;
  margin: 0 0 22px 0;
  max-width: 52rem;
}
.ail-subpage-h3 {
  font-size: 1.02rem;
  font-weight: 700;
  color: #134e4a;
  margin: 22px 0 12px 0;
  letter-spacing: -0.02em;
}
.ail-subpage-card p {
  font-size: 0.88rem;
  line-height: 1.58;
}
.ail-subpage-list li {
  margin-bottom: 8px;
}
.ail-subpage-band {
  margin-top: 8px;
}
.ail-subpage-services-wrap {
  margin-bottom: 8px;
}
.ail-subpage-service-grid {
  margin-bottom: 6px;
}
.ail-subpage-note {
  margin-top: 18px !important;
  background: linear-gradient(165deg, #f8fafc 0%, #f1f5f9 100%) !important;
  border-color: rgba(100, 116, 139, 0.2) !important;
}
.ail-subpage-note p {
  margin: 0;
  font-size: 0.88rem;
  line-height: 1.6;
  color: #475569;
}

.ail-subpage-cta-wrap {
  text-align: center;
  max-width: 36rem;
  margin: 0 auto 8px auto;
}
.ail-subpage-cta-title {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: #0d9488;
  margin: 0 0 8px 0;
}
.ail-subpage-cta-copy {
  font-size: 0.9rem;
  line-height: 1.55;
  color: #64748b;
  margin: 0;
}
.ail-subpage-root .ail-landing-band-grid h3 {
  font-size: 1rem;
  color: #134e4a;
  margin-top: 0;
}
.ail-subpage-root .ail-landing-band-grid p {
  font-size: 0.88rem;
  line-height: 1.6;
  color: #475569;
}
.ail-landing-register-context {
  display: grid;
  grid-template-columns: minmax(0, 320px) 1fr;
  gap: 28px;
  align-items: start;
  margin: 20px 0 24px 0;
  padding: 24px 28px;
  background: linear-gradient(180deg, #ffffff 0%, #f8fcfb 100%);
  border: 1px solid var(--ail-border);
  border-radius: 20px;
  box-shadow: var(--ail-shadow);
}
@media (max-width: 800px) {
  .ail-landing-register-context { grid-template-columns: 1fr; }
}
.ail-reg-context-visual img {
  width: 100%;
  border-radius: 16px;
  object-fit: cover;
  aspect-ratio: 16/11;
  box-shadow: var(--ail-shadow);
}
.ail-landing-register-context h3 {
  margin: 0 0 12px 0;
  font-size: 1.12rem;
  color: #134e4a;
}
.ail-landing-register-context p {
  margin: 0 0 14px 0;
  font-size: 0.9rem;
  line-height: 1.65;
  color: #475569;
}
.ail-reg-list {
  margin: 0;
  padding-left: 1.15rem;
  font-size: 0.86rem;
  line-height: 1.65;
  color: #64748b;
}
.ail-reg-list li { margin-bottom: 6px; }
.ail-landing-pills {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 22px;
  position: relative;
  z-index: 1;
}
.ail-landing-pill {
  display: inline-block;
  font-size: 0.82rem;
  font-weight: 600;
  padding: 8px 14px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.18);
  color: #ecfdf5;
  border: 1px solid rgba(255, 255, 255, 0.22);
}
.ail-landing-features {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}
@media (min-width: 880px) {
  .ail-landing-features { grid-template-columns: 1fr 1fr; }
}
.ail-landing-feature-card {
  background: linear-gradient(180deg, #ffffff 0%, #f8fcfb 100%);
  border: 1px solid var(--ail-border);
  border-radius: 16px;
  padding: 18px 20px;
  box-shadow: var(--ail-shadow);
}
.ail-landing-feature-card strong {
  color: #134e4a;
  font-size: 0.95rem;
}
.ail-landing-feature-card p {
  margin: 8px 0 0 0;
  font-size: 0.88rem;
  color: var(--ail-ink-muted);
  line-height: 1.5;
}
.ail-auth-panel-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: #134e4a;
  margin-bottom: 4px;
}
.ail-auth-panel-hint {
  font-size: 0.82rem;
  color: var(--ail-ink-muted);
  margin-bottom: 16px;
}

.stButton > button[kind="primary"] {
  background: linear-gradient(145deg, #14b8a6, #0d9488) !important;
  border: none !important;
  border-radius: 10px !important;
  font-weight: 600 !important;
  box-shadow: 0 4px 14px rgba(13, 148, 136, 0.3) !important;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
</style>
        """,
        unsafe_allow_html=True,
    )
