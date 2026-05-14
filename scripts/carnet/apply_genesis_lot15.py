#!/usr/bin/env python3
"""
CARNET · Lot 15 (Phase α) — Page Mémoire Genesis

Source        : Founder story Sly + Christian autour de leur Mercedes-Benz
                E250 CGI Carlsson 2011, co-ownership 2/2 depuis 2011,
                55 000 km partagés. Cette voiture portera le NFT Vehicle
                Certificate VC-001, le premier Vehicle Certificate XLS-20
                émis par CARNET, frappé lors de la cérémonie inaugurale
                du 14·12·2026 à la Cité de l'automobile de Mulhouse.

Scope         : Page standalone éditoriale (pas une page légale comme
                Privacy/Security/A11y/Transparency — c'est un récit).
                Sections :
                  1. Hero — Elle.
                  2. La voiture (specs, kilométrage, co-ownership)
                  3. Eux (Sly + Christian, 2011, le partage commence)
                  4. Carlsson (Autotechnik, le tuner)
                  5. VC-001 (le premier certificat NFT XLS-20)
                  6. Mulhouse (la Cité, Schlumpf, le lieu juste)
                  7. Mousquetaire (l'archétype incarné, un pour tous)
                  8. Le template (pour celles et ceux qui suivront)

                + lien "Mémoire Genesis" dans menu user dropdown (entre
                Transparence et Se déconnecter)

Hors scope    : Photos / vidéos (à venir, Phase ε quand assets disponibles)
                Programme détaillé de la cérémonie (à venir J-30 du launch)
                Liste invités (à venir J-30 si publié)
                NFT VC-001 metadata réelle (frappée 14·12·2026)

Pipeline du script (pattern Lots 9-12) :
  - Étape A : créer/mettre à jour genesis.html (idempotence md5)
  - Étape B : patcher index.html pour ajouter lien menu user

Prérequis : Lot 12 (Phase α) appliqué (le menu user contient déjà
            Transparence — anchor pour insertion)
Usage     :
    python3 apply_genesis_lot15.py path/to/index.html
    python3 apply_genesis_lot15.py path/to/index.html --dry-run
"""

import sys
import hashlib
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from carnet_patch_lib import Patch, PatchSet, _Style


# ═══════════════════════════════════════════════════════════════════════
# PARTIE A — Contenu du fichier genesis.html
# ═══════════════════════════════════════════════════════════════════════

