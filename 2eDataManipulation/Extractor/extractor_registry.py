from Extractor.spell_extractor import SpellExtractor
from Extractor.ancestry_extractor import AncestryExtractor

## Referencable extractor registry to dynamically determine extractor to use
EXTRACTOR_REGISTRY = {
    "spell" : SpellExtractor,
    "ancestry" : AncestryExtractor
}