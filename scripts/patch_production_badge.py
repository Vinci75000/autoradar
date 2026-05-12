#!/usr/bin/env python3
"""Patch Carnet index.html — badge production v2 (6 tiers)."""
import sys
from pathlib import Path
from datetime import datetime

CSS_BLOCK = """
/* ─── Production badge — 6 tiers ────── */
.ar-prod-badge{font-size:11px;font-style:italic;margin-top:3px;letter-spacing:0.01em;line-height:1.4;color:var(--text2)}
.ar-prod-badge .ar-prod-num{font-family:var(--mono);font-style:normal;font-weight:500;font-size:11px;letter-spacing:0;color:var(--text)}
.ar-prod-badge.tier-unique{color:#E85A1F;font-weight:500}
.ar-prod-badge.tier-confidential{color:#E85A1F}
.ar-prod-badge.tier-confidential .ar-prod-num{color:#E85A1F}
.ar-prod-badge.tier-rare{color:var(--gc)}
.ar-prod-badge.tier-rare .ar-prod-num{color:var(--gc)}
.ar-prod-badge.tier-limited{color:var(--text2)}
.ar-prod-badge.tier-series{color:var(--text3)}
.ar-prod-badge.tier-series .ar-prod-num{color:var(--text2);font-weight:400}
.ar-prod-badge.tier-volume{color:var(--text3)}
.ar-prod-badge.tier-volume .ar-prod-num{color:var(--text2);font-weight:400}
.ar-prod-detail{padding:11px 14px;background:var(--bg2);margin:10px 0;border-radius:0 var(--rsm) var(--rsm) 0;border-left:2px solid var(--border2)}
.ar-prod-detail.tier-unique{border-left-color:#E85A1F}
.ar-prod-detail.tier-confidential{border-left-color:#E85A1F}
.ar-prod-detail.tier-rare{border-left-color:var(--gc)}
.ar-prod-detail.tier-limited{border-left-color:var(--gc);opacity:0.85}
.ar-prod-detail-line{font-size:13px;font-style:italic;color:var(--text);line-height:1.5}
.ar-prod-detail-line .ar-prod-num-big{font-family:var(--mono);font-style:normal;font-weight:500;font-size:14px;letter-spacing:0;margin:0 1px;color:var(--text)}
.ar-prod-detail.tier-unique .ar-prod-num-big{color:#E85A1F}
.ar-prod-detail.tier-confidential .ar-prod-num-big{color:#E85A1F}
.ar-prod-detail.tier-rare .ar-prod-num-big{color:var(--gc)}
.ar-prod-detail.tier-limited .ar-prod-num-big{color:var(--gc)}
.ar-prod-detail-source{font-size:9px;color:var(--text3);margin-top:5px;text-transform:uppercase;letter-spacing:0.07em;font-weight:500}
"""

JS_HELPERS = """
/* PRODUCTION BADGE */
function _shouldShowProdBadge(car){if(!car.production_total||car.production_total<=0)return false;if(car.production_confidence!=null&&car.production_confidence<60)return false;return true}
function _prodTier(n){if(n===1)return'unique';if(n<100)return'confidential';if(n<1000)return'rare';if(n<5000)return'limited';if(n<50000)return'series';return'volume'}
function _formatProdNum(n){return n.toLocaleString('fr-FR')}
function _prodSourceLabel(s){return({wikidata:'Wikidata',wikipedia_infobox:'Wikipedia',wikipedia_section:'Wikipedia',manual:'Source curée',llm_haiku:'Description analysée'})[s]||'Source'}
function prodBadgeHtml(car){if(!_shouldShowProdBadge(car))return'';const t=_prodTier(car.production_total);if(car.production_total===1)return `<div class="ar-prod-badge tier-${t}">Pièce unique</div>`;return `<div class="ar-prod-badge tier-${t}">Une de <span class="ar-prod-num">${_formatProdNum(car.production_total)}</span></div>`}
function prodDetailHtml(car){if(!_shouldShowProdBadge(car))return'';const t=_prodTier(car.production_total);const m=car.production_meta||{};let p='';if(m.year_start&&m.year_end)p=` produites entre ${m.year_start} et ${m.year_end}`;else if(m.year_start)p=` produites depuis ${m.year_start}`;else p=' produites';const s=_prodSourceLabel(car.production_source);if(car.production_total===1)return `<div class="ar-prod-detail tier-${t}"><div class="ar-prod-detail-line">Pièce unique${p}.</div><div class="ar-prod-detail-source">${s}</div></div>`;return `<div class="ar-prod-detail tier-${t}"><div class="ar-prod-detail-line">Une de <span class="ar-prod-num-big">${_formatProdNum(car.production_total)}</span>${p}.</div><div class="ar-prod-detail-source">${s}</div></div>`}
"""

