
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
    
