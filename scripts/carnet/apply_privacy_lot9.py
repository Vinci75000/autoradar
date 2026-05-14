#!/usr/bin/env python3
"""
CARNET · Lot 9 (Phase α) — Page Privacy / RGPD

Source        : Création d'une nouvelle page standalone privacy.html
                (conforme RGPD article 13) + lien dans menu user dropdown
                d'index.html.

Scope         : Politique de confidentialité Year -1 obligatoire pour une
                association loi 1901 collectant des données personnelles.
                12 sections RGPD article 13 :
                  1. Responsable de traitement
                  2. Finalités
                  3. Base légale
                  4. Données collectées
                  5. Destinataires
                  6. Transferts hors UE
                  7. Durée de conservation
                  8. Vos droits
                  9. Réclamation CNIL
                  10. Cookies & trackers
                  11. Décisions automatisées
                  12. Mises à jour

Hors scope    : Mécanisme d'export RGPD (téléchargement JSON) → Phase ε
                Cookie banner consent UI → Phase ε si cookies non-essentiels
                Page Security / Accessibility / Transparency → Lots 10/11/12

Pipeline du script :
  - Étape A : créer/mettre à jour privacy.html avec idempotence par md5
  - Étape B : patcher index.html pour ajouter lien menu user (anchor-based)

Prérequis : Lot 8 (Phase α) appliqué
Usage     :
    python3 apply_privacy_lot9.py path/to/index.html
    python3 apply_privacy_lot9.py path/to/index.html --dry-run

Note : le script crée privacy.html dans le même dossier que index.html.
"""

import sys
import hashlib
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, _Style


# ═══════════════════════════════════════════════════════════════════════
# PARTIE A — Contenu du fichier privacy.html
# ═══════════════════════════════════════════════════════════════════════

