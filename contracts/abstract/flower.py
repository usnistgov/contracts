import yaml
import zipfile
import io
import glob
import logging
import os
import re
import json
import click

LOGGER = logging.getLogger(__name__)

class Flower:
    def __init__(self, id='unknown', spec='spec.yaml'):
        self.parsable = ['json', 'xml', 'yaml', 'md', 'csv', 'txt']
        self.guesses = {}
        ## @ refer to a node, ~ refer to a ransition.
        ## the difference in nodes here just expresses a scope difference.
        ## Thus, when we go from a node1 to node2 and back to node2 it does not means that we come back to the same
        metadata = {'@root':{}}
        metadata['@root'] = {'~start':{}}
        metadata['@root']['~start'] = {'@node1':{}}
        metadata['@root']['~start']['@node1'] = {'~open':[{'@node2':{}}]}
        metadata['@root']['~start']['@node1']['~open'][0]['@node2'] = {'~open':'@node1', '~parse':{}}
        metadata['@root']['~start']['@node1']['~open'][0]['@node2']['~parse']= {'@node3':{}}
        metadata['@root']['~start']['@node1']['~open'][0]['@node2']['~parse']['@node3']= {'~parse':[{'@node4':{}}]}
        metadata['@root']['~start']['@node1']['~open'][0]['@node2']['~parse']['@node3']['~parse'][0]['@node4']= {'~parse':'@node3', '~load':'@leaf'}

        raw = {'@root':{}}
        raw['@root'] = {'~start':{}}
        raw['@root']['~start'] = {'@node1':{}}
        raw['@root']['~start']['@node1'] = {'~open':[{'@node2':{}}]}
        raw['@root']['~start']['@node1']['~open'][0]['@node2'] = {'~open':'@node1', '~read':{}}
        raw['@root']['~start']['@node1']['~open'][0]['@node2']['~read'] = {'@node3':{}}
        raw['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3'] = {'~parse':{}, '~none':'@leaf'}
        raw['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3']['~parse'] = {'@node5':{}}
        raw['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3']['~parse']['@node5']= {'~parse':[{'@node6':{}}]}
        raw['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3']['~parse']['@node5']['~parse'][0]['@node6'] = {'~parse':'@node5', '~load':'@node3'}

        hybrid = {'@root':{}}
        hybrid['@root'] = {'~start':{}}
        hybrid['@root']['~start'] = {'@node1':{}}
        hybrid['@root']['~start']['@node1'] = {'~open':[{'@node2':{}}]}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2'] = {'~open':'@node1', '~read':{}, '~parse':{}}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~read'] = {'@node3':{}}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3'] = {'~parse':{}, '~none':'@leaf'}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3']['~parse'] = {'@node5':{}}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3']['~parse']['@node5']= {'~parse':[{'@node6':{}}]}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~read']['@node3']['~parse']['@node5']['~parse'][0]['@node6'] = {'~parse':'@node5', '~load':'@node3'}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~parse']= {'@node3':{}}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~parse']['@node3']= {'~parse':[{'@node4':{}}]}
        hybrid['@root']['~start']['@node1']['~open'][0]['@node2']['~parse']['@node3']['~parse'][0]['@node4']= {'~parse':'@node3', '~load':'@leaf'}

        self.id = id
        self.spec = self.read_yaml(spec)

    def read_yaml(self, filepath):
        """
        Read a YAML file and returns the corresponding dictionary.

        :param filepath: The path to the YAML file.
        :returns: A dictionary of the YAML file.
        """
        LOGGER.debug('Reading in YAML file: {}'.format(filepath))
        data = {}
        with open(filepath) as stream:
            data = yaml.safe_load(stream)
        return data

    def classify(self):
        # Determine if it is a metadata, raw or hybrid flower.
        # This allows us to determine immediate relevance between representation.
        # Migrating a metadata representation to a raw one is more complicated that a raw to a raw. Or presumably.
        return 'hybrid'

    def extract(self, zippedFile, toFolder):
        """ Unzip a zip file and its contents, including nested zip files
            Delete the zip file(s) after extraction
        """
        with zipfile.ZipFile(zippedFile, 'r') as zfile:
            zfile.extractall(path=toFolder)
        pathTo = "{}/{}".format(toFolder, zippedFile.split('.zip')[0])
        listOfFile = os.listdir(pathTo)
        for entry in listOfFile:
            if '.zip' in entry:
                self.extract(entry, toFolder)

    def open(self, precedence={}, record='./record'):
        # create a list of file and sub directories
        # names in the given directory
        listOfFile = glob.glob(record+"/*")
        # Iterate over all the entries
        read = False
        parse = False
        precedence['~open'] = {}
        for entry in listOfFile:
            # Create full path
            key_entry = entry
            fullPath = os.path.join(record, entry)
            # print(fullPath)
            # print(entry)
            # If entry is a directory then get the list of files in this directory
            if not os.path.isdir(entry):
                if any('.{}'.format(ext) in fullPath for ext in self.parsable):
                    precedence['~open'][key_entry] = {'~parse':{key_entry:{}}}
                    ## open file and parse key value and indicate
                    self.parse(precedence['~open'][key_entry]['~parse'][key_entry], entry)
                    if not parse:
                        parse = True
                else:
                    precedence['~open'][key_entry] = {'~read':{key_entry:{}}}
                    ## check the mime type to see if we can turn this to a parsable format.
                    ## for example xls, doc, html,
                    self.read(precedence['~open'][key_entry]['~read'][key_entry], entry)
                    if not read:
                        read = True
                if read and parse:
                    if entry.count('/') in self.guesses.keys():
                        self.guesses[entry.count('/')].append('hybrid')
                    else:
                        self.guesses[entry.count('/')] = ['hybrid']
                elif read and not parse:
                    if entry.count('/') in self.guesses.keys():
                        self.guesses[entry.count('/')].append('raw')
                    else:
                        self.guesses[entry.count('/')] = ['raw']
                elif not read and parse:
                    if entry.count('/') in self.guesses.keys():
                        self.guesses[entry.count('/')].append('metadata')
                    else:
                        self.guesses[entry.count('/')] = ['metadata']
                else:
                    if entry.count('/') in self.guesses.keys():
                        self.guesses[entry.count('/')].append('empty')
                    else:
                        self.guesses[entry.count('/')] = ['empty']
            else:
                precedence['~open'][key_entry] = {}
                self.open(precedence['~open'][key_entry], entry)

    def read(self, precedence={}, file='./file'):
        pass

    def load(self, precedence={}, content=None):
        pass

    def parse(self, precedence={}, parsable='./parsable.ext'):
        print(parsable)
        if '.json' in parsable:
            try:
                with open(parsable, "r") as parsed:
                    content = json.loads(parsed.read())
            except:
                content = {}
        else:
            content = {}
        precedence['~parse'] = {}
        for key, value in content.items():
            precedence['~parse'][parsable+"/"+key] = {}
            self.load(precedence['~parse'][parsable+"/"+key], value)

    def verify(self, record="record.zip"):
        # Apply the spec to a record.
        self.extract(record, '.')
        skeleton = {}
        skeleton[record.split('.zip')[0]]= {}
        skeleton[record.split('.zip')[0]]['~open']= {}
        type = self.open(skeleton[record.split('.zip')[0]], record.split('.zip')[0])
        # print(json.dumps(skeleton, sort_keys=True, indent=4, separators=(',', ': ')))
        if any('hybrid' in vs for vs in self.guesses.values()):
            skeleton['representation'] = 'hybrid'
        else:
            guessed = self.guesses.values()[0][0]
            if any(guessed not in vs for vs in self.guesses.values()):
                skeleton['representation'] = 'hybrid'
            else:
                skeleton['representation'] = guessed
        with open('record.yml', 'w') as outfile:
            yaml.dump(skeleton, outfile, default_flow_style=False)


@click.command()
@click.option('--tool', default=None, help="The tool spec.")
@click.option('--record', default=None, help="The tool record")

def main(tool, record):
    if tool is None:
        print("You must provide a tool spec.")
    elif record is None:
        print("You must provide a record.")
    else:
        flower = Flower(id='{}'.format(tool.split('.yaml')[0]), spec=tool)
        flower.verify(record)
