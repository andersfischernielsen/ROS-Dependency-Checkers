import os
import sys
import types

PINLINED_DEFAULT_PACKAGE = ''
PINLINER_MODULE_NAME = 'pinliner_loader'
loader_version = '0.2.0'

FORCE_EXC_HOOK = None

inliner_importer_code = '''
import imp
import marshal
import os
import struct
import sys
import types


class InlinerImporter(object):
    version = '%(loader_version)s'
    def __init__(self, data, datafile, set_excepthook=True):
        self.data = data
        self.datafile = datafile
        if set_excepthook:
            sys.excepthook = self.excepthook

    @staticmethod
    def excepthook(type, value, traceback):
        import traceback as tb
        tb.print_exception(type, value, traceback)

    def find_module(self, fullname, path):
        module = fullname in self.data
        if module:
            return self

    def get_source(self, fullname):
        __, start, end, ts = self.data[fullname]
        with open(self.datafile) as datafile:
            datafile.seek(start)
            code = datafile.read(end - start)
        return code

    def get_code(self, fullname, filename):
        py_ts = self.data[fullname][3]
        try:
            with open(fullname + '.pyc', 'rb') as pyc:
                pyc_magic = pyc.read(4)
                pyc_ts = struct.unpack('<I', pyc.read(4))[0]
                if pyc_magic == imp.get_magic() and pyc_ts == py_ts:
                    return marshal.load(pyc)
        except:
            pass

        code = self.get_source(fullname)
        compiled_code = compile(code, filename, 'exec')

        try:
            with open(fullname + '.pyc', 'wb') as pyc:
                pyc.write(imp.get_magic())
                pyc.write(struct.pack('<I', py_ts))
                marshal.dump(compiled_code, pyc)
        except:
            pass
        return compiled_code

    def load_module(self, fullname):
        # If the module it's already in there we'll reload but won't remove the
        # entry if we fail
        exists = fullname in sys.modules

        module = types.ModuleType(fullname)
        module.__loader__ = self

        is_package = self.data[fullname][0]
        path = fullname.replace('.', os.path.sep)
        if is_package:
            module.__package__ = fullname
            module.__file__ = os.path.join(path, '__init__.py')
            module.__path__ = [path]
        else:
            module.__package__ = fullname.rsplit('.', 1)[0]
            module.__file__ = path + '.py'

        sys.modules[fullname] = module

        try:
            compiled_code = self.get_code(fullname, module.__file__)
            exec compiled_code in module.__dict__
        except:
            if not exists:
                del sys.modules[fullname]
            raise

        return module
''' % {'loader_version': loader_version}

'''
#!/usr/bin/python
#################################################################
##\file
#
# \note
#   Copyright (c) 2010 \n
#   Fraunhofer Institute for Manufacturing Engineering
#   and Automation (IPA) \n\n
#
#################################################################
#
# \note
#   Project name: care-o-bot
# \note
#   ROS stack name: cob_apps
# \note
#   ROS package name: cob_command_gui
#
# \author
#   Author: Florian Weisshardt, email:florian.weisshardt@ipa.fhg.de
# \author
#   Supervised by: Florian Weisshardt, email:florian.weisshardt@ipa.fhg.de
#
# \date Date of creation: Aug 2010
#
# \brief
#   Implementation of ROS node for command gui.
#
#################################################################
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#     - Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer. \n
#     - Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution. \n
#     - Neither the name of the Fraunhofer Institute for Manufacturing
#       Engineering and Automation (IPA) nor the names of its
#       contributors may be used to endorse or promote products derived from
#       this software without specific prior written permission. \n
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License LGPL as 
# published by the Free Software Foundation, either version 3 of the 
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License LGPL for more details.
# 
# You should have received a copy of the GNU Lesser General Public 
# License LGPL along with this program. 
# If not, see <http://www.gnu.org/licenses/>.
#
#################################################################

import rospy
from simple_script_server import *

## Implements configurable buttons
class command_gui_buttons:
	def __init__(self):
		self.sss = simple_script_server()
		self.panels = []
		self.stop_buttons = []
		self.init_buttons = []
		self.recover_buttons = []
		self.halt_buttons = []
		self.CreateControlPanel()

	## Creates the control panel out of configuration from ROS parameter server
	def CreateControlPanel(self):
		param_prefix = "~control_buttons"
		if not rospy.has_param(param_prefix):
			rospy.logerr("parameter %s does not exist on ROS Parameter Server, aborting...",param_prefix)
			return False
		group_param = rospy.get_param(param_prefix)
		#print group_param
		group_param = self.SortDict(group_param)
		#print group_param
		
		for group in group_param:
			group_name = group[1]["group_name"]
			component_name = group[1]["component_name"] # \todo check component name with robot_components.yaml files
			button_list = group[1]["buttons"]
			buttons = []
			for button in button_list:
				#print "button = ",button
				if button[1] == "move":
					buttons.append(self.CreateButton(button[0],self.sss.move,component_name,button[2]))
				elif button[1] == "move_base_rel":
					buttons.append(self.CreateButton(button[0],self.sss.move_base_rel,component_name,button[2]))
				elif button[1] == "trigger":
					buttons.append(self.CreateButton(button[0],self.sss.trigger,component_name,button[2]))
					if button[2] == "stop":
						self.stop_buttons.append(component_name)
					if button[2] == "init":
						self.init_buttons.append(component_name)
					if button[2] == "recover":
						self.recover_buttons.append(component_name)
					if button[2] == "halt":
						self.halt_buttons.append(component_name)
				elif button[1] == "stop":
					buttons.append(self.CreateButton(button[0],self.sss.stop,component_name))
					self.stop_buttons.append(component_name)
				elif button[1] == "init":
					buttons.append(self.CreateButton(button[0],self.sss.init,component_name))
					self.init_buttons.append(component_name)
				elif button[1] == "recover":
					buttons.append(self.CreateButton(button[0],self.sss.recover,component_name))
					self.recover_buttons.append(component_name)
				elif button[1] == "halt":
					buttons.append(self.CreateButton(button[0],self.sss.halt,component_name))
					self.halt_buttons.append(component_name)
				else:
					rospy.logerr("Function <<%s>> not known to command gui",button[1])
					return False
			group = (group_name,buttons)
			
			# add nav buttons (optional)
			if component_name == "base": # \todo get base name from robot_components.yaml
				param_prefix = "~nav_buttons"
				if rospy.has_param(param_prefix):
					nav_buttons_param = rospy.get_param(param_prefix)
					nav_button_list = nav_buttons_param["buttons"]
					#print nav_button_list
					for button in nav_button_list:
						#print "button = ",button
						buttons.append(self.CreateButton(button[0],self.sss.move,component_name,button[2]))
				else:
					rospy.logwarn("parameter %s does not exist on ROS Parameter Server, no nav buttons will be available.",param_prefix)
			self.panels.append(group)

		# uniqify lists to not have double entries
		self.stop_buttons = self.uniqify_list(self.stop_buttons)
		self.init_buttons = self.uniqify_list(self.init_buttons)
		self.recover_buttons = self.uniqify_list(self.recover_buttons)
		self.halt_buttons = self.uniqify_list(self.halt_buttons)
		
	
	## Creates one button with functionality
	def CreateButton(self,button_name,function,component_name,parameter_name=None):
		if parameter_name == None:
			button = (button_name,function,(component_name,False))
		else:
			button = (button_name,function,(component_name,parameter_name,False))
		return button
	
	## Sorts a dictionary alphabetically
	def SortDict(self,dictionary):
		keys = sorted(dictionary.iterkeys())
		k=[]
		#print "keys = ", keys
		#for key in keys:
		#	print "values = ", dictionary[key]
		return [[key,dictionary[key]] for key in keys]
		
	## Uniqifies a list to not have double entries
	def uniqify_list(self,seq, idfun=None): 
		# order preserving
		if idfun is None:
			def idfun(x): return x
		seen = {}
		result = []
		for item in seq:
			marker = idfun(item)
			# in old Python versions:
			# if seen.has_key(marker)
			# but in new ones:
			if marker in seen: continue
			seen[marker] = 1
			result.append(item)
		return result
from command_gui_buttons import *
'''


