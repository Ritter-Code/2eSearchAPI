# 2eSearchAPI

A full ETL pipeline and REST API for Pathfinder Second Edition data sourced from FoundryVTT PF2e JSON documents. Normalizes deeply nested, inconsistently structured JSON into relational Parquet datasets and serves them via a FastAPI + DuckDB backend.

**Live API:** [https://twoesearchapi.onrender.com/docs](https://twoesearchapi.onrender.com/docs)

---

## Overview

FoundryVTT stores PF2e content as deeply nested JSON intended for UI consumption rather than querying or search. This project converts that data into relational, schema-stable Parquet datasets and exposes them through a FastAPI search API.

---

## Architecture

### Extractor Framework

Each PF2e entity type is parsed by a dedicated extractor class implementing core functions for a base extractor class managing:
- Safe nested JSON access
- Consistent ID handling
- Description cleaning (strips HTML, Foundry roll commands, and UUID references)
- A standard extract_all interface

Extractor selection is handled by a registry-based dispatcher referencing the 'type' field present in each significant file.

Currently implemented: spell, ancestry, feat

### Pipeline

The pipeline is fully idempotent. On each run it:
1. Loads a committed ledger of previously processed files
2. Skips any file whose content hash matches a committed entry
3. Extracts and normalizes only new or changed files
4. Writes outputs as Parquet files batched by run timestamp
5. Records the result of every file (IN_PROGRESS, STAGED, COMMITTED, or FAILED) to a persistent ledger

Data is sourced from the FoundryVTT PF2e GitHub repository (v13-dev branch) via a sparse checkout that pulls only the `packs/pf2e/` directory.

### Schema Normalization

Spell tables: main, meta, details, damage, heightening, heighten_interval, heighten_level, heighten_level_damage, traits, traditions, ritual

Ancestry tables: main, meta, boosts, flaw, traits, languages, additional_languages, race_features

Feat tables: main, meta, details, traits, prerequisites

Each table is written as an independent Parquet file under Content/{type}/{table}/.

### API

Built with FastAPI and DuckDB. On startup, DuckDB registers each Parquet file as an in-memory view, making all tables immediately queryable without loading data into memory upfront. Deployed on Render.

Current endpoints:

**Spells**
- `GET /spells/` — all spells with name, level, traditions, traits, and truncated description
- `GET /spells/filter` — filter by level_min, level_max, tradition, trait, action
- `GET /spells/{name}` — full spell detail including damage, heightening, and ritual data

**Ancestries**
- `GET /ancestry/` — all ancestries sorted by rarity
- `GET /ancestry/filter` — filter by rarity, hp, size, boost
- `GET /ancestry/{name}` — full ancestry detail including boosts, traits, languages, and race features

**Feats**
- `GET /feats/` — all feats with name, level, category, traits
- `GET /feats/filter` — filter by level_min, level_max, category, rarity, trait, action_type
- `GET /feats/{name}` — full feat detail including prerequisites and description

---

## Output Structure

```
Content/
  spell/
    main/
    meta/
    details/
    damage/
    heightening/
    heighten_interval/
    heighten_level/
    heighten_level_damage/
    traits/
    traditions/
    ritual/
  ancestry/
    main/
    meta/
    boosts/
    flaw/
    traits/
    languages/
    additional_languages/
    race_features/
  feat/
    main/
    meta/
    details/
    traits/
    prerequisites/
  metadata/
    ledger/
```

---

## Current Status

- Spell, ancestry, and feat extractors complete
- Idempotent pipeline with hash-based change detection and ledger tracking
- Description artifact cleaning to remove HTML, Foundry UUID references, roll commands, damage formulas, and area templates
- FastAPI running with DuckDB view layer over Parquet files
- List, detail, and filter endpoints for spells, ancestries, and feats
- Deployed on Render

## Planned Work

- Additional entity extractors (equipment, conditions, backgrounds, etc.)
- AI-assisted querying

---

## Design Decisions

Extraction Process: Early iterations normalized each entity type into a single wide dataframe. Processing times ballooned due to UUID reference expansion, and flattened tables created significant query complexity. Restructuring into relational tables with one-to-one and one-to-many relationships reduced processing from hours to minutes and made the data meaningfully queryable.

Change Detection: A hash-based detection system combined with continuous ledger tracking prevents reprocessing already committed files. The content hash determines whether a file has changed since its last committed run, ensuring updated files are caught without reprocessing the entire dataset.

DuckDB: DuckDB queries Parquet files directly without a maintained server, integrates cleanly with the existing pipeline, and handles the read-heavy workload efficiently.

## Technologies

- Python
- FastAPI
- DuckDB
- PyArrow / Parquet
- Pandas
- Orjson
- GitPython

## Dependencies

API: `requirements.txt`
Pipeline: `requirements-Pipeline.txt`

## Community Use Disclosure
This project uses trademarks and/or copyrights owned by Paizo Inc., used under Paizo's Community Use Policy (paizo.com/communityuse). We are expressly prohibited from charging you to use or access this content.