PRIVACY_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CARNET · Confidentialité · politique de protection des données</title>
  <meta name="description" content="Politique de confidentialité CARNET — comment vos données sont traitées, vos droits, vos choix.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@1,400;1,500;1,600&family=Cormorant+Garamond:ital,wght@1,400;1,500;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="carnet-tokens.css">
  <style>
    body {
      margin: 0;
      font-family: var(--sans);
      background: var(--papier);
      color: var(--encre);
      line-height: 1.5;
      -webkit-font-smoothing: antialiased;
    }
    a { color: var(--orange-polo); text-decoration: none; }
    a:hover { text-decoration: underline; text-underline-offset: 3px; }

    /* Topbar */
    .topbar {
      padding: 14px 22px;
      border-bottom: 1px solid var(--gris-line);
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: var(--papier);
      position: sticky;
      top: 0;
      z-index: 5;
    }
    .topbar-wordmark { display: flex; gap: 7px; align-items: baseline; }
    .topbar-dot {
      width: 7px; height: 7px;
      background: var(--orange-polo);
      border-radius: 1px;
      display: inline-block;
    }
    .topbar-name {
      font-family: var(--display);
      font-style: italic;
      font-size: 18px;
      color: var(--encre);
    }
    .topbar-back {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.14em;
      color: var(--gris);
      text-transform: uppercase;
    }
    .topbar-back:hover { color: var(--orange-polo); }

    /* Nav éditoriale */
    .ed-nav {
      display: flex;
      gap: 22px;
      padding: 10px 22px;
      border-bottom: 1px solid var(--gris-line);
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }
    .ed-nav a {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.16em;
      text-transform: uppercase;
      color: var(--gris);
      white-space: nowrap;
    }
    .ed-nav a.is-active { color: var(--encre); }
    .ed-nav a:hover { color: var(--orange-polo); }

    /* Container */
    main { max-width: 700px; margin: 0 auto; padding: 40px 22px 80px; }

    /* Hero */
    .hero-eyebrow {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.2em;
      color: var(--gris);
      text-transform: uppercase;
      margin: 0 0 12px 0;
    }
    h1 {
      font-family: var(--display);
      font-style: italic;
      font-weight: 500;
      font-size: 48px;
      line-height: 0.95;
      letter-spacing: -0.015em;
      margin: 0 0 16px 0;
      color: var(--encre);
    }
    .hero-sub {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 17px;
      line-height: 1.5;
      color: var(--encre-soft);
      margin: 0 0 28px 0;
    }
    .hero-meta {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.12em;
      color: var(--gris);
      text-transform: uppercase;
      margin: 0;
    }

    /* TOC */
    .toc {
      margin: 32px 0 40px;
      padding: 20px 22px;
      background: #FAFAF7;
      border: 1px solid var(--gris-line);
      border-radius: var(--r);
    }
    .toc-title {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.2em;
      color: var(--gris);
      text-transform: uppercase;
      margin: 0 0 12px 0;
    }
    .toc ol {
      list-style: none;
      counter-reset: toc;
      padding: 0;
      margin: 0;
      column-count: 1;
    }
    @media (min-width: 600px) {
      .toc ol { column-count: 2; column-gap: 28px; }
    }
    .toc li {
      counter-increment: toc;
      padding: 4px 0;
      font-family: var(--editorial);
      font-style: italic;
      font-size: 15px;
      break-inside: avoid;
    }
    .toc li::before {
      content: counter(toc, decimal-leading-zero) ". ";
      font-family: var(--mono);
      font-style: normal;
      font-size: 11px;
      color: var(--orange-polo);
      margin-right: 6px;
    }
    .toc li a { color: var(--encre); }
    .toc li a:hover { color: var(--orange-polo); text-decoration: none; }

    /* Sections */
    section { margin: 0 0 40px 0; scroll-margin-top: 90px; }
    .section-eyebrow {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.2em;
      color: var(--orange-polo);
      text-transform: uppercase;
      margin: 0 0 8px 0;
    }
    h2 {
      font-family: var(--display);
      font-style: italic;
      font-weight: 500;
      font-size: 28px;
      line-height: 1.1;
      letter-spacing: -0.01em;
      margin: 0 0 14px 0;
      color: var(--encre);
    }
    section p {
      font-size: 15px;
      line-height: 1.65;
      color: var(--encre-soft);
      margin: 0 0 14px 0;
    }
    section p strong {
      color: var(--encre);
      font-weight: 600;
    }
    section ul { padding-left: 0; list-style: none; margin: 0 0 14px 0; }
    section ul li {
      position: relative;
      padding: 6px 0 6px 22px;
      font-size: 15px;
      line-height: 1.55;
      color: var(--encre-soft);
    }
    section ul li::before {
      content: "·";
      position: absolute;
      left: 8px;
      top: 6px;
      font-family: var(--mono);
      color: var(--orange-polo);
    }
    section ul li strong { color: var(--encre); font-weight: 600; }

    .callout {
      padding: 16px 18px;
      background: #FAFAF7;
      border-left: 3px solid var(--vert-anglais);
      border-radius: var(--r);
      margin: 14px 0;
    }
    .callout p { margin: 0; font-family: var(--editorial); font-style: italic; font-size: 14px; color: var(--encre); }

    /* Footer */
    footer {
      max-width: 700px;
      margin: 60px auto 0;
      padding: 32px 22px 80px;
      border-top: 1px solid var(--gris-line);
    }
    .footer-meta {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.08em;
      color: var(--gris);
      margin: 0 0 6px 0;
    }
    .footer-contact {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 15px;
      color: var(--encre-soft);
      margin: 0;
    }
    .footer-contact a { color: var(--encre); border-bottom: 1px solid var(--gris-line); padding-bottom: 1px; }
    .footer-contact a:hover { color: var(--orange-polo); border-bottom-color: var(--orange-polo); }

    @media (min-width: 600px) {
      h1 { font-size: 60px; }
      h2 { font-size: 32px; }
      main { padding: 60px 32px 100px; }
    }
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

  <p class="hero-eyebrow">Politique de confidentialité</p>
  <h1><em>Vos données, vos choix.</em></h1>
  <p class="hero-sub">CARNET est tenu par une association loi 1901 à but non lucratif. Nous traitons vos données pour faire fonctionner le service, et pour rien d'autre. Voici précisément lesquelles, comment, et comment vous gardez la main.</p>
  <p class="hero-meta">Version 1.0 · 14 mai 2026 · conforme RGPD article 13</p>

  <div class="toc">
    <p class="toc-title">Sommaire</p>
    <ol>
      <li><a href="#section-1">Qui traite vos données</a></li>
      <li><a href="#section-2">Pour quoi faire</a></li>
      <li><a href="#section-3">Sur quelle base</a></li>
      <li><a href="#section-4">Quelles données</a></li>
      <li><a href="#section-5">Qui les voit</a></li>
      <li><a href="#section-6">Transferts hors UE</a></li>
      <li><a href="#section-7">Combien de temps</a></li>
      <li><a href="#section-8">Vos droits</a></li>
      <li><a href="#section-9">Réclamation CNIL</a></li>
      <li><a href="#section-10">Cookies et trackers</a></li>
      <li><a href="#section-11">Décisions automatisées</a></li>
      <li><a href="#section-12">Mises à jour de cette politique</a></li>
    </ol>
  </div>

  <section id="section-1">
    <p class="section-eyebrow">01 · Responsable</p>
    <h2>Qui traite vos données.</h2>
    <p>Le responsable de traitement est l'<strong>Association Carnet</strong> (loi 1901, à but non lucratif, sans salariés ni distribution de dividendes). Tout l'argent collecté (donations, royalties de cession sur les NFT XLS-20) finance l'infrastructure et les événements automobiles avec des enfants.</p>
    <p>Pour toute question — données personnelles ou compte — écrivez à <a href="mailto:auth@carnet.life">auth@carnet.life</a>.</p>
    <div class="callout">
      <p>Acronymes : <em>Carnet Automatisé Référentiel du Négoce Et de la Transparence</em> (FR) · <em>Curated Automotive Records Network for Exchange and Trust</em> (EN).</p>
    </div>
  </section>

  <section id="section-2">
    <p class="section-eyebrow">02 · Finalités</p>
    <h2>Pour quoi faire.</h2>
    <p>Vos données sont traitées uniquement pour faire fonctionner CARNET :</p>
    <ul>
      <li><strong>Créer et gérer votre compte</strong> (authentification, session, préférences).</li>
      <li><strong>Tenir votre garage</strong> : voitures, entretiens, factures, photos, souvenirs.</li>
      <li><strong>Vous proposer un profil d'archétype</strong> (pour personnaliser l'interface — vous gardez le contrôle).</li>
      <li><strong>Détecter des opportunités marché</strong> qui correspondent à votre garage et à vos archétypes.</li>
      <li><strong>Vous notifier d'événements</strong> auxquels vous participez (rallyes, track days, convoy).</li>
      <li><strong>Recevoir vos donations en RLUSD</strong> sur le wallet officiel <code style="font-family:var(--mono);font-size:13px;background:#FAFAF7;padding:1px 5px;border-radius:2px;">rJBhnYvg5kq9PgWFZziEXu2EcdJfcq8WSU</code>.</li>
      <li><strong>Émettre des certificats NFT XLS-20</strong> sur le ledger XRPL pour vos voitures (à votre demande).</li>
      <li><strong>Statistiques d'usage anonymisées</strong> (combien d'utilisateurs actifs, quelles fonctionnalités sont utilisées — jamais d'individu identifiable).</li>
    </ul>
  </section>

  <section id="section-3">
    <p class="section-eyebrow">03 · Base légale</p>
    <h2>Sur quelle base.</h2>
    <ul>
      <li><strong>Exécution du service</strong> (contrat) : votre compte, votre garage, les fonctionnalités de base.</li>
      <li><strong>Consentement explicite</strong> : profilage archétype, géolocalisation pour la fonction Tribu et le Co-pilote rallye, scoring LLM. Vous pouvez retirer ce consentement à tout moment.</li>
      <li><strong>Intérêt légitime</strong> : analytics anonymisées, sécurité, prévention de fraude. Toujours minimal, jamais à votre détriment.</li>
      <li><strong>Obligation légale</strong> : conservation des logs liés aux transactions XRPL pour les durées réglementaires.</li>
    </ul>
  </section>

  <section id="section-4">
    <p class="section-eyebrow">04 · Catégories de données</p>
    <h2>Quelles données.</h2>
    <ul>
      <li><strong>Identité</strong> : email, prénom (optionnel), pseudo si fourni.</li>
      <li><strong>Authentification</strong> : empreinte cryptographique du mot de passe (jamais le mot de passe en clair — Supabase Auth s'en occupe), tokens de session, journaux de connexion.</li>
      <li><strong>Profil</strong> : archétype(s) que vous avez sélectionné(s), préférences d'affichage.</li>
      <li><strong>Garage</strong> : marques, modèles, années, kilométrages, prix d'acquisition, photos, factures (PDF/images), notes.</li>
      <li><strong>Mémoires</strong> : photos avec captions, dates, événements, tags, voitures associées.</li>
      <li><strong>Géolocalisation</strong> (consentement explicite) : position approximative pour la fonction Tribu (collectionneurs proches) ; position fine pendant la durée d'un rallye/convoy actif.</li>
      <li><strong>Wallet XRPL</strong> : adresse publique uniquement (jamais de clé privée — vous signez via Xaman). Une adresse XRPL est publique par construction du ledger.</li>
      <li><strong>Logs techniques</strong> : adresse IP, user-agent, horodatage des requêtes (durée limitée).</li>
    </ul>
    <div class="callout">
      <p>Nous ne collectons jamais : votre numéro de carte bancaire (les paiements passent par Xaman/XRPL), votre numéro de sécurité sociale, votre situation matrimoniale, vos opinions politiques ou religieuses.</p>
    </div>
  </section>

  <section id="section-5">
    <p class="section-eyebrow">05 · Destinataires</p>
    <h2>Qui les voit.</h2>
    <p>CARNET utilise un nombre limité de sous-traitants, sélectionnés pour leur conformité RGPD :</p>
    <ul>
      <li><strong>Supabase GmbH</strong> (Frankfurt, Allemagne — UE) — base de données principale, authentification, stockage R2 photos.</li>
      <li><strong>Cloudflare Inc.</strong> (San Francisco, USA) — Workers (paiements), R2 (proxy photos), CDN.</li>
      <li><strong>Vercel Inc.</strong> (San Francisco, USA) — hébergement du frontend (le code que vous voyez).</li>
      <li><strong>Anthropic PBC</strong> (San Francisco, USA) — modèle Claude API pour le scoring archétype et l'extraction de données voitures depuis les annonces.</li>
      <li><strong>Xaman / xrpl-labs</strong> (Pays-Bas — UE) — application de signature wallet XRPL (les transactions, vous les signez vous-même).</li>
    </ul>
    <p><strong>Ce que nous ne faisons pas :</strong> aucune vente de données. Aucun courtier publicitaire. Aucune régie ad. Aucun pixel Facebook, aucun Google Analytics.</p>
  </section>

  <section id="section-6">
    <p class="section-eyebrow">06 · Transferts hors UE</p>
    <h2>Transferts hors UE.</h2>
    <p>Certains sous-traitants sont aux États-Unis. Pour ces transferts, nous nous appuyons sur les <strong>Clauses Contractuelles Types</strong> (SCC) adoptées par la Commission européenne, et sur le <strong>Data Privacy Framework UE–US</strong> lorsque le fournisseur y a adhéré.</p>
    <ul>
      <li>Cloudflare, Vercel, Anthropic — SCC + DPF (le cas échéant).</li>
      <li>Supabase — UE (Frankfurt), pas de transfert hors UE pour la base principale.</li>
      <li>Xaman — UE (Pays-Bas).</li>
    </ul>
    <p>Vous pouvez nous demander une copie des SCC à <a href="mailto:auth@carnet.life">auth@carnet.life</a>.</p>
  </section>

  <section id="section-7">
    <p class="section-eyebrow">07 · Durée de conservation</p>
    <h2>Combien de temps.</h2>
    <ul>
      <li><strong>Compte actif</strong> : tant que vous êtes inscrit.</li>
      <li><strong>Compte supprimé</strong> : effacement complet sous 30 jours (sauf obligations légales — voir transactions XRPL ci-dessous).</li>
      <li><strong>Logs techniques</strong> : 90 jours glissants.</li>
      <li><strong>Backups Supabase</strong> : 35 jours glissants.</li>
      <li><strong>Transactions XRPL liées à donations ou royalties NFT</strong> : 10 ans (obligations comptables et fiscales d'une association loi 1901). À noter : ces transactions sont publiques sur le ledger XRPL par nature, indépendamment de CARNET.</li>
    </ul>
  </section>

  <section id="section-8">
    <p class="section-eyebrow">08 · Vos droits</p>
    <h2>Vos droits.</h2>
    <p>Vous disposez à tout moment, gratuitement, des droits suivants :</p>
    <ul>
      <li><strong>Accès</strong> : recevoir une copie des données que nous traitons à votre sujet.</li>
      <li><strong>Rectification</strong> : corriger les données inexactes (directement depuis votre compte pour la plupart).</li>
      <li><strong>Effacement</strong> (droit à l'oubli) : demander la suppression complète de votre compte et de vos données.</li>
      <li><strong>Portabilité</strong> : recevoir vos données dans un format structuré (JSON) pour les transférer ailleurs.</li>
      <li><strong>Opposition</strong> : vous opposer au traitement de vos données pour des finalités déterminées.</li>
      <li><strong>Limitation</strong> : demander la suspension du traitement pendant qu'on étudie une réclamation.</li>
      <li><strong>Retrait du consentement</strong> : pour les traitements basés sur votre consentement (archétype, géolocalisation, LLM scoring).</li>
      <li><strong>Décision humaine</strong> : ne pas faire l'objet d'une décision exclusivement automatisée (voir section 11).</li>
    </ul>
    <p>Pour exercer ces droits : écrivez à <a href="mailto:auth@carnet.life">auth@carnet.life</a>. Nous répondons sous 30 jours.</p>
  </section>

  <section id="section-9">
    <p class="section-eyebrow">09 · Recours</p>
    <h2>Réclamation CNIL.</h2>
    <p>Si vous estimez que vos droits n'ont pas été respectés, vous pouvez introduire une réclamation auprès de la Commission Nationale de l'Informatique et des Libertés :</p>
    <ul>
      <li>CNIL · 3 place de Fontenoy · TSA 80715 · 75334 Paris Cedex 07</li>
      <li><a href="https://www.cnil.fr">cnil.fr</a> · 01 53 73 22 22</li>
    </ul>
    <p>Nous préférons que vous nous écriviez d'abord à <a href="mailto:auth@carnet.life">auth@carnet.life</a> — souvent c'est plus rapide et on règle le problème ensemble.</p>
  </section>

  <section id="section-10">
    <p class="section-eyebrow">10 · Cookies</p>
    <h2>Cookies et trackers.</h2>
    <p>CARNET utilise uniquement des cookies strictement nécessaires :</p>
    <ul>
      <li><strong>Authentification</strong> (Supabase) : pour vous garder connecté entre les visites. Sans ce cookie, vous devriez vous reconnecter à chaque page.</li>
      <li><strong>Préférences UI</strong> : votre choix de mode d'affichage, langue, etc.</li>
    </ul>
    <p>Nous n'utilisons <strong>aucun cookie tiers publicitaire</strong>, <strong>aucun Google Analytics</strong>, <strong>aucun Facebook Pixel</strong>. Pas de bannière de consentement cookie, parce qu'il n'y a rien pour quoi vous demander de consentir.</p>
  </section>

  <section id="section-11">
    <p class="section-eyebrow">11 · Profilage</p>
    <h2>Décisions automatisées.</h2>
    <p>Deux traitements impliquent une forme d'automatisation :</p>
    <ul>
      <li><strong>Scoring archétype</strong> par Claude (LLM Anthropic) : analyse de vos préférences déclarées pour suggérer un ou plusieurs archétypes. Vous pouvez à tout moment modifier, ajouter, retirer vos archétypes manuellement. Si vous voulez une révision humaine, écrivez à <a href="mailto:auth@carnet.life">auth@carnet.life</a>.</li>
      <li><strong>Détection d'opportunités marché</strong> : un algorithme compare votre garage et vos archétypes aux annonces actives pour suggérer des voitures qui pourraient vous intéresser. C'est <strong>purement informatif</strong> — aucune décision contractuelle ou financière n'en découle. Vous n'êtes jamais inscrit, débité, ou engagé sans votre action explicite.</li>
    </ul>
  </section>

  <section id="section-12">
    <p class="section-eyebrow">12 · Versions</p>
    <h2>Mises à jour de cette politique.</h2>
    <p>Cette politique évoluera — c'est inévitable, le service évolue. À chaque modification matérielle, nous vous notifierons par email (si vous avez un compte) au moins 30 jours avant l'entrée en vigueur, avec un résumé clair de ce qui change.</p>
    <p>Version actuelle : <strong>1.0 du 14 mai 2026</strong>. L'historique complet des versions précédentes est disponible sur demande.</p>
  </section>

</main>

<footer>
  <p class="footer-meta">CARNET · Association loi 1901 · à but non lucratif</p>
  <p class="footer-contact">Contact : <a href="mailto:auth@carnet.life">auth@carnet.life</a></p>
</footer>

</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════
# PARTIE B — Patch du menu user dropdown dans index.html
# ═══════════════════════════════════════════════════════════════════════

PATCH_INDEX_ANCHOR = """          <a class="user-menu-item" href="archetypes.html" style="text-decoration:none;">
            <span>Mes archétypes</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <button class="user-menu-item" data-action="signOut">"""

PATCH_INDEX_REPLACEMENT = """          <a class="user-menu-item" href="archetypes.html" style="text-decoration:none;">
            <span>Mes archétypes</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <a class="user-menu-item" href="privacy.html" style="text-decoration:none;" data-lot9="privacy">
            <span>Confidentialité</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <button class="user-menu-item" data-action="signOut">"""

PATCHSET_INDEX = PatchSet(
    name="Lot 9 (Phase α) — lien Privacy dans menu user",
    requires=[
        "LOT 8 (Phase α) — Garage Dashboard Complet",
    ],
    patches=[
        Patch(
            name="Lien Confidentialité dans user-menu",
            anchor=PATCH_INDEX_ANCHOR,
            replacement=PATCH_INDEX_REPLACEMENT,
            idempotence_marker='data-lot9="privacy"',
        ),
    ],
)


# ═══════════════════════════════════════════════════════════════════════
# PARTIE C — Helper idempotent pour créer/mettre à jour privacy.html
# ═══════════════════════════════════════════════════════════════════════

def _md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def ensure_privacy_file(index_path: Path, dry_run: bool = False) -> int:
    """
    Crée ou met à jour privacy.html dans le même dossier qu'index.html.
    Idempotent : si le fichier existe et a le bon contenu, skip silencieusement.
    Retourne exit code (0 = OK).
    """
    privacy_path = index_path.parent / 'privacy.html'
    expected_md5 = _md5(PRIVACY_HTML)

    print(f"\n{_Style.BOLD}► Lot 9 (Phase α) — Création / mise à jour privacy.html{_Style.RESET}")
    print(f"  {_Style.GREY}Fichier : {privacy_path}{_Style.RESET}")

    if privacy_path.exists():
        current = privacy_path.read_text(encoding='utf-8')
        current_md5 = _md5(current)
        if current_md5 == expected_md5:
            print(f"  {_Style.DIM}◇ privacy.html : déjà à jour (skip, md5 identique){_Style.RESET}")
            return 0
        # Contenu différent → backup + écriture
        if dry_run:
            print(f"  {_Style.YELLOW}⚠ privacy.html existe avec contenu différent — sera mis à jour{_Style.RESET}")
            print(f"    {_Style.GREY}Current md5  : {current_md5}{_Style.RESET}")
            print(f"    {_Style.GREY}Expected md5 : {expected_md5}{_Style.RESET}")
            return 0
        backup_path = privacy_path.with_suffix('.html.before_lot9')
        if not backup_path.exists():
            backup_path.write_text(current, encoding='utf-8')
            print(f"  {_Style.BLUE}▸ Backup{_Style.RESET} : {backup_path.name}")
        privacy_path.write_text(PRIVACY_HTML, encoding='utf-8')
        print(f"  {_Style.GREEN}✓ privacy.html mis à jour ({len(PRIVACY_HTML):,} chars){_Style.RESET}")
        return 0

    # Fichier inexistant
    if dry_run:
        print(f"  {_Style.YELLOW}⚠ privacy.html n'existe pas — sera créé ({len(PRIVACY_HTML):,} chars){_Style.RESET}")
        return 0
    privacy_path.write_text(PRIVACY_HTML, encoding='utf-8')
    print(f"  {_Style.GREEN}✓ privacy.html créé ({len(PRIVACY_HTML):,} chars){_Style.RESET}")
    return 0


# ═══════════════════════════════════════════════════════════════════════
# ENTRY POINT — pipeline en 2 étapes
# ═══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Apply CARNET Lot 9 (Phase α) — Privacy page + menu lien",
    )
    parser.add_argument("file", type=Path, help="Path to index.html")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate without writing")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: {args.file} not found")
        return 1

    # Étape A : créer/mettre à jour privacy.html
    rc_a = ensure_privacy_file(args.file, dry_run=args.dry_run)
    if rc_a != 0:
        return rc_a

    # Étape B : patcher index.html
    rc_b = PATCHSET_INDEX.apply(args.file, dry_run=args.dry_run)
    return rc_b


if __name__ == "__main__":
    sys.exit(main())
