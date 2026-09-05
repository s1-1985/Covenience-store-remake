# PS release / revision identity anchors (2026-09-06)

## Scope

Target is the first PlayStation title, **『ザ・コンビニ ～あの町を独占せよ～』** only. This note does not import behavior from later series entries. It records release identities that can be used to separate future play-test evidence by disc/reissue.

No original copyrighted assets, manual scans, screenshots, audio, logos, or text dumps are stored here.

## Evidence labels used here

- **A / MULTI-SOURCE-PACKAGE-ID**: exact product code and release date corroborated by multiple independent catalog/product records.
- **B / SINGLE-SOURCE-PACKAGE-ID**: exact product code from one usable catalog source.
- **UNKNOWN-BEHAVIOR**: package identity is known, but no gameplay/ROM difference has yet been demonstrated.

## Confirmed PlayStation release identities

### 1. Original retail release

- Platform: PlayStation
- Product code: **SLPS-00782**
- Release date: **1997-03-28**
- Publisher: Human
- Original list price: **5,800 yen before tax** (catalog listing)
- Evidence: **A / MULTI-SOURCE-PACKAGE-ID**

Corroboration:
- Retro Game no Dendou catalog lists SLPS-00782, 1997-03-28, Human.
- Suruga-ya lists SLPS-00782, JAN 4959143900141, 1997-03-28, Human.
- Kaitori World independently lists SLPS-00782 and 1997-03-28.
- PSX DataCenter also identifies disc serial SLPS-00782 and release date 1997-03-28.

### 2. PlayStation the Best reissue

- Platform: PlayStation
- Product code: **SLPS-91104**
- Release date: **1998-10-22**
- Label: **PlayStation the Best**
- List price: **2,800 yen before tax** (catalog listing)
- Evidence: **A / MULTI-SOURCE-PACKAGE-ID**

Corroboration:
- Retro Game no Dendou catalog lists SLPS-91104, 1998-10-22, PlayStation the Best.
- Kaitori World independently lists SLPS-91104 and 1998-10-22.

### 3. Major Wave reissue

- Platform: PlayStation
- Product code: **SLPM-86655**
- Release date: **2000-11-30**
- Label: **Major Wave series**
- Publisher shown by later catalog records: **Hamster**
- List price: **1,500 yen before tax** / 1,650 yen tax-included in retail records
- Evidence: **A / MULTI-SOURCE-PACKAGE-ID**

Corroboration:
- Retro Game no Dendou catalog lists SLPM-86655, 2000-11-30, Major Wave.
- Suruga-ya lists SLPM-86655, JAN 4529651000468, 2000-11-30, Hamster.
- Kaitori World independently lists SLPM-86655 and 2000-11-30.

## What this does NOT prove

The existence of three package/product codes does **not** by itself prove three different ROM revisions or gameplay behaviors.

At present the following are **UNKNOWN-BEHAVIOR**:

- whether SLPS-00782 and SLPS-91104 contain byte-identical game data;
- whether SLPM-86655 contains fixes or behavioral changes;
- whether any known exploit, date-boundary behavior, sales-license bug, save behavior, UI quirk, or simulation formula differs among the three PS releases;
- whether save data is fully interoperable across all three releases.

Do not infer a bug fix merely because a later budget release exists.

## Research handling rule added

Future PS gameplay evidence should carry a release identity whenever the source makes it possible:

- `PS-SLPS-00782` — original 1997 release
- `PS-SLPS-91104-BEST` — 1998 PlayStation the Best
- `PS-SLPM-86655-MAJOR-WAVE` — 2000 Major Wave
- `PS-REV-UNKNOWN` — source does not expose disc/product identity

This mirrors the existing SS revision-separation policy and prevents a behavior observed on a later reissue from silently becoming a universal PS rule.

## Why this matters for faithful reconstruction

The current project already has SS evidence that some exploit reports may be revision-dependent. The PS family also has multiple separately identified commercial releases. Until disc/ROM equivalence is established, implementation-facing research should preserve the identity of the observed release rather than flattening every PS observation into one bucket.

This is especially important when researching:

- sales-license behavior;
- day/month-boundary exploits;
- UI or cursor bugs;
- save compatibility;
- any behavior that later guides describe as fixed or version-specific.

## Current implementation consequence

No gameplay code or data table should change from this note alone. This note only strengthens source hygiene and version tagging.

If a future behavior conflict appears between two PS play records, first test whether the records came from different product codes before treating one as erroneous.

## Sources

- Retro Game no Dendou / atwiki, product-code catalog for the title: https://w.atwiki.jp/yamamura2/pages/4219.html
- Suruga-ya, original PS release: https://www.suruga-ya.jp/kaitori/kaitori_detail/140000714
- Kaitori World, original PS release: https://www.kaitori-world.jp/products/detail/50511
- Kaitori World, PlayStation the Best: https://www.kaitori-world.jp/products/detail/280949
- Suruga-ya, Major Wave release: https://www.suruga-ya.jp/kaitori/kaitori_detail/140002869
- Kaitori World, Major Wave release: https://www.kaitori-world.jp/products/detail/157956
- PSX DataCenter, SLPS-00782 disc identity: https://psxdatacenter.com/games/SLPS-00782.html

## Remaining uncertainty / next verification target

Priority follow-up is not to assume a revision difference, but to verify disc identity directly or through high-quality preservation metadata for SLPS-00782 / SLPS-91104 / SLPM-86655. If hashes or executable version markers can be established lawfully without storing copyrighted game data, record only the metadata/hashes and resulting equivalence/difference conclusion.
