import sublime
import sublime_plugin
import dnd.sets as sets
from datetime import datetime as dt
import os
from functools import wraps # This convenience func preserves name and docstring


# Decorator that helps me extend classes.
# I am using this to extend sublime a bit
# and add some mechanisms to orgparse without
# adding sublime specific components to node.
def add_method(cls):
    def decorator(func):
        setattr(cls, func.__name__, func)
    return decorator


@add_method(sublime.View)
def curRow(self):
	return self.rowcol(self.sel()[0].begin())[0]

class DndInsertCombatCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		id = sets.GetInt("currentCombatId",1)
		sets.Set("currentCombatId", str(id + 1))
		plys = sets.Get("players",[{"name": "Ply1", "ac": 10, "starthealth": 13}])
		n = dt.now()
		nstr = n.strftime("%d_%m_%Y %H_%M")
		tables =  "* Combat Event " + str(nstr) + "\n"
		tables += "** Combat Action"
		tables += "   #NAME: " + str(id) + "-Combat-Action\n"
		tables += "   | PC | Damage | |\n"
		tables += "   |-\n"
		for ply in plys:
			tables += "   |{name}| 0| |\n".format(name=ply['name'])
		tables += "   |-\n"
		tables += "   | Hit | Who | For |\n"
		tables += "   |-\n"
		tables += "   | | | |\n"
		endps = 1+len(plys)
		tables += "   #+TBLFM: @2$2..@{endps}$2=vsumifeq($2,$1,@{actionsps}$3..@>$3,'b_or')\n".format(endps=str(endps), actionsps=str(endps+2))
		tables += "\n"
		tables += "** Player Info\n"
		tables += "   #+NAME: " + str(id) + "-Player-Stats\n"
		tables += "   | Player | Start Health | Temp Hits | AC | Damage | Cur HP | Initiative |\n"
		tables += "   |-\n"
		cmbpull = ""
		row = 2
		for ply in plys:
			tables += "   |{name}| {starthealth}|0 |{ac}|0|0||\n".format(name=ply['name'],starthealth=ply['starthealth'],ac=ply['ac'])
			if cmbpull != "":
				cmbpull += "::"
			cmbpull += "@{row}$5=remote('{id}-Combat-Action',@{row}$2)".format(row=row,id=id)
		tables += "   #+TBLFM:{cmbpull}::$6=($2+$3)-$5::$6=gradient($6,($6/$2)*100.0,\"red\",\"orange\",\"yellow\",\"cyan\",\"green\")\n".format(cmbpull=cmbpull)
		tables += "\n"
		tables += "** Monsters\n"
		tables += "   #+NAME: " + str(id) + "-Monster-Stats\n"
		tables += "   | Name | Start Health | Damage | Cur HP | AC | Initiative |\n"
		tables += "   |-\n"
		tables += "   |||||||\n"
		cmbpull = ""#"@3$3=remote('Combat-Action',@5$2)"
		tables += "   #+TBLFM:{cmbpull}::$4=gradient($4,($4/$2)*100.0, \"red\",\"orange\",\"yellow\",\"cyan\",\"green\")\n".format(cmbpull=cmbpull)
		row = self.view.curRow()
		t1 = row + 3
		t2 = t1 + len(plys) + 10
		t3 = t2 + len(plys) +  6
		self.view.insert(edit, self.view.sel()[0].begin(), tables)

		pt = self.view.text_point(t1, 0)
		self.view.sel().clear()
		self.view.sel().add(pt)
		self.view.run_command('table_editor_align')

		pt = self.view.text_point(t2, 0)
		self.view.sel().clear()
		self.view.sel().add(pt)
		self.view.run_command('table_editor_align')

		pt = self.view.text_point(t3, 0)
		self.view.sel().clear()
		self.view.sel().add(pt)
		self.view.run_command('table_editor_align')

