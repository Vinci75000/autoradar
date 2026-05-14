#!/usr/bin/env python3
"""
CARNET · Lot 10 (Phase α) — Page Security

Source        : Création d'une nouvelle page standalone security.html
                (politique de sécurité Year -1) + lien dans menu user
                dropdown d'index.html.

Scope         : Politique de sécurité publique d'une asso loi 1901.
                9 sections :
                  1. Approche défense en profondeur
                  2. Authentification
                  3. Hébergement & chiffrement
                  4. Wallets & paiements
                  5. Données utilisateur (RLS, JWT)
                  6. Audit & monitoring
                  7. Divulgation responsable
                  8. Dépendances majeures
                  9. Incidents & notification

Hors scope    : SBOM complet (Year 1)
                Bug bounty rémunéré (asso non lucrative, pas le budget)
                Certification ISO 27001 (Year 2+)

Pipeline du script (pattern Lot 9) :
  - Étape A : créer/mettre à jour security.html (idempotence md5)
  - Étape B : patcher index.html pour ajouter lien menu user

Prérequis : Lot 9 (Phase α) appliqué
Usage     :
    python3 apply_security_lot10.py path/to/index.html
    python3 apply_security_lot10.py path/to/index.html --dry-run
"""

import sys
import hashlib
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, _Style


# ═══════════════════════════════════════════════════════════════════════
# PARTIE A — Contenu du fichier security.html
# ═══════════════════════════════════════════════════════════════════════