inliner_packages = {
    "": [
        1, 9442, 9476, 1551826111],
    "command_gui_buttons": [
        0, 2778, 9442, 1551826111]
}


def prepare_package():
    # Loader's module name changes withh each major version to be able to have
    # different loaders working at the same time.
    module_name = PINLINER_MODULE_NAME + '_' + loader_version.split('.')[0]

    # If the loader code is not already loaded we create a specific module for
    # it.  We need to do it this way so that the functions in there are not
    # compiled with a reference to this module's global dictionary in
    # __globals__.
    module = sys.modules.get(module_name)
    if not module:
        module = types.ModuleType(module_name)
        module.__package__ = ''
        module.__file__ = module_name + '.py'
        exec inliner_importer_code in module.__dict__
        sys.modules[module_name] = module

    # We cannot use __file__ directly because on the second run __file__ will
    # be the compiled file (.pyc) and that's not the file we want to read.
    filename = os.path.splitext(__file__)[0] + '.py'

    # Add our own finder and loader for this specific package if it's not
    # already there.
    # This must be done before we initialize the package, as it may import
    # packages and modules contained in the package itself.
    for finder in sys.meta_path:
        if (isinstance(finder, module.InlinerImporter) and
                finder.data == inliner_packages):
            importer = finder
    else:
        # If we haven't forced the setting of the uncaught exception handler
        # we replace it only if it hasn't been replace yet, this is because
        # CPython default handler does not use traceback or even linecache, so
        # it never calls get_source method to get the code, but for example
        # iPython does, so we don't need to replace the handler.
        if FORCE_EXC_HOOK is None:
            set_excepthook = sys.__excepthook__ == sys.excepthook
        else:
            set_excepthook = FORCE_EXC_HOOK

        importer = module.InlinerImporter(inliner_packages, filename,
                                          set_excepthook)
        sys.meta_path.append(importer)

    __, start, end, ts = inliner_packages[PINLINED_DEFAULT_PACKAGE]
    with open(filename) as datafile:
        datafile.seek(start)
        code = datafile.read(end - start)

    # We need everything to be local variables before we clear the global dict
    def_package = PINLINED_DEFAULT_PACKAGE
    name = __name__
    filename = def_package + '/__init__.py'
    compiled_code = compile(code, filename, 'exec')

    # Prepare globals to execute __init__ code
    globals().clear()
    # If we've been called directly we cannot set __path__
    if name != '__main__':
        globals()['__path__'] = [def_package]
    else:
        def_package = None
    globals().update(__file__=filename,
                     __package__=def_package,
                     __name__=name,
                     __loader__=importer)


    exec compiled_code


# Prepare loader's module and populate this namespace only with package's
# __init__
prepare_package()
