import sublime
import sublime_plugin
import datetime
import os
import logging
import shutil
import string
import re

log = logging.getLogger(__name__)

cur1 = re.compile('\\$0')

# A really quick and dirty template mechanism.
# Stolen from: https://makina-corpus.com/blog/metier/2016/the-worlds-simplest-python-template-engine
#              https://github.com/ebrehault/superformatter
class TemplateFormatter(string.Formatter):
    def __init__(self, resolver=None):
        super(TemplateFormatter, self).__init__()
        self.resolver = resolver
    def format_field(self, value, spec):
        # REPITITION
        #>>> sf.format('''Table of contents:
        #{chapters:repeat:Chapter {{item}}
        #}''', chapters=["I", "II", "III", "IV"])
        #'''Table of contents:
        #Chapter I
        #Chapter II
        #Chapter III
        #Chapter IV
        #'''
        if spec.startswith('repeat'):
            template = spec.partition(':')[-1]
            if type(value) is dict:
                value = value.items()
            return ''.join([template.format(item=item) for item in value])
        # FUNCTION CALLS
        #>>> sf.format('My name is {name.upper:call}', name="eric")
        #'My name is ERIC'
        elif spec == 'call':
            return value()
        # OPTIONAL EXPANSION
        #>>> sf.format('Action: Back / Logout {manager:if:/ Delete {id}}', manager=True, id=34)
        #'Action: Back / Logout / Delete 34'        
        elif spec.startswith('if'):
            return (value and spec.partition(':')[-1]) or ''
        else:
            return super(TemplateFormatter, self).format_field(value, spec)
    def get_value(self, key, args, kwargs):
        if(str(key)):
            if(key in kwargs):
                return kwargs[key]
            if(self.resolver):
                return str(self.resolver(key,None))
            return None
        else:
            return args[key]

def ExpandTemplate(view, template, format={},resolver=None):
    # Supported expansions
    formatDict = {
    "date": str(datetime.date.today()),
    "time": datetime.datetime.now().strftime("%H:%M:%S"),
    #"datetime": str(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
    "datetime": str(datetime.datetime.now().strftime("%Y-%m-%d %a %H:%M")),
    "file": str(view.file_name()),
    "clipboard": sublime.get_clipboard()
    }

    if(format != None):
        formatDict.update(format) 

    formatter = TemplateFormatter(resolver)
    template  = formatter.format(template, **formatDict)

    global cur1
    mat = cur1.search(template)
    pos = -1
    if(mat != None):
    	pos = mat.start(0)
    	template = cur1.sub('',template)
    return (template, pos)


class ASettings:
	def __init__(self, settingsName):
		self.settingsName = settingsName
		self.settings = sublime.load_settings(settingsName + '.sublime-settings')

	def Get(self, name, defaultVal):
		val = self.settings.get(name)
		if(val == None):
			val = defaultVal
		return val

	def Set(self, name, val):
		self.settings.set(name,val)
		sublime.save_settings(self.settingsName + '.sublime-settings')


# Singleton access
configFilename    = "dnd"
_sets = None

def Load():
	global configFilename
	global _sets
	_sets          = ASettings(configFilename)


def Get(name, defaultValue, formatDictionary = None):
	global _sets
	if(_sets == None):
		log.warning("SETTINGS IS NULL? IS THIS BEING CALLED BEFORE PLUGIN START?")
		Load()
	rv = _sets.Get(name, defaultValue)
	formatDict = {
		"date":     str(datetime.date.today()),
		"time":     datetime.datetime.now().strftime("%H:%M:%S"),
		"datetime": str(datetime.datetime.now().strftime("%Y-%m-%d %a %H:%M")),
	}

	if(formatDictionary != None):
		formatDict.update(formatDictionary)

	if(str == type(rv)):
		formatter = TemplateFormatter(Get)
		rv  = formatter.format(rv, **formatDict)
	if(list == type(rv)):
		formatter = TemplateFormatter(Get)
		rv = [ (formatter.format(r, **formatDict) if str == type(r) else r) for r in rv ]
	return rv

def Set(key, val):
	if(_sets == None):
		Load()
	_sets.Set(key,val)

def RepresentsInt(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False	

def GetInt(name, defaultValue):
	v = Get(name, defaultValue)
	try:
		i = int(v)
		return i
	except:
		return defaultValue




