#!/usr/bin/env python3
"""
Apply Sprint B.1 magic-link UI patches to index.html.

Idempotent: refuses to run if patches already applied.
Verifies each anchor matches exactly once before replacing.
"""
import sys
from pathlib import Path

p = Path("index.html")
if not p.exists():
    sys.exit("ERROR: index.html introuvable. Lance ce script depuis ~/Code/autoradar/frontend/")

content = p.read_text()

# Idempotence guard
if 'id="authModal"' in content:
    sys.exit(
        "ERROR: 'authModal' déjà présent dans index.html.\n"
        "       Si tu veux relancer le script, fais d'abord :\n"
        "       git reset --hard HEAD~1 && git push --force-with-lease"
    )


def apply_patch(name, content, anchor, replacement, mode="prepend"):
    """mode: 'prepend' (insert before anchor) or 'replace' (replace anchor)."""
    n = content.count(anchor)
    if n != 1:
        sys.exit(f"ERROR Patch {name}: ancre trouvée {n} fois (attendu 1). Abort.")
    if mode == "prepend":
        return content.replace(anchor, replacement + anchor)
    elif mode == "replace":
        return content.replace(anchor, replacement)
    else:
        sys.exit(f"Bad mode: {mode}")


# ============================================================
# Patch 1 — Modal HTML (insertion avant la modal paywall)
# ============================================================
ANCHOR1 = '<div id="paywall" class="pw-overlay" style="display:none"'

MODAL_HTML = '''<!-- ═══════════════════════════════════════════════
     AUTH MODAL — Magic link via Supabase
═══════════════════════════════════════════════ -->
<div id="authModal" class="pw-overlay" style="display:none" onclick="if(event.target===this)closeAuthModal()">
  <div class="pw-screen" style="max-width:380px;padding:24px 26px">

    <!-- État 1 : email -->
    <div id="auth-s1">
      <div class="pw-head" style="margin-bottom:6px">
        <div class="pw-logo"><span class="ar-dot"></span>Carnet</div>
        <button class="pw-close" onclick="closeAuthModal()">×</button>
      </div>

      <div style="text-align:center;padding:18px 0 22px">
        <div style="font-size:16px;font-weight:500;color:var(--text);margin-bottom:6px">Se connecter</div>
        <div style="font-size:12px;color:var(--text2);line-height:1.5">
          Entrez votre adresse email — vous recevrez un lien de connexion.<br>
          <span style="color:var(--text3)">Pas encore de compte ? Il sera créé.</span>
        </div>
      </div>

      <input id="auth-email" type="email" autocomplete="email" placeholder="vous@email.com"
             style="width:100%;padding:11px 14px;border:1px solid var(--border2);border-radius:var(--rsm);font-family:var(--sans);font-size:13px;color:var(--text);background:var(--bg);box-sizing:border-box;margin-bottom:10px"
             onkeydown="if(event.key==='Enter')sendMagicLink()" />

      <button id="auth-send-btn"
              style="width:100%;padding:11px 18px;background:var(--gc);color:#fff;border:none;border-radius:var(--rsm);font-size:13px;cursor:pointer;font-family:var(--sans);font-weight:500"
              onclick="sendMagicLink()">Recevoir le lien</button>

      <div id="auth-error" style="display:none;margin-top:10px;padding:8px 12px;background:#FFF1F0;color:#B0413E;border:1px solid #F5C6CB;border-radius:var(--rsm);font-size:11px"></div>
    </div>

    <!-- État 2 : lien envoyé -->
    <div id="auth-s2" style="display:none;text-align:center;padding:14px 0">
      <div style="font-size:30px;margin-bottom:8px">✉</div>
      <div style="font-size:15px;font-weight:500;color:var(--text);margin-bottom:6px">Lien envoyé</div>
      <div style="font-size:12px;color:var(--text2);line-height:1.5;margin-bottom:16px">
        Vérifiez votre boîte mail à<br>
        <strong id="auth-sent-to" style="color:var(--text)"></strong><br>
        <span style="color:var(--text3)">Pensez aussi au dossier spam.</span>
      </div>
      <button onclick="closeAuthModal()"
              style="padding:8px 18px;background:none;border:1px solid var(--border2);border-radius:var(--rsm);font-size:12px;color:var(--text2);cursor:pointer;font-family:var(--sans)">Fermer</button>
    </div>

  </div>
</div>

'''

content = apply_patch("1 (Modal HTML)", content, ANCHOR1, MODAL_HTML, mode="prepend")
print("✓ Patch 1 — Modal HTML inséré")