PATCHES = [
    {"name":"CSS badge","skip_marker":"tier-unique","anchor":"/* ── Footer nav ── */","replacement":CSS_BLOCK+"\n/* ── Footer nav ── */"},
    {"name":"JS helpers","skip_marker":"function _prodTier","anchor":"/* ═══════════════════════════════════════════════\n   SEARCH CARD RENDERER","replacement":JS_HELPERS+"\n/* ═══════════════════════════════════════════════\n   SEARCH CARD RENDERER"},
    {"name":"renderCard badge","skip_marker":"${prodBadgeHtml(car)}","anchor":'<div class="ar-title">${car.mk} ${car.mo} · ${car.yr}</div>',"replacement":'<div class="ar-title">${car.mk} ${car.mo} · ${car.yr}</div>\n          ${prodBadgeHtml(car)}'},
    {"name":"detailHtml block","skip_marker":"${prodDetailHtml(car)}","anchor":'<div class="ar-bdown">${recordsScoreBreakdown(car)}</div>',"replacement":'${prodDetailHtml(car)}\n      <div class="ar-bdown">${recordsScoreBreakdown(car)}</div>'},
    {"name":"Supabase view","skip_marker":"from('cars_with_production')","anchor":".from('cars').select('*')","replacement":".from('cars_with_production').select('*')"},
    {"name":"push fields","skip_marker":"production_total: car.production_total","anchor":"ch: car.ch || [], ss: car.ss || {}, hs: car.hs || []","replacement":"ch: car.ch || [], ss: car.ss || {}, hs: car.hs || [],\n      production_total: car.production_total,\n      production_source: car.production_source,\n      production_confidence: car.production_confidence,\n      production_meta: car.production_meta || {}"},
]

def main():
    if len(sys.argv)<2:print("Usage: python patch_production_badge.py path/to/index.html");sys.exit(1)
    path=Path(sys.argv[1])
    if not path.exists():print(f"❌ {path} not found");sys.exit(1)
    content=path.read_text();original=content
    ts=datetime.now().strftime('%Y%m%d_%H%M%S')
    backup=path.with_suffix(f".bak.{ts}.html");backup.write_text(original)
    print(f"📦 Backup: {backup.name}\n")
    applied,skipped=0,0
    for p in PATCHES:
        if p["skip_marker"] in content:print(f"  ⏭  {p['name']}: already applied");skipped+=1;continue
        n=content.count(p["anchor"])
        if n==0:print(f"  ❌ {p['name']}: anchor not found\n      anchor: {p['anchor'][:80]}...");sys.exit(1)
        if n>1:print(f"  ❌ {p['name']}: anchor found {n}× (expected 1)");sys.exit(1)
        content=content.replace(p["anchor"],p["replacement"],1);print(f"  ✓  {p['name']}: applied");applied+=1
    if content!=original:path.write_text(content);print(f"\n✅ {applied} applied, {skipped} skipped.\n   Rollback: cp {backup} {path}")
    else:print(f"\n✅ All {len(PATCHES)} already in place.")

if __name__=="__main__":main()