SECURITY_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CARNET · Sécurité · politique et stack technique</title>
  <meta name="description" content="Politique de sécurité CARNET — comment vos données et vos transactions sont protégées, et comment nous divulguer une vulnérabilité.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@1,400;1,500;1,600&family=Cormorant+Garamond:ital,wght@1,400;1,500;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="carnet-tokens.css">
  <style>
    body { margin: 0; font-family: var(--sans); background: var(--papier); color: var(--encre); line-height: 1.5; -webkit-font-smoothing: antialiased; }
    a { color: var(--orange-polo); text-decoration: none; }
    a:hover { text-decoration: underline; text-underline-offset: 3px; }
    .topbar { padding: 14px 22px; border-bottom: 1px solid var(--gris-line); display: flex; justify-content: space-between; align-items: center; background: var(--papier); position: sticky; top: 0; z-index: 5; }
    .topbar-wordmark { display: flex; gap: 7px; align-items: baseline; }
    .topbar-dot { width: 7px; height: 7px; background: var(--orange-polo); border-radius: 1px; display: inline-block; }
    .topbar-name { font-family: var(--display); font-style: italic; font-size: 18px; color: var(--encre); }
    .topbar-back { font-family: var(--mono); font-size: 10px; letter-spacing: 0.14em; color: var(--gris); text-transform: uppercase; }
    .topbar-back:hover { color: var(--orange-polo); }
    .ed-nav { display: flex; gap: 22px; padding: 10px 22px; border-bottom: 1px solid var(--gris-line); overflow-x: auto; -webkit-overflow-scrolling: touch; }
    .ed-nav a { font-family: var(--mono); font-size: 10px; letter-spacing: 0.16em; text-transform: uppercase; color: var(--gris); white-space: nowrap; }
    .ed-nav a.is-active { color: var(--encre); }
    .ed-nav a:hover { color: var(--orange-polo); }
    main { max-width: 700px; margin: 0 auto; padding: 40px 22px 80px; }
    .hero-eyebrow { font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; color: var(--gris); text-transform: uppercase; margin: 0 0 12px 0; }
    h1 { font-family: var(--display); font-style: italic; font-weight: 500; font-size: 48px; line-height: 0.95; letter-spacing: -0.015em; margin: 0 0 16px 0; color: var(--encre); }
    .hero-sub { font-family: var(--editorial); font-style: italic; font-size: 17px; line-height: 1.5; color: var(--encre-soft); margin: 0 0 28px 0; }
    .hero-meta { font-family: var(--mono); font-size: 10px; letter-spacing: 0.12em; color: var(--gris); text-transform: uppercase; margin: 0; }
    .toc { margin: 32px 0 40px; padding: 20px 22px; background: #FAFAF7; border: 1px solid var(--gris-line); border-radius: var(--r); }
    .toc-title { font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; color: var(--gris); text-transform: uppercase; margin: 0 0 12px 0; }
    .toc ol { list-style: none; counter-reset: toc; padding: 0; margin: 0; column-count: 1; }
    @media (min-width: 600px) { .toc ol { column-count: 2; column-gap: 28px; } }
    .toc li { counter-increment: toc; padding: 4px 0; font-family: var(--editorial); font-style: italic; font-size: 15px; break-inside: avoid; }
    .toc li::before { content: counter(toc, decimal-leading-zero) ". "; font-family: var(--mono); font-style: normal; font-size: 11px; color: var(--orange-polo); margin-right: 6px; }
    .toc li a { color: var(--encre); }
    .toc li a:hover { color: var(--orange-polo); text-decoration: none; }
    section { margin: 0 0 40px 0; scroll-margin-top: 90px; }
    .section-eyebrow { font-family: var(--mono); font-size: 10px; letter-spacing: 0.2em; color: var(--orange-polo); text-transform: uppercase; margin: 0 0 8px 0; }
    h2 { font-family: var(--display); font-style: italic; font-weight: 500; font-size: 28px; line-height: 1.1; letter-spacing: -0.01em; margin: 0 0 14px 0; color: var(--encre); }
    section p { font-size: 15px; line-height: 1.65; color: var(--encre-soft); margin: 0 0 14px 0; }
    section p strong { color: var(--encre); font-weight: 600; }
    section ul { padding-left: 0; list-style: none; margin: 0 0 14px 0; }
    section ul li { position: relative; padding: 6px 0 6px 22px; font-size: 15px; line-height: 1.55; color: var(--encre-soft); }
    section ul li::before { content: "·"; position: absolute; left: 8px; top: 6px; font-family: var(--mono); color: var(--orange-polo); }
    section ul li strong { color: var(--encre); font-weight: 600; }
    .callout { padding: 16px 18px; background: #FAFAF7; border-left: 3px solid var(--vert-anglais); border-radius: var(--r); margin: 14px 0; }
    .callout.is-warning { border-left-color: var(--orange-polo); }
    .callout p { margin: 0; font-family: var(--editorial); font-style: italic; font-size: 14px; color: var(--encre); }
    code { font-family: var(--mono); font-size: 13px; background: #FAFAF7; padding: 1px 5px; border-radius: 2px; }
    footer { max-width: 700px; margin: 60px auto 0; padding: 32px 22px 80px; border-top: 1px solid var(--gris-line); }
    .footer-meta { font-family: var(--mono); font-size: 10px; letter-spacing: 0.08em; color: var(--gris); margin: 0 0 6px 0; }
    .footer-contact { font-family: var(--editorial); font-style: italic; font-size: 15px; color: var(--encre-soft); margin: 0; }
    .footer-contact a { color: var(--encre); border-bottom: 1px solid var(--gris-line); padding-bottom: 1px; }
    .footer-contact a:hover { color: var(--orange-polo); border-bottom-color: var(--orange-polo); }
    @media (min-width: 600px) { h1 { font-size: 60px; } h2 { font-size: 32px; } main { padding: 60px 32px 100px; } }
  </style>
</head>
<body>

<header class="topbar">
  <a href="index.html" class="topbar-wordmark" style="text-decoration:none;">
    <span class="topbar-dot"></span>
    <span class="topbar-name">CARNET</span>
  </a>
  <a href="index.html" class="topbar-back">← retour</a>
</header>

<nav class="ed-nav" aria-label="Navigation éditoriale">
  <a href="discover.html">Discover</a>
  <a href="archetypes.html">Archétypes</a>
  <a href="launch.html">14·12·2026</a>
  <a href="about.html">About</a>
</nav>

<main>

  <p class="hero-eyebrow">Politique de sécurité</p>
  <h1><em>Solide par défaut.</em></h1>
  <p class="hero-sub">CARNET tient le carnet de bord de voitures qui valent parfois plus que la maison. Nous prenons la sécurité au sérieux — voici comment, et comment nous signaler une faille si vous en trouvez une.</p>
  <p class="hero-meta">Version 1.0 · 14 mai 2026</p>

  <div class="toc">
    <p class="toc-title">Sommaire</p>
    <ol>
      <li><a href="#section-1">Notre approche</a></li>
      <li><a href="#section-2">Authentification</a></li>
      <li><a href="#section-3">Hébergement et chiffrement</a></li>
      <li><a href="#section-4">Wallets et paiements</a></li>
      <li><a href="#section-5">Données utilisateur</a></li>
      <li><a href="#section-6">Audit et monitoring</a></li>
      <li><a href="#section-7">Divulgation responsable</a></li>
      <li><a href="#section-8">Dépendances majeures</a></li>
      <li><a href="#section-9">Incidents</a></li>
    </ol>
  </div>

  <section id="section-1">
    <p class="section-eyebrow">01 · Principes</p>
    <h2>Notre approche.</h2>
    <p>CARNET applique la défense en profondeur : <strong>minimum de données collectées</strong>, <strong>chiffrement systématique</strong>, <strong>sous-traitants sélectionnés pour leur conformité</strong>, et <strong>code review systématique</strong> sur tout ce qui touche aux identifiants ou aux paiements.</p>
    <p>Nous ne sommes pas une grande entreprise avec une équipe sécurité dédiée. Nous sommes une association loi 1901 avec des bénévoles attentifs. Nous compensons en gardant la surface d'attaque petite et en publiant ce qu'on fait.</p>
  </section>

  <section id="section-2">
    <p class="section-eyebrow">02 · Auth</p>
    <h2>Authentification.</h2>
    <p>La connexion à CARNET passe par <strong>Supabase Auth</strong>, l'un des standards de l'industrie pour les applications modernes.</p>
    <ul>
      <li><strong>Magic link</strong> (lien à usage unique envoyé par email) — pas de mot de passe à retenir, pas de mot de passe à voler.</li>
      <li><strong>OAuth Google</strong> — délégation à Google pour l'authentification.</li>
      <li><strong>Mots de passe</strong> (optionnel) — stockés sous forme d'empreinte cryptographique (bcrypt) côté Supabase, jamais en clair.</li>
      <li><strong>Sessions</strong> — tokens JWT signés, durée limitée, rafraîchissement explicite.</li>
      <li><strong>Pas de 2FA</strong> à ce stade — sur la roadmap pour Year 1 (TOTP).</li>
    </ul>
  </section>

  <section id="section-3">
    <p class="section-eyebrow">03 · Infra</p>
    <h2>Hébergement et chiffrement.</h2>
    <ul>
      <li><strong>Base de données</strong> : Supabase (PostgreSQL) hébergé à Frankfurt, Allemagne. Chiffrement TLS 1.3 en transit, AES-256 au repos. Backups chiffrés rolling 35 jours.</li>
      <li><strong>Frontend</strong> : Vercel (USA). Static assets servis via CDN, HSTS, CSP basique en place.</li>
      <li><strong>Photos</strong> : Cloudflare R2 (USA) via Cloudflare Worker proxy (carnet-photos-proxy). Cache 1 an, URLs signées non requis (les photos sont publiques par design pour le proxy d'annonces, vos photos personnelles de garage restent privées via RLS Supabase).</li>
      <li><strong>Paiements</strong> : Cloudflare Worker (carnet-payements) qui orchestre Xaman pour la signature XRPL. Aucune clé privée n'est jamais détenue par CARNET.</li>
    </ul>
    <div class="callout">
      <p>Toutes les communications client ↔ serveur passent en HTTPS exclusivement. Aucun accès en HTTP non chiffré n'est servi.</p>
    </div>
  </section>

  <section id="section-4">
    <p class="section-eyebrow">04 · Paiements</p>
    <h2>Wallets et paiements.</h2>
    <p>CARNET ne touche <strong>jamais</strong> aux clés privées de vos wallets. Les signatures de transactions XRPL passent par <strong>Xaman</strong> (application wallet dédiée XRPL, gérée par xrpl-labs aux Pays-Bas) :</p>
    <ul>
      <li>CARNET prépare la transaction (montant, destinataire, mémo).</li>
      <li>Xaman vous présente la transaction et vous la signez avec vos clés (chez vous, sur votre appareil).</li>
      <li>CARNET reçoit la confirmation de la transaction signée par le ledger XRPL.</li>
    </ul>
    <p>Le wallet officiel CARNET pour les donations et royalties NFT XLS-20 est <code>rJBhnYvg5kq9PgWFZziEXu2EcdJfcq8WSU</code>. Son activité est <strong>publique et auditable</strong> sur le ledger XRPL — voir la page <a href="transparency.html">Transparence</a>.</p>
  </section>

  <section id="section-5">
    <p class="section-eyebrow">05 · Données</p>
    <h2>Données utilisateur.</h2>
    <ul>
      <li><strong>Row-Level Security (RLS)</strong> : Supabase applique des règles RLS sur chaque table. Vous ne voyez que vos propres données — c'est garanti par la base elle-même, pas seulement par le code applicatif.</li>
      <li><strong>JWT sur chaque requête</strong> : chaque appel API porte un token JWT signé. Pas de token, pas de réponse.</li>
      <li><strong>Pas de stockage côté client de données sensibles</strong> : aucun mot de passe, aucune clé wallet, aucune information bancaire en localStorage ou cookie.</li>
      <li><strong>Effacement</strong> : sur demande à <a href="mailto:auth@carnet.life">auth@carnet.life</a>, votre compte et vos données sont effacés sous 30 jours (sauf obligations légales — voir Privacy).</li>
    </ul>
  </section>

  <section id="section-6">
    <p class="section-eyebrow">06 · Monitoring</p>
    <h2>Audit et monitoring.</h2>
    <p>Nous gardons des logs techniques pour détecter les comportements anormaux :</p>
    <ul>
      <li><strong>Logs d'authentification</strong> : tentatives de connexion, IP source, user-agent. Conservés 90 jours.</li>
      <li><strong>Logs applicatifs</strong> : requêtes API, erreurs, temps de réponse. Conservés 90 jours.</li>
      <li><strong>Logs paiements</strong> : préparation de transaction, succès, échec. Conservés 10 ans (obligation comptable asso).</li>
      <li><strong>Alertes</strong> : tentatives de brute-force, requêtes anormales, taux d'erreur 5xx.</li>
    </ul>
    <p>Nous ne pratiquons <strong>pas</strong> de tracking publicitaire, ni d'analytics tierces (pas de Google Analytics, pas de Facebook Pixel). Voir la page <a href="privacy.html">Confidentialité</a>.</p>
  </section>

  <section id="section-7">
    <p class="section-eyebrow">07 · Disclosure</p>
    <h2>Divulgation responsable.</h2>
    <p>Si vous trouvez une vulnérabilité dans CARNET (le site, l'API, les Workers, les NFT XLS-20, n'importe quoi de relié à carnet.life), <strong>nous voulons le savoir</strong>.</p>
    <ul>
      <li><strong>Écrivez à</strong> <a href="mailto:auth@carnet.life">auth@carnet.life</a> avec [SECURITY] en sujet.</li>
      <li><strong>Décrivez la vulnérabilité</strong> avec autant de détails techniques que possible (PoC apprécié).</li>
      <li><strong>Donnez-nous 90 jours</strong> pour réparer avant publication. Si la vulnérabilité est critique et activement exploitée, on coordonne.</li>
      <li><strong>Pas de bug bounty rémunéré</strong> à ce stade (asso non lucrative, pas le budget). Mais reconnaissance publique sur cette page si vous le souhaitez, et notre gratitude sincère.</li>
    </ul>
    <div class="callout is-warning">
      <p>Ce qui est <strong>hors scope</strong> : DDoS sur les sous-traitants tiers, vulnérabilités sociales (phishing nos utilisateurs), tests destructifs sur la prod. Pour ces sujets, signalez d'abord, on regarde ensemble.</p>
    </div>
  </section>

  <section id="section-8">
    <p class="section-eyebrow">08 · Stack</p>
    <h2>Dépendances majeures.</h2>
    <p>Les briques techniques de CARNET, dans l'ordre d'exposition :</p>
    <ul>
      <li><strong>Vercel</strong> — hébergement frontend, CDN.</li>
      <li><strong>Supabase</strong> — base PostgreSQL, Auth, Storage R2-compatible (Frankfurt).</li>
      <li><strong>Cloudflare</strong> — Workers (paiements + photos proxy), R2 (stockage photos), CDN.</li>
      <li><strong>Anthropic</strong> — API Claude pour le scoring archétype et l'extraction LLM d'annonces.</li>
      <li><strong>Xaman / xrpl-labs</strong> — signature wallet XRPL.</li>
      <li><strong>XRPL Foundation</strong> — ledger décentralisé pour donations RLUSD et NFT XLS-20 (royalties 1,7%).</li>
    </ul>
    <p>Nous suivons les bulletins CVE des dépendances principales et appliquons les mises à jour de sécurité dans la semaine quand elles sont critiques.</p>
  </section>

  <section id="section-9">
    <p class="section-eyebrow">09 · Incident</p>
    <h2>Incidents.</h2>
    <p>En cas de fuite de données ou d'incident affectant la sécurité de vos données personnelles, nous nous engageons à :</p>
    <ul>
      <li><strong>Notifier la CNIL</strong> dans les 72 heures, conformément à l'article 33 du RGPD.</li>
      <li><strong>Vous notifier directement</strong> si l'incident peut représenter un risque élevé pour vos droits (article 34 du RGPD).</li>
      <li><strong>Publier un post-mortem</strong> public sur cette page une fois l'incident résolu et les correctifs déployés, dans un délai raisonnable.</li>
    </ul>
    <p>À ce jour, aucun incident à signaler.</p>
  </section>

</main>

<footer>
  <p class="footer-meta">CARNET · Association loi 1901 · à but non lucratif</p>
  <p class="footer-contact">Contact sécurité : <a href="mailto:auth@carnet.life">auth@carnet.life</a> (préfixe [SECURITY])</p>
</footer>

</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════
# PARTIE B — Patch du menu user dropdown dans index.html
# Insertion entre "Confidentialité" (Lot 9) et "Se déconnecter"
# ═══════════════════════════════════════════════════════════════════════

PATCH_INDEX_ANCHOR = """          <a class="user-menu-item" href="privacy.html" style="text-decoration:none;" data-lot9="privacy">
            <span>Confidentialité</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <button class="user-menu-item" data-action="signOut">"""

PATCH_INDEX_REPLACEMENT = """          <a class="user-menu-item" href="privacy.html" style="text-decoration:none;" data-lot9="privacy">
            <span>Confidentialité</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <a class="user-menu-item" href="security.html" style="text-decoration:none;" data-lot10="security">
            <span>Sécurité</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <button class="user-menu-item" data-action="signOut">"""

PATCHSET_INDEX = PatchSet(
    name="Lot 10 (Phase α) — lien Security dans menu user",
    requires=[
        'data-lot9="privacy"',  # Lot 9 doit être appliqué
    ],
    patches=[
        Patch(
            name="Lien Sécurité dans user-menu",
            anchor=PATCH_INDEX_ANCHOR,
            replacement=PATCH_INDEX_REPLACEMENT,
            idempotence_marker='data-lot10="security"',
        ),
    ],
)


# ═══════════════════════════════════════════════════════════════════════
# PARTIE C — Helper idempotent (pattern Lot 9)
# ═══════════════════════════════════════════════════════════════════════

def _md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def ensure_security_file(index_path: Path, dry_run: bool = False) -> int:
    target = index_path.parent / 'security.html'
    expected_md5 = _md5(SECURITY_HTML)

    print(f"\n{_Style.BOLD}► Lot 10 (Phase α) — Création / mise à jour security.html{_Style.RESET}")
    print(f"  {_Style.GREY}Fichier : {target}{_Style.RESET}")

    if target.exists():
        current = target.read_text(encoding='utf-8')
        if _md5(current) == expected_md5:
            print(f"  {_Style.DIM}◇ security.html : déjà à jour (skip, md5 identique){_Style.RESET}")
            return 0
        if dry_run:
            print(f"  {_Style.YELLOW}⚠ security.html existe avec contenu différent — sera mis à jour{_Style.RESET}")
            return 0
        backup_path = target.with_suffix('.html.before_lot10')
        if not backup_path.exists():
            backup_path.write_text(current, encoding='utf-8')
            print(f"  {_Style.BLUE}▸ Backup{_Style.RESET} : {backup_path.name}")
        target.write_text(SECURITY_HTML, encoding='utf-8')
        print(f"  {_Style.GREEN}✓ security.html mis à jour ({len(SECURITY_HTML):,} chars){_Style.RESET}")
        return 0

    if dry_run:
        print(f"  {_Style.YELLOW}⚠ security.html n'existe pas — sera créé ({len(SECURITY_HTML):,} chars){_Style.RESET}")
        return 0
    target.write_text(SECURITY_HTML, encoding='utf-8')
    print(f"  {_Style.GREEN}✓ security.html créé ({len(SECURITY_HTML):,} chars){_Style.RESET}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Apply CARNET Lot 10 (Phase α) — Security page + menu lien")
    parser.add_argument("file", type=Path, help="Path to index.html")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: {args.file} not found")
        return 1

    rc_a = ensure_security_file(args.file, dry_run=args.dry_run)
    if rc_a != 0:
        return rc_a

    return PATCHSET_INDEX.apply(args.file, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
