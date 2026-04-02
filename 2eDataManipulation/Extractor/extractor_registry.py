from Extractor.spell_extractor import SpellExtractor
from Extractor.ancestry_extractor import AncestryExtractor
from Extractor.feat_extractor import FeatExtractor

## Referencable extractor registry to dynamically determine extractor to use
EXTRACTOR_REGISTRY = {
    "spell" : SpellExtractor,
    "ancestry" : AncestryExtractor,
    "feat" : FeatExtractor
}