GENESIS_HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CARNET · Genesis · la voiture qui porte VC-001</title>
  <meta name="description" content="Mémoire Genesis CARNET — Mercedes-Benz E250 CGI Carlsson 2011, co-owned 2/2 entre Sly et Christian depuis 2011. Premier certificat NFT XLS-20 frappé à Mulhouse le 14 décembre 2026.">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Bodoni+Moda:ital,wght@1,400;1,500;1,600;1,700&family=Cormorant+Garamond:ital,wght@1,400;1,500;1,600&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=DM+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="carnet-tokens.css">
  <style>
    body { margin: 0; font-family: var(--sans); background: var(--papier); color: var(--encre); line-height: 1.55; -webkit-font-smoothing: antialiased; }
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
    .ed-nav a:hover { color: var(--orange-polo); }

    main { max-width: 700px; margin: 0 auto; padding: 56px 22px 80px; }

    /* Hero */
    .genesis-eyebrow {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.22em;
      color: var(--orange-polo);
      text-transform: uppercase;
      margin: 0 0 18px 0;
    }
    h1 {
      font-family: var(--display);
      font-style: italic;
      font-weight: 500;
      font-size: 110px;
      line-height: 0.9;
      letter-spacing: -0.025em;
      margin: 0 0 24px 0;
      color: var(--encre);
    }
    .genesis-lede {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 19px;
      line-height: 1.45;
      color: var(--encre-soft);
      margin: 0 0 8px 0;
    }
    .genesis-lede em {
      color: var(--encre);
    }
    .genesis-stamp {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.16em;
      color: var(--gris);
      text-transform: uppercase;
      margin: 32px 0 0 0;
      padding-top: 14px;
      border-top: 1px solid var(--gris-line);
      display: flex;
      gap: 12px;
      flex-wrap: wrap;
    }
    .genesis-stamp span { white-space: nowrap; }
    .genesis-stamp span + span::before { content: "·"; margin-right: 12px; color: var(--orange-polo); }

    /* Sections */
    section { margin: 56px 0 0 0; scroll-margin-top: 90px; }
    .section-eyebrow {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.2em;
      color: var(--orange-polo);
      text-transform: uppercase;
      margin: 0 0 12px 0;
    }
    h2 {
      font-family: var(--display);
      font-style: italic;
      font-weight: 500;
      font-size: 36px;
      line-height: 1.05;
      letter-spacing: -0.015em;
      margin: 0 0 22px 0;
      color: var(--encre);
    }
    section p {
      font-size: 16px;
      line-height: 1.7;
      color: var(--encre-soft);
      margin: 0 0 18px 0;
    }
    section p strong {
      color: var(--encre);
      font-weight: 600;
    }
    section p em {
      font-family: var(--editorial);
      font-style: italic;
      color: var(--encre);
    }

    /* Specs card — la voiture */
    .specs-card {
      margin: 22px 0;
      padding: 22px;
      background: #FAFAF7;
      border: 1px solid var(--gris-line);
      border-radius: var(--r);
      display: grid;
      grid-template-columns: 1fr;
      gap: 14px;
    }
    @media (min-width: 600px) {
      .specs-card { grid-template-columns: 1fr 1fr; }
    }
    .specs-row {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      gap: 14px;
      padding: 8px 0;
      border-bottom: 1px solid rgba(0,0,0,0.06);
    }
    .specs-row:last-child { border-bottom: none; }
    .specs-label {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.12em;
      color: var(--gris);
      text-transform: uppercase;
    }
    .specs-value {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 16px;
      color: var(--encre);
      text-align: right;
    }
    .specs-value strong { font-weight: 600; }

    /* Callout — VC-001 */
    .vc-card {
      margin: 22px 0;
      padding: 24px;
      background: var(--encre);
      color: var(--papier);
      border-radius: var(--r);
      position: relative;
    }
    .vc-card-label {
      font-family: var(--mono);
      font-size: 10px;
      letter-spacing: 0.22em;
      color: #9FE1CB;
      text-transform: uppercase;
      margin: 0 0 10px 0;
    }
    .vc-card-id {
      font-family: var(--display);
      font-style: italic;
      font-weight: 500;
      font-size: 48px;
      line-height: 1;
      margin: 0 0 14px 0;
      letter-spacing: -0.01em;
    }
    .vc-card-desc {
      font-family: var(--editorial);
      font-style: italic;
      font-size: 16px;
      line-height: 1.5;
      color: var(--papier);
      opacity: 0.92;
      margin: 0;
    }

    /* Pull quote — Mousquetaire */
    .pull-quote {
      margin: 38px 0;
      padding: 26px 0;
      border-top: 1px solid var(--gris-line);
      border-bottom: 1px solid var(--gris-line);
      text-align: center;
    }
    .pull-quote-text {
      font-family: var(--display);
      font-style: italic;
      font-weight: 500;
      font-size: 28px;
      line-height: 1.25;
      letter-spacing: -0.01em;
      color: var(--encre);
      margin: 0 0 10px 0;
    }
    .pull-quote-attribution {
      font-family: var(--mono);
      font-size: 9px;
      letter-spacing: 0.22em;
      color: var(--gris);
      text-transform: uppercase;
    }

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
      h1 { font-size: 156px; }
      h2 { font-size: 42px; }
      main { padding: 80px 32px 100px; }
      .pull-quote-text { font-size: 32px; }
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

  <p class="genesis-eyebrow">Mémoire Genesis · CARNET VC-001</p>
  <h1><em>Elle.</em></h1>
  <p class="genesis-lede"><em>Elle</em> n'est pas la plus rapide. Elle n'est pas la plus chère. Elle est <em>la première</em> — celle qui porte le certificat n°1 de CARNET. La voiture autour de laquelle tout le reste se construit.</p>
  <p class="genesis-stamp">
    <span>Mercedes-Benz E250 CGI</span>
    <span>Carlsson Autotechnik</span>
    <span>2011</span>
    <span>55 000 km</span>
    <span>Co-ownership 2/2</span>
  </p>

  <section id="la-voiture">
    <p class="section-eyebrow">01 · La voiture</p>
    <h2>Mercedes-Benz E250 CGI Carlsson.</h2>
    <p>Coupé W207, deux portes, calandre étoile-trois. Le quatre cylindres 1.8 litres CGI suralimenté, qui ne fait pas dans la démesure. La signature Carlsson sur les jantes, sur la mécanique, sur la robe — discrète, qui ne crie pas. Une voiture qu'on prend pour aller chercher quelqu'un, et qu'on garde quinze ans.</p>
    <div class="specs-card">
      <div class="specs-row">
        <span class="specs-label">Année</span>
        <span class="specs-value">2011</span>
      </div>
      <div class="specs-row">
        <span class="specs-label">Modèle</span>
        <span class="specs-value">E250 CGI Coupé</span>
      </div>
      <div class="specs-row">
        <span class="specs-label">Préparateur</span>
        <span class="specs-value">Carlsson Autotechnik</span>
      </div>
      <div class="specs-row">
        <span class="specs-label">Kilométrage</span>
        <span class="specs-value"><strong>55 000 km</strong></span>
      </div>
      <div class="specs-row">
        <span class="specs-label">Statut</span>
        <span class="specs-value">Co-owned 2/2</span>
      </div>
      <div class="specs-row">
        <span class="specs-label">Certificat</span>
        <span class="specs-value"><strong>VC-001</strong></span>
      </div>
    </div>
    <p>55 000 km en 15 ans. <em>Pas une voiture-musée</em>, pas une voiture-trophée. Une voiture roulée — assez pour qu'elle ait vu deux mariages, des courses chez le glacier, une panne sur l'autoroute A6 un dimanche soir. Assez peu pour qu'elle ait encore tout à donner.</p>
  </section>

  <section id="eux">
    <p class="section-eyebrow">02 · Eux</p>
    <h2>Sly et Christian.</h2>
    <p><strong>2011.</strong> Sylvain et Christian ont la trentaine. Ni l'un ni l'autre n'a les moyens d'acheter ce coupé Mercedes seul. Ils décident de l'acheter <em>ensemble</em>. Pas une option d'achat partagé, pas un montage SCI compliqué — juste deux noms sur le certificat de cession, une parole donnée, et un accord tacite : on en prend soin, on partage tout, on décidera ensemble le jour où il faudra décider.</p>
    <p>Pendant quinze ans, ils ne se sont jamais disputés à propos de cette voiture. Ils l'ont prêtée à des amis qui se mariaient. Ils ont roulé dedans en silence quand l'un des deux traversait quelque chose. Ils ont changé l'embrayage à frais partagés en 2018. Ils ont refusé deux offres de rachat — pas parce que le prix était mauvais, parce que ce n'était pas le bon moment.</p>
    <p>L'idée de CARNET vient de là. <strong>Une voiture, c'est une histoire qui se partage.</strong> Et il n'existait jusque-là aucun outil pour formaliser ce partage de façon durable, transparente, transmissible.</p>
  </section>

  <section id="carlsson">
    <p class="section-eyebrow">03 · Le préparateur</p>
    <h2>Carlsson Autotechnik.</h2>
    <p>Famille Hartge à l'origine, puis Andreas et Rolf-Hartmut Carlsson reprennent la spécialité Mercedes en 1989. Atelier en Sarre, près de la frontière allemande. Pas un tuner agressif comme Brabus ou Mansory — Carlsson travaille en finesse, sur des Classe E et S, garde la sobriété, ajoute du caractère sans dénaturer.</p>
    <p>La C25 (basée sur SL65 AMG) reste leur tour de force public. Mais le cœur du métier, ce sont ces préparations discrètes, sur des coupés et berlines bourgeoises — celles qu'on ne remarque pas en croisant à un feu rouge, et qui font la différence après vingt minutes au volant.</p>
    <p>Carlsson a fait faillite une première fois en 2017, repris depuis. La voiture porte donc une signature qui appartient déjà à l'histoire de Mercedes — ce qui ne fait qu'ajouter à sa valeur de mémoire.</p>
  </section>

  <section id="vc-001">
    <p class="section-eyebrow">04 · Certificat</p>
    <h2>VC-001.</h2>
    <p>Le 14 décembre 2026, à Mulhouse, lors de la cérémonie inaugurale de CARNET, un premier <strong>Vehicle Certificate NFT XLS-20</strong> sera frappé sur le ledger XRPL. Identifiant CARNET interne : <strong>VC-001</strong>. Bénéficiaires inscrits on-chain : Sylvain Schaillout + Christian, en multisig 2/2.</p>
    <div class="vc-card">
      <p class="vc-card-label">Vehicle Certificate</p>
      <h3 class="vc-card-id">VC-001</h3>
      <p class="vc-card-desc">Premier certificat XLS-20 émis par l'Association Carnet. Voiture : E250 CGI Carlsson 2011. Royalties 1,7% on-chain au profit de l'asso. Co-ownership 2/2 enforcée par signatures multiples.</p>
    </div>
    <p>Le certificat survivra à CARNET. Si l'association disparaît demain, le NFT reste sur XRPL, consultable, transférable, héritable. C'est le sens du choix d'un ledger public décentralisé — donner aux objets et aux histoires automobiles une assise qui ne dépend pas de l'existence continue de l'opérateur.</p>
  </section>

  <section id="mulhouse">
    <p class="section-eyebrow">05 · Le lieu</p>
    <h2>Mulhouse, 14 décembre 2026.</h2>
    <p>Pas Paris, pas Genève, pas Monaco. <strong>Mulhouse.</strong> Parce que la Cité de l'automobile y abrite la collection des frères Schlumpf — la plus grande collection automobile au monde, dans une halle industrielle de 25 000 m² qui ressemble à un songe. 450 voitures, dont une centaine de Bugatti, dont la Royale Esders, dont les choses qui n'ont pas de prix.</p>
    <p>Le 14 décembre 2026, jour du <em>Big Bang launch</em> de CARNET — coup d'envoi de la plateforme et lancement de l'association — la cérémonie VC-001 a lieu là-bas. Une seule voiture frappée, une seule transaction XRPL. Le reste est public, transparent, audi­table à perpétuité.</p>
    <p>Pourquoi Mulhouse précisément : parce que c'est un lieu juste pour ce qu'on essaie de faire — donner aux voitures une mémoire qui dure. Schlumpf l'avait fait avec des halles. Nous le faisons avec un ledger.</p>
  </section>

  <section id="mousquetaire">
    <p class="section-eyebrow">06 · L'archétype</p>
    <h2>Mousquetaire.</h2>
    <p>Sur la liste des 8 archétypes proposés par CARNET, l'un d'eux décrit Sylvain et Christian autour de cette E250 : <strong>Mousquetaire</strong>. Un pour tous, tous pour un. Co-ownership multi-signature, décisions collégiales, valeurs partagées. La voiture appartient au collectif, pas à l'un ou à l'autre.</p>
    <p>L'archétype Mousquetaire est <em>l'évolution open d'un rallye outlaw</em> — comme un Gumball où l'on aurait remplacé l'individualisme par la coopération. La voiture y devient un instrument de lien, pas un trophée à exhiber.</p>
    <p>Le NFT VC-001 est donc aussi un template technique : tout couple, fratrie, groupe d'amis, club, association qui voudra adopter cette posture multi-signature 2/2, 3/3 ou n/n pourra le faire via CARNET, à partir du 14 décembre 2026.</p>
  </section>

  <section id="template">
    <p class="section-eyebrow">07 · Le template</p>
    <h2>Pour celles et ceux qui suivront.</h2>
    <p>Cette mémoire Genesis n'est pas une simple anecdote founder. Elle pose un précédent enregistré on-chain : <strong>VC-001 est le modèle</strong> que toutes les voitures CARNET-iennes suivront. Mêmes droits, même structure, même royalty taux (1,7 %), même portabilité hors-CARNET.</p>
    <p>VC-002 sera frappé dès qu'un membre de l'association en fera la demande. VC-003, VC-004, et ainsi de suite — à un rythme qu'on n'essaie pas de prédire. Chaque certificat raconte sa propre histoire, mais ils partagent tous l'ADN technique inscrit dans VC-001.</p>
    <p>Si vous lisez ceci avant le 14 décembre 2026 : <em>on vous attend</em>. Si vous le lisez après : votre VC se range à côté du nôtre, sur le même ledger, avec les mêmes droits.</p>
  </section>

  <div class="pull-quote">
    <p class="pull-quote-text"><em>Une voiture, c'est une histoire qui se partage.</em></p>
    <p class="pull-quote-attribution">Sly + Christian · 2011 → 2026 → ∞</p>
  </div>

