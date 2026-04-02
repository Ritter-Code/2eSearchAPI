from .base_extractor import BaseExtractor

def safe_int(val):
    if isinstance(val, int):
        return val
    if isinstance(val, str) and val.isdigit():
        return int(val)
    return None

class FeatExtractor(BaseExtractor):

    def extract_main(self):
        return {
            "id": self.id,
            "name": self.retrieve("name"),
            "level": safe_int(self.retrieve("system", "level", "value")),
            "category": self.retrieve("system", "category"),
            "rarity": self.retrieve("system", "traits", "rarity"),
            "action_type": self.retrieve("system", "actionType", "value"),
            "actions": safe_int(self.retrieve("system", "actions", "value"))
        }

    def extract_meta(self):
        return {
            "id": self.id,
            "source": self.retrieve("system", "publication", "title"),
            "remaster": self.retrieve("system", "publication", "remaster"),
            "license": self.retrieve("system", "publication", "license")
        }

    def extract_details(self):
        return {
            "id": self.id,
            "description": self.clean_description(self.retrieve("system", "description", "value"))
        }

    def extract_traits(self):
        results = []
        traits_list = self.retrieve("system", "traits", "value") or []
        for each in traits_list:
            results.append({
                "id": self.id,
                "trait": each
            })
        return results

    def extract_prerequisites(self):
        results = []
        prereqs = self.retrieve("system", "prerequisites", "value") or []
        for each in prereqs:
            value = each.get("value") if isinstance(each, dict) else each
            if value:
                results.append({
                    "id": self.id,
                    "prerequisite": value
                })
        return results

    def extract_all(self):
        return {
            "main": self.extract_main(),
            "meta": self.extract_meta(),
            "details": self.extract_details(),
            "traits": self.extract_traits(),
            "prerequisites": self.extract_prerequisites()
        }
