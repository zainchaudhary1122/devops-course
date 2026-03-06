import streamlit as st
import os, io, re, base64, html as html_lib
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# PAGE CONFIG  (must be FIRST streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Drive Viewer",
    page_icon="📁",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# CSS  – sidebar styling uses PLAIN TEXT labels
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family:'Inter',sans-serif; }

/* ══ SIDEBAR ALWAYS VISIBLE ══ */
[data-testid="stSidebar"] {
    background:#12121a !important;
    min-width:270px !important; max-width:360px !important;
    border-right:1px solid #2a2a3e !important;
}
[data-testid="stSidebarCollapseButton"],
[data-testid="collapsedControl"] { display:none !important; }
[data-testid="stSidebar"][aria-expanded="false"] {
    transform:none !important; min-width:270px !important;
    visibility:visible !important; margin-left:0 !important;
}
section[data-testid="stSidebarContent"] { padding:0 8px 0 4px !important; }

/* ══ SIDEBAR BUTTONS – DBeaver-style clean tree ══ */
[data-testid="stSidebar"] .stButton>button {
    width:100%; text-align:left !important;
    background:transparent !important; border:none !important;
    font-family:'Inter',sans-serif !important;
    font-size:0.8rem !important; padding:4px 8px !important;
    border-radius:5px; white-space:nowrap; overflow:hidden;
    text-overflow:ellipsis; cursor:pointer; line-height:1.7;
    transition:background .12s, color .12s;
    box-shadow:none !important;
    letter-spacing:0.01em;
    /* default = file color */
    color:#7c83a0 !important;
}
[data-testid="stSidebar"] .stButton>button:hover {
    background:#1d1d2e !important; color:#cdd6f4 !important;
}
[data-testid="stSidebar"] .stButton>button:focus {
    box-shadow:none !important; outline:none !important;
}
/* Active file */
.active-btn .stButton>button {
    background:#1a2744 !important; color:#89b4fa !important;
    border-left:3px solid #89b4fa !important; padding-left:5px !important;
}
/* Folder = brighter warm white, bold */
.tree-folder .stButton>button {
    color:#dde1f0 !important; font-weight:600 !important;
}
.tree-folder .stButton>button:hover {
    color:#ffffff !important;
}

/* ══ Search ══ */
[data-testid="stSidebar"] .stTextInput input {
    background:#1a1a28 !important; border:1px solid #2a2a3e !important;
    border-radius:6px !important; color:#cdd6f4 !important;
    font-size:0.78rem !important; font-family:'Inter',sans-serif !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder { color:#45475a !important; }
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color:#89b4fa !important; outline:none !important;
    box-shadow:0 0 0 2px rgba(137,180,250,.15) !important;
}

/* ══ Explorer title ══ */
.expl-title {
    font-size:.63rem; font-weight:700; letter-spacing:.14em;
    text-transform:uppercase; color:#45475a; padding:14px 10px 7px;
    border-bottom:1px solid #1e1e30; margin-bottom:4px;
    font-family:'Inter',sans-serif;
}

/* ══ PREVENT COPY on preview ══ */
#preview-zone, #preview-zone * {
    user-select:none !important; -webkit-user-select:none !important;
}

