import requests, json, logging as log, os
# from dataclasses import dataclass
log.basicConfig(level=log.INFO)

class Entry:
    """ stores values from dictonary API """
    def __init__(self, entry):
        self.rawData: dict = entry
        self.word: str
        self.definitions: list
        self.origin: str
        self.phonetic: str
        self.__conv(entry)
    
    def __conv(self, entry: str):
        """ extracts relevant data from JSON into entry structure """
        self.word = entry[0]["word"]
        self.definitions = entry[0]["meanings"][0]["definitions"]
        self.origin = entry[0].get("origin", None)
        self.phonetic = entry[0].get("phonetic", None)
        log.debug("convertion successful")

    def __str__(self) -> str:
        """ string format """
        definitions = '\n\n'.join("- " + d['definition'] for d in self.definitions)
        return f"""\
Word: {self.word}
Origin: {self.origin if self.origin else "Unknown"}
Phonetic: {self.phonetic if self.phonetic else "Unknown"}
===Definition(s)===
{definitions}
        """

    def __repl__(self) -> str:
        """ REPL format 
        
        returns raw data from dictionary"""
        return json.dumps(self.rawData, indent = 2)

# TODO rework local storage format to more efficently store relevant data
class Buffer:
    """   allows dictionary entries to be stored locally to minimize API calls   """
    # name of directory used to store entries on local disk
    BUFFER_DIR: str = "buffer" 

    def __init__(self):
        self.dict = dict()
        self.__load_all()

    def contains(self, word: str) -> bool:
        """ returns true if file in buffer """
        return word in self.dict

    def get(self, word: str) -> Entry:
        """ returns entry for word from buffer
        
        will return KeyError if word not in buffer """
        if self.contains(word):
            return self.dict[word]
        else:
            raise KeyError("word not in buffer")

    def add(self, entry: Entry):
        """ adds new entries to buffer
        
        TypeError is raised argument is not of type Entry """
        if type(entry) != Entry:
            raise TypeError("must be of type entry")
        self.dict[entry.word] = entry

    def load(self, filename: str):
        """ loads API files, converts them to Entry format, and stores in buffer
        
        ValueError is raised if conversion to Entry fails
        """
        file_path = os.path.join(Buffer.BUFFER_DIR, filename)
        with open(file_path, "r") as f:
            try:
                entry = Entry(json.loads(f.read()))
                self.dict[entry.word] = entry
            except:
                raise ValueError("invalid file in buffer directory")

    def save(self, entry: Entry):
        """ saves entry to local disk """
        file_path = os.path.join(Buffer.BUFFER_DIR, f"{entry.word}.json")
        with open(file_path, "w") as f:
            f.write(json.dumps(entry.rawData))

    def __load_all(self):
        """ loads alls files in buffer directory

        invalid files are ignored. """
        if not os.path.isdir(Buffer.BUFFER_DIR):
            os.mkdir(Buffer.BUFFER_DIR)
            return
        for f in os.scandir(Buffer.BUFFER_DIR):
            if f.is_file() and f.name.endswith(".json"):
                try:
                    self.load(f)
                except:
                    continue # ignore invalid files on load
        


# https://api.dictionaryapi.dev/api/v2/entries/en/
def __get_entry_from_api(word):
    """ grabs word from dictionary API.
    
    If word not found, raises keyerror """
    with requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}") as r:
        if r.status_code == 200:
            return r.json()
        else:
            raise KeyError("word not found")
    

def search(word, buffer:Buffer = None):
    """ returns the dicitonary entry for word.
    If word not found, returns None
    Optional """
    # dummy entry 
    if buffer and buffer.contains(word):
        return buffer.get(word)

    try:
        result_json = __get_entry_from_api(word)
        entry = Entry(result_json)
    except:
        # if no valid entry found, return none
        return None
    
    if buffer:
        buffer.add(entry)
        buffer.save(entry)
    
    return entry



    







