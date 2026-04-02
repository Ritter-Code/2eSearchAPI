
import re
## Universal extractor method for use in extractors

class BaseExtractor:
    
    ## Initialize with full json file, and specifically call the _id and system information
    def __init__ (self, obj):
        self.obj = obj
        self.sys = obj.get("system", {})
        self.id = obj.get("_id")

    ## Retrieve data in nested json cleanly
    def retrieve(self, *path):

        step = self.obj

        for each in path:
            if not isinstance(step, dict):
                return None
            step = step.get(each)
        
        return step
    
    def clean_description(self, text):
        if not text:
            return text
        # @UUID with label --> keep label
        text = re.sub(r'@UUID\[[^\]]+\]\{([^}]+)\}', r'\1', text)
        # @UUID journal entry without label --> strip entirely
        text = re.sub(r'@UUID\[Compendium\.[^.]+\.journals\.[^\]]+\]', '', text)
        # @UUID without label --> extract name (last segment)
        text = re.sub(r'@UUID\[Compendium\.[^.]+\.[^.]+\.[^.]+\.([^\]]+)\]', r'\1', text)
        # @Check with label --> keep label
        text = re.sub(r'@Check\[[^\]]+\]\{([^}]+)\}', r'\1', text)
        # @Check without label --> strip entirely
        text = re.sub(r'@Check\[[^\]]+\]', '', text)
        # @Template with label --> keep label
        text = re.sub(r'@Template\[[^\]]+\]\{([^}]+)\}', r'\1', text)
        # @Template without label --> "N-foot type"
        text = re.sub(r'@Template\[(?:type:)?(\w+)\|distance:(\d+)[^\]]*\]', r'\2-foot \1', text)
        # @Damage with type --> "formula type"
        text = re.sub(r'@Damage\[([^\[]+)\[([^\]]+)\]', lambda m: m.group(1).replace('@item.level', 'spell level').replace('@item.rank', 'spell level').strip() + ' ' + m.group(2), text)
        # @Damage without type --> just formula
        text = re.sub(r'@Damage\[([^\]]+)\]', lambda m: m.group(1).replace('@item.level', 'spell level').replace('@item.rank', 'spell level').strip(), text)
        # [[/r formula #label]] and [[/gmr formula #label]] roll commands --> "formula label"
        text = re.sub(r'\[\[/(?:r|gmr) \{?([^\s#\]{}]+)\}?(?:\s+#([^\]]+))?\]\]', lambda m: (m.group(1) + ' ' + m.group(2) if m.group(2) else m.group(1)), text)
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