/* ══ Top bar ══ */
.top-bar {
    display:flex; align-items:center; gap:10px;
    padding:10px 18px; background:#12121a;
    border:1px solid #2a2a3e; border-radius:8px 8px 0 0;
}
.top-bar .filename {
    font-size:.9rem; font-weight:600; color:#cdd6f4;
    flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;
}
.badge {
    background:#1a1a28; color:#6c7086; font-size:.65rem;
    padding:2px 8px; border-radius:10px; border:1px solid #2a2a3e;
    font-family:'JetBrains Mono',monospace; text-transform:uppercase;
    letter-spacing:.06em; white-space:nowrap;
}
.ro-badge { background:#2d1f00; color:#f9e2af; border-color:#f9e2af44; }

/* ══ Preview pane ══ */
.preview-frame {
    background:#13131f; border:1px solid #2a2a3e; border-top:none;
    border-radius:0 0 8px 8px; padding:30px 46px;
    min-height:72vh; color:#cdd6f4; line-height:1.85;
    overflow:auto; font-size:.9rem;
}
.preview-frame h1{color:#89b4fa;font-size:1.6rem;border-bottom:1px solid #2a2a3e;padding-bottom:6px;margin-bottom:16px;}
.preview-frame h2{color:#cba6f7;font-size:1.25rem;}
.preview-frame h3{color:#89dceb;font-size:1.05rem;}
.preview-frame a {color:#89b4fa;pointer-events:none;text-decoration:none;}
.preview-frame strong{color:#f5c2e7;}
.preview-frame em{color:#a6e3a1;}
.preview-frame pre{background:#12121a;border:1px solid #2a2a3e;padding:14px 18px;border-radius:8px;overflow-x:auto;margin:14px 0;}
.preview-frame code{font-family:'JetBrains Mono',monospace;font-size:.82em;color:#a6e3a1;}
.preview-frame table{border-collapse:collapse;width:100%;font-size:.85rem;margin:12px 0;}
.preview-frame th{background:#1a1a28;color:#89b4fa;text-align:left;padding:8px 14px;border:1px solid #2a2a3e;}
.preview-frame td{padding:7px 14px;border:1px solid #2a2a3e;color:#cdd6f4;}
.preview-frame tr:nth-child(even) td{background:#12121a;}
.preview-frame img{max-width:100%;border-radius:6px;pointer-events:none;}
.preview-frame blockquote{border-left:3px solid #89b4fa;margin:0;padding:6px 18px;color:#a6adc8;font-style:italic;}
.preview-frame p{margin:10px 0;}
.preview-frame ul,.preview-frame ol{padding-left:22px;}
.preview-frame li{margin-bottom:4px;}

/* ══ PPTX slides ══ */
.slide-card{background:#1a1a28;border:1px solid #2a2a3e;border-radius:10px;padding:22px 28px;margin-bottom:16px;}
.slide-num{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#45475a;margin-bottom:10px;font-family:'JetBrains Mono',monospace;}
.slide-title{font-size:1.3rem;font-weight:600;color:#89b4fa;margin-bottom:8px;}
.slide-body{color:#cdd6f4;font-size:.87rem;line-height:1.75;}
.slide-body li{margin-bottom:4px;} .slide-body ul{padding-left:20px;}

/* ══ Streamlit chrome off ══ */
#MainMenu,footer,header{visibility:hidden;}
.stDeployButton,[data-testid="stToolbar"]{display:none;}
.main .block-container{padding-top:1rem!important;padding-bottom:1rem!important;max-width:100%!important;}

/* ══ Empty state ══ */
.empty-state{display:flex;flex-direction:column;align-items:center;justify-content:center;height:72vh;color:#2a2a3e;text-align:center;}
.empty-state .eicon{font-size:3.5rem;margin-bottom:14px;}
.empty-state h3{color:#45475a;font-weight:400;margin-bottom:6px;}
.empty-state p{font-size:.85rem;color:#313244;line-height:1.7;}
</style>

<script>
document.addEventListener('contextmenu', e => e.preventDefault());
document.addEventListener('keydown', function(e){
    const c = e.ctrlKey || e.metaKey;
    if(c && ['s','p','u','a'].includes(e.key.toLowerCase())){e.preventDefault();return false;}
    if(e.key==='F12'){e.preventDefault();return false;}
    if(c&&e.shiftKey&&e.key==='I'){e.preventDefault();return false;}
});
// Re-expand sidebar if accidentally collapsed
setInterval(()=>{
    const s=document.querySelector('[data-testid="stSidebar"]');
    if(s&&s.getAttribute('aria-expanded')==='false'){
        const b=document.querySelector('[data-testid="stSidebarCollapseButton"]');
        if(b)b.click();
    }
},700);
</script>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
FOLDER_ID        = os.getenv("GOOGLE_DRIVE_FOLDER_ID", "")
SCOPES           = ["https://www.googleapis.com/auth/drive.readonly"]
FOLDER_MIME      = "application/vnd.google-apps.folder"

def _ext(name: str) -> str:
    return name.rsplit(".", 1)[-1].lower() if "." in name else ""

# ── Plain-text emoji icons (safe for st.button labels) ──────
def file_emoji(mime: str, name: str) -> str:
    e = _ext(name)
    if mime == FOLDER_MIME:                            return "📁"
    if "presentation" in mime or e == "pptx":          return "📊"
    if "spreadsheet"  in mime or e in ("xlsx","xls"):  return "📗"
    if "document"     in mime or e == "docx":          return "📝"
    if mime == "application/pdf" or e == "pdf":        return "📕"
    if mime == "text/markdown"   or e == "md":         return "📋"
    if mime == "text/plain"      or e == "txt":        return "📄"
    if mime.startswith("image/") or e in ("png","jpg","jpeg","gif","webp","svg","bmp","ico"): return "🖼️"
    return "📄"

def file_label(mime: str) -> str:
    return {
        FOLDER_MIME: "Folder",
        "application/vnd.google-apps.document": "Google Doc",
        "application/vnd.google-apps.spreadsheet": "Google Sheet",
        "application/vnd.google-apps.presentation": "Google Slides",
        "application/pdf": "PDF", "text/plain": "Text",
        "text/markdown": "Markdown",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "DOCX",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": "XLSX",
        "application/vnd.openxmlformats-officedocument.presentationml.presentation": "PPTX",
    }.get(mime, "File")


# ─────────────────────────────────────────────
# DRIVE SERVICE
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def get_drive_service():
    """Build Drive service entirely from .env variables — no JSON file needed."""
    try:
        import json
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        # ── Option A: full JSON blob in one env var (easiest) ──
        json_blob = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
        if json_blob:
            info = json.loads(json_blob)
            creds = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES)
            return build("drive", "v3", credentials=creds)

        # ── Option B: individual fields in separate env vars ──
        required = {
            "type":                        os.getenv("GCP_TYPE", "service_account"),
            "project_id":                  os.getenv("GCP_PROJECT_ID", ""),
            "private_key_id":              os.getenv("GCP_PRIVATE_KEY_ID", ""),
            "private_key":                 os.getenv("GCP_PRIVATE_KEY", "").replace("\\n", "\n"),
            "client_email":                os.getenv("GCP_CLIENT_EMAIL", ""),
            "client_id":                   os.getenv("GCP_CLIENT_ID", ""),
            "auth_uri":                    "https://accounts.google.com/o/oauth2/auth",
            "token_uri":                   "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_x509_cert_url":        os.getenv("GCP_CLIENT_CERT_URL", ""),
        }
        missing = [k for k, v in required.items()
                   if not v and k not in ("type","auth_uri","token_uri","auth_provider_x509_cert_url")]
        if missing:
            st.error(f"❌ Missing .env vars: {', '.join(missing)}\n\n"
                     "Set either `GOOGLE_SERVICE_ACCOUNT_JSON` (full JSON) "
                     "or the individual `GCP_*` variables. See `.env.example`.")
            st.stop()

        creds = service_account.Credentials.from_service_account_info(
            required, scopes=SCOPES)
        return build("drive", "v3", credentials=creds)

    except Exception as e:
        st.error(f"❌ Drive auth failed: {e}")
        st.stop()


@st.cache_data(ttl=300, show_spinner=False)
def fetch_children(_service, folder_id: str) -> list:
    results, page_token = [], None
    while True:
        resp = _service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            fields="nextPageToken, files(id, name, mimeType)",
            pageToken=page_token, orderBy="folder,name", pageSize=1000,
        ).execute()
        results.extend(resp.get("files", []))
        page_token = resp.get("nextPageToken")
        if not page_token:
            break
    return results


@st.cache_data(ttl=600, show_spinner=False)
def fetch_file_content(_service, file_id: str, mime_type: str):
    """Always returns (tag: str, data: bytes). Handles every weird API response."""
    try:
        # ── Google native files → export as HTML ──
        if mime_type in (
            "application/vnd.google-apps.document",
            "application/vnd.google-apps.spreadsheet",
            "application/vnd.google-apps.presentation",
        ):
            raw = _service.files().export(
                fileId=file_id, mimeType="text/html").execute()
            return ("html", _to_bytes(raw))

        # ── Everything else → download raw bytes ──
        # IMPORTANT: Use .execute() directly — it returns bytes cleanly.
        # MediaIoBaseDownload wraps chunks in objects for large binary files
        # but causes [object Object] issues for plain text files.
        req = _service.files().get_media(fileId=file_id)
        content = req.execute()
        if isinstance(content, bytes):
            return (mime_type, content)
        if isinstance(content, str):
            return (mime_type, content.encode("utf-8"))
        # Fallback for very large files: stream via MediaIoBaseDownload
        from googleapiclient.http import MediaIoBaseDownload
        buf = io.BytesIO()
        dl  = MediaIoBaseDownload(buf, req)
        done = False
        while not done:
            _, done = dl.next_chunk()
        return (mime_type, buf.getvalue())

    except Exception as e:
        return ("error", str(e).encode("utf-8"))


def _to_bytes(raw) -> bytes:
    """Convert ANY API return type to clean bytes."""
    if isinstance(raw, bytes):
        return raw
    if isinstance(raw, bytearray):
        return bytes(raw)
    if isinstance(raw, str):
        return raw.encode("utf-8")
    # list / dict / other – convert via repr-safe join
    if isinstance(raw, list):
        # Flatten list of dicts/strings (rare Drive API edge case)
        parts = []
        for item in raw:
            if isinstance(item, dict):
                parts.append(item.get("text", item.get("content", str(item))))
            elif isinstance(item, (bytes, bytearray)):
                parts.append(item.decode("utf-8", errors="replace"))
            else:
                parts.append(str(item))
        return "\n".join(parts).encode("utf-8")
    return str(raw).encode("utf-8")


def _bytes_to_str(data) -> str:
    """Safely turn bytes / str / list / anything into a clean Python str."""
    if isinstance(data, (bytes, bytearray)):
        return data.decode("utf-8", errors="replace")
    if isinstance(data, str):
        return data
    if isinstance(data, list):
        parts = []
        for item in data:
            if isinstance(item, dict):
                parts.append(item.get("text", item.get("content", str(item))))
            elif isinstance(item, (bytes, bytearray)):
                parts.append(item.decode("utf-8", errors="replace"))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(data)


def sanitize_html(raw) -> str:
    s = _bytes_to_str(raw)
    s = re.sub(r'<a\s[^>]*>', '<a>', s)
    s = re.sub(r'<form[^>]*>.*?</form>', '', s, flags=re.DOTALL)
    s = re.sub(r'<script[^>]*>.*?</script>', '', s, flags=re.DOTALL)
    return s


# ─────────────────────────────────────────────
# KEYWORD REDACTION
# Removes all variations of "corvit" from any
# rendered content — plain text, HTML, code, etc.
# ─────────────────────────────────────────────
# Patterns to strip (case-insensitive):
#   corvit.com  /  www.corvit.com  /  corvit  / Corvit / CORVIT
_REDACT_PATTERNS = [
    r'https?://(?:www\.)?corvit\.com\S*',   # full URLs
    r'(?:www\.)?corvit\.com',               # domain
    r'\bcorvit\b',                           # standalone word
]
_REDACT_RE = re.compile(
    "|".join(_REDACT_PATTERNS), re.IGNORECASE
)

def redact(text: str) -> str:
    """Remove all corvit references from a string."""
    return _REDACT_RE.sub("", text)

def redact_bytes(data) -> bytes:
    """Redact from bytes/str/anything, return bytes."""
    s = _bytes_to_str(data)
    return redact(s).encode("utf-8")


# ─────────────────────────────────────────────
# PPTX → slide cards
# ─────────────────────────────────────────────
def render_pptx_html(data: bytes) -> str:
    try:
        from pptx import Presentation
        prs   = Presentation(io.BytesIO(data))
        total = len(prs.slides)
        cards = []
        for idx, slide in enumerate(prs.slides, 1):
            title_text, body_lines = "", []
            for shape in slide.shapes:
                if not shape.has_text_frame:
                    continue
                text = shape.text_frame.text.strip()
                if not text:
                    continue
                is_title = False
                try:
                    ph = shape.placeholder_format
                    if ph is not None and ph.idx in (0, 1):
                        is_title = True
                except Exception:
                    pass
                if is_title and not title_text:
                    title_text = text
                else:
                    for para in shape.text_frame.paragraphs:
                        line = para.text.strip()
                        if line:
                            body_lines.append(line)

            title_h = f'<div class="slide-title">{html_lib.escape(title_text)}</div>' if title_text else ""
            if body_lines:
                items   = "".join(f"<li>{html_lib.escape(l)}</li>" for l in body_lines)
                body_h  = f'<div class="slide-body"><ul>{items}</ul></div>'
            elif not title_text:
                body_h  = '<div class="slide-body" style="color:#45475a;font-style:italic">— empty slide —</div>'
            else:
                body_h  = ""

            cards.append(f"""
            <div class="slide-card">
                <div class="slide-num">Slide {idx} / {total}</div>
                {title_h}{body_h}
            </div>""")
        return "\n".join(cards) or "<p style='color:#585b70'>No slides.</p>"
    except ImportError:
        return "<p style='color:#f9e2af'>⚠️ Run <code>pip install python-pptx</code> to preview PPTX files.</p>"
    except Exception as e:
        return f"<p style='color:#f38ba8'>PPTX error: {html_lib.escape(str(e))}</p>"


# ─────────────────────────────────────────────
# SIDEBAR TREE  — DBeaver / IntelliJ style
#
# Rules:
#   • Labels are PLAIN TEXT only (no HTML tags — buttons render them literally)
#   • Indentation is embedded IN the label string using em-spaces (U+2003)
#     because use_container_width=True makes buttons fill the full sidebar
#     width regardless of any wrapper div margin, so CSS margin on divs
#     has no visual effect on button content.
#   • Folders: ▼/▶ toggle + bold bright color via .tree-folder CSS class
#   • Files: dimmer color, indented under their folder
# ─────────────────────────────────────────────

# Em-space (wider than regular space) used for visual indentation in labels
_EM = "\u2003"

def render_tree(service, folder_id: str, depth: int = 0):
    items     = fetch_children(service, folder_id)
    # Each depth level gets 2 em-spaces of indentation
    pad       = _EM * (depth * 2)

    for item in items:
        fid   = item["id"]
        name  = item["name"]
        mime  = item["mimeType"]
        emoji = file_emoji(mime, name)

        # ── FOLDER ──────────────────────────────────────────
        if mime == FOLDER_MIME:
            expanded = st.session_state.expanded.get(fid, False)
            arrow    = "▼" if expanded else "▶"
            label    = f"{pad}{arrow}  {emoji}  {name}"

            st.sidebar.markdown('<div class="tree-folder">', unsafe_allow_html=True)
            if st.sidebar.button(label, key=f"d_{fid}",
                                 use_container_width=True, help=name):
                st.session_state.expanded[fid] = not expanded
                st.rerun()
            st.sidebar.markdown("</div>", unsafe_allow_html=True)

            if expanded:
                render_tree(service, fid, depth + 1)

        # ── FILE ────────────────────────────────────────────
        else:
            is_active = st.session_state.get("selected_id") == fid
            # Extra em-space so files sit visually past the folder arrow
            label     = f"{pad}{_EM}   {emoji}  {name}"

            wrapper_cls = "active-btn" if is_active else ""
            st.sidebar.markdown(f'<div class="{wrapper_cls}">', unsafe_allow_html=True)
            if st.sidebar.button(label, key=f"f_{fid}",
                                 use_container_width=True, help=name):
                st.session_state.selected_id   = fid
                st.session_state.selected_name = name
                st.session_state.selected_mime = mime
                st.rerun()
            st.sidebar.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PREVIEW
# ─────────────────────────────────────────────
def render_preview(service, file_id: str, file_name: str, mime_type: str):
    lbl  = file_label(mime_type)
    ext  = _ext(file_name)
    icon = file_emoji(mime_type, file_name)

    st.markdown(f"""
    <div class="top-bar">
        <span class="filename">{icon} {html_lib.escape(file_name)}</span>
        <span class="badge">{lbl}</span>
        <span class="badge ro-badge">🔒 Read-only</span>
    </div>""", unsafe_allow_html=True)

    with st.spinner("Loading…"):
        content_type, data = fetch_file_content(service, file_id, mime_type)

    if content_type == "error":
        st.error(f"Could not load file: {_bytes_to_str(data)}")
        return

    st.markdown('<div id="preview-zone">', unsafe_allow_html=True)

    # ── Google native → HTML export ──────────────────
    if content_type == "html":
        body = redact(sanitize_html(data))
        st.markdown(f'<div class="preview-frame">{body}</div>', unsafe_allow_html=True)

    # ── PPTX ─────────────────────────────────────────
    elif (mime_type == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
          or ext == "pptx"):
        cards = render_pptx_html(data)
        cards = redact(cards)  # strip keyword from slide content
        # Must use components.html — st.markdown breaks when slide content
        # has &amp; entities or long HTML strings (only renders slide 1).
        import streamlit.components.v1 as components
        full_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
        *{{box-sizing:border-box;margin:0;padding:0;}}
        body{{background:#13131f;font-family:'Inter',sans-serif;padding:20px 24px;}}
        .slide-card{{background:#1a1a28;border:1px solid #2a2a3e;border-radius:10px;padding:22px 28px;margin-bottom:16px;}}
        .slide-num{{font-size:.62rem;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:#45475a;margin-bottom:10px;font-family:monospace;}}
        .slide-title{{font-size:1.3rem;font-weight:600;color:#89b4fa;margin-bottom:8px;}}
        .slide-body{{color:#cdd6f4;font-size:.88rem;line-height:1.75;}}
        .slide-body li{{margin-bottom:4px;list-style:disc;}} .slide-body ul{{padding-left:20px;}}
        .empty{{color:#45475a;font-style:italic;}}
        </style></head><body>{cards}</body></html>"""
        # Estimate height: ~120px per slide card
        try:
            from pptx import Presentation
            n_slides = len(Presentation(io.BytesIO(data)).slides)
        except Exception:
            n_slides = 10
        components.html(full_html, height=max(500, n_slides * 160), scrolling=True)

    # ── DOCX ─────────────────────────────────────────
    elif (mime_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
          or ext == "docx"):
        try:
            import mammoth
            result   = mammoth.convert_to_html(io.BytesIO(data))
            html_out = redact(sanitize_html(result.value))
            st.markdown(f'<div class="preview-frame">{html_out}</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(
                f'<div class="preview-frame"><p style="color:#f38ba8;">DOCX error: {e}</p></div>',
                unsafe_allow_html=True)

    # ── PDF ──────────────────────────────────────────
    elif mime_type == "application/pdf" or ext == "pdf":
        b64 = base64.b64encode(data).decode()
        st.markdown(f"""
        <div class="preview-frame" style="padding:0;overflow:hidden;">
            <iframe src="data:application/pdf;base64,{b64}#toolbar=0&navpanes=0&view=FitH"
                width="100%" height="820px" style="border:none;display:block;"></iframe>
        </div>""", unsafe_allow_html=True)

    # ── XLSX ─────────────────────────────────────────
    elif (mime_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          or ext in ("xlsx", "xls")):
        try:
            import openpyxl
            wb   = openpyxl.load_workbook(io.BytesIO(data), read_only=True, data_only=True)
            tabs = []
            for ws in wb.worksheets:
                rows  = list(ws.iter_rows(values_only=True))
                table = (f'<h3 style="color:#a6e3a1;margin:20px 0 8px;">'
                         f'📊 {html_lib.escape(ws.title)}</h3><table>')
                for i, row in enumerate(rows[:500]):
                    tag   = "th" if i == 0 else "td"
                    cells = "".join(
                        f"<{tag}>{html_lib.escape(str(c) if c is not None else '')}</{tag}>"
                        for c in row)
                    table += f"<tr>{cells}</tr>"
                table += "</table>"
                if len(rows) > 500:
                    table += (f"<p style='color:#585b70;font-size:.78rem'>"
                              f"…{len(rows)} rows total – showing first 500</p>")
                tabs.append(table)
            st.markdown(f'<div class="preview-frame">{"".join(tabs)}</div>',
                        unsafe_allow_html=True)
        except Exception as e:
            st.markdown(
                f'<div class="preview-frame"><p style="color:#f38ba8;">XLSX error: {e}</p></div>',
                unsafe_allow_html=True)

    # ── TXT / Markdown / CSV / code / Dockerfile / no-extension text ──
    elif (mime_type in ("text/plain", "text/markdown")
          or ext in ("txt","md","csv","json","yaml","yml","xml","toml",
                     "ini","sh","bash","py","js","ts","css",
                     "sql","log","rst","conf","env","tf","go","rs",
                     "java","cpp","c","rb","php","kt","swift","r")
          # Files with no extension that are always plain text
          or file_name in ("Dockerfile","Makefile","Jenkinsfile","Vagrantfile",
                           "Gemfile","Procfile","Pipfile",".gitignore",
                           ".dockerignore",".env",".editorconfig","nginx.conf")):
        # Use _bytes_to_str for maximum robustness against API quirks, then redact
        text = redact(_bytes_to_str(data))

        if ext == "md" or mime_type == "text/markdown":
            # Show raw .md content exactly as-is (same as .txt)
            st.markdown('<div style="border:1px solid #2a2a3e;border-radius:0 0 8px 8px;overflow:hidden;margin-top:0;">',
                        unsafe_allow_html=True)
            st.code(text, language="text")
            st.markdown('</div>', unsafe_allow_html=True)

        elif ext == "csv":
            import csv, io as _io
            rows  = list(csv.reader(_io.StringIO(text)))
            table = "<table>"
            for i, row in enumerate(rows[:300]):
                tag   = "th" if i == 0 else "td"
                cells = "".join(f"<{tag}>{html_lib.escape(c)}</{tag}>" for c in row)
                table += f"<tr>{cells}</tr>"
            table += "</table>"
            if len(rows) > 300:
                table += f"<p style='color:#585b70;font-size:.78rem'>…{len(rows)} rows – showing first 300</p>"
            st.markdown(f'<div class="preview-frame">{table}</div>', unsafe_allow_html=True)

        else:
            # ALL plain text and code files — st.code() is 100% reliable.
            # It never goes through the HTML pipeline so [object Object]
            # and special characters are impossible.
            lang_map = {
                "py":"python","js":"javascript","ts":"typescript","sh":"bash",
                "bash":"bash","yml":"yaml","yaml":"yaml","json":"json",
                "xml":"xml","sql":"sql","tf":"hcl","go":"go","rs":"rust",
                "java":"java","cpp":"cpp","c":"c","rb":"ruby","php":"php",
                "kt":"kotlin","swift":"swift","r":"r","html":"html","css":"css",
            }
            lang = lang_map.get(ext, "text")
            st.markdown('<div style="border:1px solid #2a2a3e;border-radius:0 0 8px 8px;overflow:hidden;margin-top:0;">',
                        unsafe_allow_html=True)
            st.code(text, language=lang)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── Images ───────────────────────────────────────
    elif (mime_type.startswith("image/")
          or ext in ("png","jpg","jpeg","gif","webp","bmp","ico")):
        # SVG — render in iframe (st.image doesn't support SVG)
        if ext == "svg" or mime_type == "image/svg+xml":
            import streamlit.components.v1 as components
            svg_str = _bytes_to_str(data)
            components.html(
                f'<div style="background:#13131f;display:flex;align-items:center;'
                f'justify-content:center;min-height:400px;padding:20px;">{svg_str}</div>',
                height=500, scrolling=True)
        else:
            st.markdown(
                '<div style="background:#13131f;border:1px solid #2a2a3e;'
                'border-radius:0 0 8px 8px;padding:24px;text-align:center;">',
                unsafe_allow_html=True)
            st.image(data, use_container_width=False)
            st.markdown('</div>', unsafe_allow_html=True)

    # ── HTML – render as live web page in sandboxed iframe ──────────
    elif ext == "html":
        import streamlit.components.v1 as components
        html_content = redact(_bytes_to_str(data))
        # Inject a base style to prevent white flash
        html_content = html_content.replace(
            "<head>", '<head><meta charset="utf-8">', 1
        ) if "<head>" in html_content else f'<meta charset="utf-8">{html_content}'
        st.markdown(
            '<p style="color:#45475a;font-size:.75rem;margin-bottom:4px;">'
            '🌐 Rendered live — HTML preview</p>',
            unsafe_allow_html=True)
        components.html(html_content, height=700, scrolling=True)

    # ── Fallback ─────────────────────────────────────
    else:
        st.markdown(f"""
        <div class="preview-frame">
            <div class="empty-state">
                <div class="eicon">🔍</div>
                <h3>Preview unavailable</h3>
                <p><strong>{html_lib.escape(lbl)}</strong> files can't be previewed inline.<br>
                Supported: Google Docs · Sheets · Slides · PDF · DOCX · XLSX · PPTX · TXT · MD · CSV · code</p>
            </div>
        </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────
for k, v in [("expanded",{}),("selected_id",None),
             ("selected_name",""),("selected_mime","")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
# GUARDS
# ─────────────────────────────────────────────
if not FOLDER_ID:
    st.error("⚠️  Set `GOOGLE_DRIVE_FOLDER_ID` in your `.env` file.")
    st.stop()

# ─────────────────────────────────────────────
# RENDER
# ─────────────────────────────────────────────
service = get_drive_service()

# ── SIDEBAR ──────────────────────────────────
with st.sidebar:
    st.markdown('<div class="expl-title">📁 &nbsp;Explorer</div>', unsafe_allow_html=True)

    search = st.text_input("s", placeholder="🔍  Search files…",
                           label_visibility="collapsed", key="search_box")
    st.markdown('<div style="height:3px;"></div>', unsafe_allow_html=True)

    if search.strip():
        try:
            safe_q = search.replace("'", "\\'")
            hits   = service.files().list(
                q=f"name contains '{safe_q}' and trashed=false",
                fields="files(id, name, mimeType)",
                pageSize=50,
            ).execute().get("files", [])
        except Exception:
            hits = []

        if hits:
            for item in hits:
                if item["mimeType"] == FOLDER_MIME:
                    continue
                icon     = file_emoji(item["mimeType"], item["name"])
                is_act   = st.session_state.selected_id == item["id"]
                label    = f"{icon} {item['name']}"
                if is_act:
                    st.sidebar.markdown('<div class="active-btn">', unsafe_allow_html=True)
                if st.sidebar.button(label, key=f"sr_{item['id']}",
                                     use_container_width=True, help=item["name"]):
                    st.session_state.selected_id   = item["id"]
                    st.session_state.selected_name = item["name"]
                    st.session_state.selected_mime = item["mimeType"]
                    st.rerun()
                if is_act:
                    st.sidebar.markdown("</div>", unsafe_allow_html=True)
        else:
            st.sidebar.caption("No results found.")
    else:
        render_tree(service, FOLDER_ID)


# ── MAIN PANE ────────────────────────────────
if st.session_state.selected_id:
    render_preview(
        service,
        st.session_state.selected_id,
        st.session_state.selected_name,
        st.session_state.selected_mime,
    )
else:
    st.markdown("""
    <div class="empty-state">
        <div class="eicon">📂</div>
        <h3>Drive Viewer</h3>
        <p>Select a file from the explorer on the left to preview it here.<br>
        All files are <strong style="color:#f9e2af;">read-only</strong> —
        downloading is disabled.</p>
    </div>""", unsafe_allow_html=True)