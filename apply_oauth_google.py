#!/usr/bin/env python3
"""
Apply Sprint B.1.6 — bouton "Continuer avec Google" dans la modal Auth.

Idempotent: refuses to run if patch already applied.
Verifies each anchor matches exactly once before replacing.
"""
import sys
from pathlib import Path

p = Path("index.html")
if not p.exists():
    sys.exit("ERROR: index.html introuvable. Lance ce script depuis ~/Code/autoradar/frontend/")

content = p.read_text()

# Pre-req: les patches Auth (5.1-5.4) doivent être déjà appliqués
if 'id="authModal"' not in content:
    sys.exit(
        "ERROR: la modal Auth (#authModal) n'est pas trouvée dans index.html.\n"
        "       Applique d'abord apply_auth_patches.py avant ce script."
    )

# Idempotence guard
if "signInWithGoogle" in content:
    sys.exit(
        "ERROR: signInWithGoogle déjà présent dans index.html.\n"
        "       Si tu veux relancer ce script, fais d'abord :\n"
        "       git reset --hard HEAD~1 && git push --force-with-lease"
    )


def apply_patch(name, content, anchor, replacement, mode="prepend"):
    """mode: 'prepend' | 'append' (insert before/after anchor) | 'replace'."""
    n = content.count(anchor)
    if n != 1:
        sys.exit(f"ERROR Patch {name}: ancre trouvée {n} fois (attendu 1). Abort.")
    if mode == "prepend":
        return content.replace(anchor, replacement + anchor)
    elif mode == "append":
        return content.replace(anchor, anchor + replacement)
    elif mode == "replace":
        return content.replace(anchor, replacement)
    else:
        sys.exit(f"Bad mode: {mode}")


# ============================================================
# Patch 1 — Bouton Google + séparateur "ou" dans la modal
# Inséré entre le bouton magic link et le div d'erreur
# ============================================================
ANCHOR_HTML = '              onclick="sendMagicLink()">Recevoir le lien</button>\n'

GOOGLE_BTN = '''
      <!-- ── OU continuer avec Google ── -->
      <div style="display:flex;align-items:center;gap:10px;margin:14px 0">
        <div style="flex:1;height:1px;background:var(--border)"></div>
        <span style="font-size:10px;color:var(--text3);font-family:var(--sans);text-transform:uppercase;letter-spacing:0.08em">ou</span>
        <div style="flex:1;height:1px;background:var(--border)"></div>
      </div>

      <button onclick="signInWithGoogle()"
              style="width:100%;padding:10px 14px;background:var(--bg);color:var(--text);border:1px solid var(--border2);border-radius:var(--rsm);font-size:13px;cursor:pointer;font-family:var(--sans);font-weight:500;display:flex;align-items:center;justify-content:center;gap:10px">
        <svg width="16" height="16" viewBox="0 0 18 18" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <path fill="#4285F4" d="M16.51 8H8.98v3h4.3c-.18 1-.74 1.48-1.6 2.04v2.01h2.6a7.8 7.8 0 0 0 2.38-5.88c0-.57-.05-.66-.15-1.18z"/>
          <path fill="#34A853" d="M8.98 17c2.16 0 3.97-.72 5.3-1.94l-2.6-2.04a4.8 4.8 0 0 1-7.18-2.54H1.83v2.07A8 8 0 0 0 8.98 17z"/>
          <path fill="#FBBC05" d="M4.5 10.48a4.8 4.8 0 0 1 0-3.04V5.37H1.83a8 8 0 0 0 0 7.18l2.67-2.07z"/>
          <path fill="#EA4335" d="M8.98 4.18c1.17 0 2.23.4 3.06 1.2l2.3-2.3A8 8 0 0 0 1.83 5.37L4.5 7.44a4.77 4.77 0 0 1 4.48-3.26z"/>
        </svg>
        Continuer avec Google
      </button>
'''

content = apply_patch("1 (Bouton Google HTML)", content, ANCHOR_HTML, GOOGLE_BTN, mode="append")
print("✓ Patch 1 — Bouton Google inséré dans la modal")


# ============================================================
# Patch 2 — Handler JS signInWithGoogle, ajouté après signOut
# ============================================================
ANCHOR_JS = '''async function signOut() {
  if (!_sb) return;
  await _sb.auth.signOut();
  if (typeof showToast === 'function') showToast('Déconnecté');
}'''

GOOGLE_HANDLER = '''

async function signInWithGoogle() {
  if (!_sb) { showAuthError('Connexion DB indisponible'); return; }
  const { error } = await _sb.auth.signInWithOAuth({
    provider: 'google',
    options: { redirectTo: window.location.origin }
  });
  if (error) {
    showAuthError(error.message || 'Erreur OAuth Google — réessayez');
  }
  // Si OK : redirection automatique vers Google → callback Supabase → SIGNED_IN
}'''

content = apply_patch("2 (Handler signInWithGoogle)", content, ANCHOR_JS, GOOGLE_HANDLER, mode="append")
print("✓ Patch 2 — Handler signInWithGoogle injecté")


# Write
p.write_text(content)
print()
print("✅ OAuth Google ajouté à la modal Auth.")
print("   Vérifie avec : git diff index.html | head -60")
print("   Puis commit + push.")