# ============================================================
# Patch 2 — Bouton login dans header
# ============================================================
ANCHOR2 = '<div id="donor-badge-wrap" class="ar-badge-wrap" style="display:none" onclick="openLeaderboard()">'

HEADER_BTN = '''<!-- AUTH SLOT -->
    <button id="auth-login-btn" class="ar-don-btn" onclick="openAuthModal()" style="display:none">Connexion</button>
    <div id="auth-user-menu" style="display:none;align-items:center;gap:6px">
      <span id="auth-user-label" style="font-size:12px;color:var(--text2);font-family:var(--sans);max-width:140px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"></span>
      <button onclick="signOut()" style="font-size:11px;padding:4px 10px;background:none;border:1px solid var(--border2);border-radius:var(--rsm);color:var(--text3);cursor:pointer;font-family:var(--sans)">Déconnexion</button>
    </div>
    '''

content = apply_patch("2 (Bouton header)", content, ANCHOR2, HEADER_BTN, mode="prepend")
print("✓ Patch 2 — Bouton header inséré")


# ============================================================
# Patch 3 — Handlers JS + hook updateAuthUI dans getUser
# Replace 2 lignes (ligne getUser + } qui ferme if(_sb)) par un bloc enrichi
# ============================================================
OLD3 = '''  _sb.auth.getUser().then(({ data }) => { currentUser = data?.user || null; });
}'''

NEW3 = '''  _sb.auth.getUser().then(({ data }) => { currentUser = data?.user || null; updateAuthUI(); });
}

/* ── Auth UI handlers ── */
function openAuthModal() {
  document.getElementById('auth-s1').style.display = 'block';
  document.getElementById('auth-s2').style.display = 'none';
  document.getElementById('auth-error').style.display = 'none';
  document.getElementById('auth-email').value = '';
  document.getElementById('authModal').style.display = 'flex';
  setTimeout(() => document.getElementById('auth-email').focus(), 50);
}

function closeAuthModal() {
  document.getElementById('authModal').style.display = 'none';
}

function showAuthError(msg) {
  const el = document.getElementById('auth-error');
  el.textContent = msg;
  el.style.display = 'block';
}

async function sendMagicLink() {
  if (!_sb) { showAuthError('Connexion DB indisponible'); return; }
  const email = document.getElementById('auth-email').value.trim().toLowerCase();
  if (!email || !/^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(email)) {
    showAuthError('Adresse email invalide');
    return;
  }
  const btn = document.getElementById('auth-send-btn');
  btn.disabled = true; btn.textContent = 'Envoi…';

  const { error } = await _sb.auth.signInWithOtp({
    email,
    options: { emailRedirectTo: window.location.origin }
  });

  btn.disabled = false; btn.textContent = 'Recevoir le lien';

  if (error) {
    showAuthError(error.message || 'Erreur — réessayez dans un instant');
    return;
  }
  document.getElementById('auth-sent-to').textContent = email;
  document.getElementById('auth-s1').style.display = 'none';
  document.getElementById('auth-s2').style.display = 'block';
}

async function signOut() {
  if (!_sb) return;
  await _sb.auth.signOut();
  if (typeof showToast === 'function') showToast('Déconnecté');
}

function updateAuthUI() {
  const loginBtn = document.getElementById('auth-login-btn');
  const userMenu = document.getElementById('auth-user-menu');
  const userLabel = document.getElementById('auth-user-label');
  if (!loginBtn || !userMenu) return;
  if (currentUser) {
    loginBtn.style.display = 'none';
    userMenu.style.display = 'inline-flex';
    const display = currentUser.user_metadata?.display_name
                  || currentUser.email?.split('@')[0]
                  || 'Membre';
    userLabel.textContent = display;
    userLabel.title = currentUser.email || '';
  } else {
    loginBtn.style.display = 'inline-block';
    userMenu.style.display = 'none';
  }
}'''

content = apply_patch("3 (Handlers JS)", content, OLD3, NEW3, mode="replace")
print("✓ Patch 3 — Handlers JS injectés")


# ============================================================
# Patch 4 — Hook updateAuthUI dans onAuthStateChange
# ============================================================
OLD4 = '''    currentUser = session?.user || null;
    if (event === 'SIGNED_IN') {'''

NEW4 = '''    currentUser = session?.user || null;
    updateAuthUI();
    if (event === 'SIGNED_IN') {'''

content = apply_patch("4 (Hook onAuthStateChange)", content, OLD4, NEW4, mode="replace")
print("✓ Patch 4 — Hook updateAuthUI dans onAuthStateChange")


# Write
p.write_text(content)
print()
print("✅ Tous les patches appliqués proprement à index.html")
print("   Vérifie avec : git diff index.html | head -80")
print("   Puis commit + push.")
