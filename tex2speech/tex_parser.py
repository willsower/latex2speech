import TexSoup
import xml.etree.ElementTree as ET
import enum
import expand_macros, expand_labels
import os
from doc_cleanup import cleanXMLString
from tex_soup_utils import seperateContents
from pybtex.database.input import bibtex

class TexParser:
    def __init__(self):
        self.latex = ET.parse('./static/pronunciation.xml').getroot()
        self.mathmode = ET.parse('./static/mathmode_pronunciation.xml').getroot()

    def parse(self, docContents, bib):
        self.output = ''
        self.envList = []
        self.inTable = False
        self.bibFile = bib
        self.path = os.getcwd() + '/upload'

        # text = file.read()
        docstr = None

        try:
            docstr = str(docContents, 'utf-8')
        except TypeError:
            docstr = docContents

        docstr = str(docstr).replace('\n', ' ')
        docstr = str(docstr).replace('\hline', '')

        doc = TexSoup.TexSoup(docstr)
        doc = expand_macros.expandDocMacros(doc)

        self._concatOutput("<speak>")
        self._parseNodeContents(doc.contents)
        self._concatOutput("</speak>")

        self.output = cleanXMLString(self.output)

        return self.output

    def _concatOutput(self, string):
        if len(self.output) == 0 or self.output[-1] == ' ':
            self.output += string
        elif len(string) == 0 or string[0] == ' ':
            self.output += string
        else:
            self.output += ' ' + string

    # Parsing .bib files helper
    def _parse_bib_file(self, name):
        for val in self.bibFile:
            if val == name + ".bib":
                fileObj = open(self.path + "/" + val, "r")
                contents = fileObj.read()
                
                parser = bibtex.Parser()
                bib_data = parser.parse_string(contents)
                self._concatOutput("<emphasis level='strong'> References Section </emphasis> <break time='1s'/>")
                
                # Looks at bib contents
                for entry in bib_data.entries.values():
                    self._concatOutput("Bibliography item is read as: <break time='0.5s'/>" + entry.key + ". Type: " + entry.type + "<break time='0.5s'/>")

                    # Gets authors
                    for en in entry.persons.keys():
                        self._concatOutput("Authors: ")
                        for author in bib_data.entries[entry.key].persons[en]:
                            self._concatOutput(str(author) + ", <break time='0.3s'/>")

                    # Gets all other key - value pairs and reads them out
                    for en in entry.fields.keys():
                        self._concatOutput(str(en) + ": " + str(bib_data.entries[entry.key].fields[en] + "<break time='0.3s'/>"))

                os.remove(self.path + "/" + val)
                break

    # Flip switch for true/false in environment
    # This might be able to done better, when printing node
    # in _nodeparseNodeContents that single node is the \begin to \end tabular
    def _checkIfInTableEnvionment(self):
        if len(self.envList) > 0 and (self.envList[-1].get('readTable') == 'true'):
            self.inTable = not self.inTable
        elif (self.inTable == True):
            self.inTable = not self.inTable
            self._concatOutput(" End table.")

    # Function that will take in new table contents, and parse
    # each column
    def _parseTableContents(self, contentsNode):
        self._concatOutput("New Row: ")
        split = str(contentsNode).split('&') 
        column = 1
        for word in split: 
            if word != "&":
                self._concatOutput(", Column " + str(column) + ", Value: " + word)
                column += 1

    def _parseMathModeToken(self, tokenNode):
        mathTokens = self._getMathTokens(tokenNode.text)
        for t in mathTokens:
            found = False
            for s in self.mathmode.findall('symb'):
                if s.get('name') == t:
                    if s.find('say_as') is not None:
                        self._concatOutput(str(s.find('say_as').text))
                    found = True
            if not found:
                self._concatOutput(str(t))

    def _getMathTokens(self, mathStr):
        class tState(enum.Enum):
            null = -1
            number = 0
            mathChar = 1
        state = -1 
        next = ""
        for c in mathStr:
            if c.isdigit() or c == '.':
                if state != tState.number:
                    if len(next):
                        yield next
                        next = "" 
                    state = tState.number
                next = next + c
            elif c.isspace() or c == '&':
                if len(next):
                    yield next
                    next = ""
                state = tState.null
            #FIX ME: This list should be obtained from mathmode somehow, not hard-coded 
            elif c in [r"*", r"+", r"-", r"/", r"=", r"<", r">", r"!"]:
                if len(next):
                    yield next
                    next = ""
                state = tState.mathChar
                yield c
            else:
                next = next + c
        
    def _parseCmdSub(self, cmdNode, cmdElem):
        if cmdElem.find('prefix') is not None:
            self._concatOutput(cmdElem.find('prefix').text)

        argIndex = 0
        for arg in cmdElem.findall('arg'):
            while argIndex < len(cmdNode.args) and not isinstance(cmdNode.args[argIndex], TexSoup.data.BraceGroup):
                argIndex += 1

            if argIndex == len(cmdNode.args):
                print("Error: Expected more arguments then given in command")
                break

            if arg.find('prefix') is not None:
                self._concatOutput(arg.find('prefix').text)
        
            if arg.get('say_contents') == 'true':
                self._parseNodeContents(cmdNode.args[argIndex].contents)
                
            if arg.find('suffix') is not None:
                self._concatOutput(arg.find('suffix').text)
        
            argIndex += 1

        if cmdElem.find('say_as') is not None:
            self._concatOutput(cmdElem.find('say_as').text)

        if cmdElem.find('suffix') is not None:
            self._concatOutput(cmdElem.find('suffix').text)

    def _parseCmd(self, cmdNode):
        found = False
        searchEnvs = []

        if len(self.envList) > 0:
            searchEnvs.append(self.envList[-1])
            if self.envList[-1].get('mathmode') == 'true':
                searchEnvs.append(self.mathmode)
            else:
                searchEnvs.append(self.latex)
        else: 
            searchEnvs.append(self.latex)

        i = 0
        while i < len(searchEnvs) and not found:
            for cmdElem in searchEnvs[i].findall('cmd'):
                if cmdElem.get('name') == cmdNode.name:
                    self._parseCmdSub(cmdNode, cmdElem)
                    found = True
            i += 1

        if cmdNode.name == 'bibliography':
            bib_name = cmdNode.args[0].contents[0]
            if len(self.bibFile) == 0:
                self._concatOutput(" There is no corresponding bibliography (dot bib file) found. ")
            else:
                if bib_name + ".bib" in self.bibFile:
                    self._parse_bib_file(bib_name)
                else:
                    self._concatOutput(" There is no corresponding bibliography (dot bib file) found. ")

        # Go down next recursive level, excluding arguments
        _,contents = seperateContents(cmdNode)
        self._parseNodeContents(contents)

    def _parseEnv(self, envNode):
        _,contents = seperateContents(envNode)
        found = False

        for envElem in self.latex.findall('env'):

            if envElem.get('name') == envNode.name:
                found = True
                self.envList.append(envElem)
                
                if envElem.find('prefix') is not None:
                    self._concatOutput(envElem.find('prefix').text)

                # Go down next recursive level, excluding arguments
                self._parseNodeContents(contents)

                if envElem.find('suffix') is not None:
                    self._concatOutput(envElem.find('suffix').text)

                self.envList.pop()
                break

        if not found:
            self._parseNodeContents(contents)

    def _parseNodeContents(self, nodeContents):
        if len(nodeContents) > 0:
            for node in nodeContents:
                if isinstance(node, TexSoup.utils.Token):
                    if len(self.envList) > 0 and (self.envList[-1].get('mathmode') == 'true'):
                        self._parseMathModeToken(node)
                    else:
                        self._checkIfInTableEnvionment() # Could be more efficient
                        if self.inTable == True:
                            self._parseTableContents(node)
                        else:
                            self._concatOutput(str(node))

                elif isinstance(node, TexSoup.data.TexNode):
                    if isinstance(node.expr, TexSoup.data.TexEnv):
                        self._parseEnv(node)
                    elif isinstance(node.expr, TexSoup.data.TexCmd):
                        self._parseCmd(node)
                    else:
                        self._parseNodeContents(node.contents)