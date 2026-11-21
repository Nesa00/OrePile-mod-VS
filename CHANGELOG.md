## Changelog

### v1.0.0
- **512-Capacity Ground Storage:** Upgraded ground storage for all raw ore nuggets (`nugget-*`) and smelted metal bits/alloys (`metalbit-*`) to hold up to 512 items in a single `1×1×1` block[cite: 3].
- **1:1 Visual Dome Model:** Replaced default messy layouts with a non-overlapping, inward-stepped 3D dome pile (`nugget-pile.json`, generated with seed `841027957`) rendering every individual nugget at full scale (`1.0`)[cite: 3].
- **Accurate Block Bounds & Vanilla Behavior:** Calibrated dynamic hitbox scaling (`cbScaleYByLayer: 0.021`) to match the dome's height while preserving vanilla placement sounds and `ArtPigment` cave-painting behaviors on hematite and limonite[cite: 3].