</main>

<footer>
  <p class="footer-meta">CARNET · Association loi 1901 · à but non lucratif</p>
  <p class="footer-contact">Cérémonie Genesis · 14 décembre 2026 · Cité de l'automobile, Mulhouse · contact <a href="mailto:auth@carnet.life">auth@carnet.life</a></p>
</footer>

</body>
</html>
"""


# ═══════════════════════════════════════════════════════════════════════
# PARTIE B — Patch du menu user dropdown
# Insertion entre "Transparence" (Lot 12) et "Se déconnecter"
# ═══════════════════════════════════════════════════════════════════════

PATCH_INDEX_ANCHOR = """          <a class="user-menu-item" href="transparency.html" style="text-decoration:none;" data-lot12="transparency">
            <span>Transparence</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <button class="user-menu-item" data-action="signOut">"""

PATCH_INDEX_REPLACEMENT = """          <a class="user-menu-item" href="transparency.html" style="text-decoration:none;" data-lot12="transparency">
            <span>Transparence</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <a class="user-menu-item" href="genesis.html" style="text-decoration:none;" data-lot15="genesis">
            <span>Mémoire Genesis</span>
            <span class="user-menu-chevron">→</span>
          </a>
          <button class="user-menu-item" data-action="signOut">"""

PATCHSET_INDEX = PatchSet(
    name="Lot 15 (Phase α) — lien Mémoire Genesis dans menu user",
    requires=[
        'data-lot12="transparency"',
    ],
    patches=[
        Patch(
            name="Lien Mémoire Genesis dans user-menu",
            anchor=PATCH_INDEX_ANCHOR,
            replacement=PATCH_INDEX_REPLACEMENT,
            idempotence_marker='data-lot15="genesis"',
        ),
    ],
)


# ═══════════════════════════════════════════════════════════════════════
# PARTIE C — Helper idempotent (pattern Lots 9-12)
# ═══════════════════════════════════════════════════════════════════════

def _md5(text: str) -> str:
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def ensure_genesis_file(index_path: Path, dry_run: bool = False) -> int:
    target = index_path.parent / 'genesis.html'
    expected_md5 = _md5(GENESIS_HTML)

    print(f"\n{_Style.BOLD}► Lot 15 (Phase α) — Création / mise à jour genesis.html{_Style.RESET}")
    print(f"  {_Style.GREY}Fichier : {target}{_Style.RESET}")

    if target.exists():
        current = target.read_text(encoding='utf-8')
        if _md5(current) == expected_md5:
            print(f"  {_Style.DIM}◇ genesis.html : déjà à jour (skip, md5 identique){_Style.RESET}")
            return 0
        if dry_run:
            print(f"  {_Style.YELLOW}⚠ genesis.html existe avec contenu différent — sera mis à jour{_Style.RESET}")
            return 0
        backup_path = target.with_suffix('.html.before_lot15')
        if not backup_path.exists():
            backup_path.write_text(current, encoding='utf-8')
            print(f"  {_Style.BLUE}▸ Backup{_Style.RESET} : {backup_path.name}")
        target.write_text(GENESIS_HTML, encoding='utf-8')
        print(f"  {_Style.GREEN}✓ genesis.html mis à jour ({len(GENESIS_HTML):,} chars){_Style.RESET}")
        return 0

    if dry_run:
        print(f"  {_Style.YELLOW}⚠ genesis.html n'existe pas — sera créé ({len(GENESIS_HTML):,} chars){_Style.RESET}")
        return 0
    target.write_text(GENESIS_HTML, encoding='utf-8')
    print(f"  {_Style.GREEN}✓ genesis.html créé ({len(GENESIS_HTML):,} chars){_Style.RESET}")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Apply CARNET Lot 15 (Phase α) — Genesis page + menu lien")
    parser.add_argument("file", type=Path, help="Path to index.html")
    parser.add_argument("--dry-run", action="store_true", help="Validate without writing")
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: {args.file} not found")
        return 1

    rc_a = ensure_genesis_file(args.file, dry_run=args.dry_run)
    if rc_a != 0:
        return rc_a

    return PATCHSET_INDEX.apply(args.file, dry_run=args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
