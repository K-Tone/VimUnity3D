#
# (C) Anthony Yakovlev, anthony.yakovlev@gmail.com, 2013
#  

import sys
import os
import tempfile

PATH_TO_UNITY = 'C:/Program Files (x86)/Unity'

class CommandFileGenerator:
	_ignored = ['Library', 'Plugins']
	
	_compiler_defines = [
		'UNITY_3_5_5',
		'UNITY_3_5',
		'UNITY_EDITOR',
		'ENABLE_PROFILER',
		'UNITY_STANDALONE_WIN',
		'ENABLE_GENERICS',
		'ENABLE_DUCK_TYPING',
		'ENABLE_TERRAIN',
		'ENABLE_MOVIES',
		'ENABLE_WEBCAM',
		'ENABLE_MICROPHONE',
		'ENABLE_NETWORK',
		'ENABLE_CLOTH',
		'ENABLE_WWW',
		'ENABLE_SUBSTANCE',
	]
	
	_compiler_options = [
		'-debug',
		'-target:library',
		'-nowarn:0169',
		'-out:Assembly-CSharp.dll',
		'-r:"C:/Program Files (x86)/Unity/Editor/Data/Managed/UnityEngine.dll"',
		'-r:"C:/Program Files (x86)/Unity/Editor/Data/Managed/UnityEditor.dll"',
	]
	
	def _get_define_options(self):
		return '\n'.join( map(lambda x : '-define:' + x, self._compiler_defines) ) + '\n'
		
	def _get_compiler_options(self):
		return '\n'.join( self._compiler_options ) + '\n' + self._get_define_options() + '\n'
	
	def __init__(self, rootPath):
		self._root = rootPath

	def _collect_input_files(self):
		self._result = []

		os.path.walk(self._root, CommandFileGenerator._cb, self)

		return self._result

	@staticmethod
	def _cb(me, dirname, fnames):
		for ig in me._ignored:
			if ig in fnames:
				fnames.remove(ig)

		for f in fnames:
			ext = os.path.splitext(f)[1]
			item = os.path.join(dirname, f)
			if ext == '.cs':
				me._result.append('"' + item + '"')
			if ext == '.dll':
				me._result.append('-r:' + item)
			if ext == '.rsp':
				me._result.append('@' + item)
				
	def generate(self):
		items = self._collect_input_files()
		return self._get_compiler_options() + '\n'.join(items)

def _compile(project_root):
	mono_path = os.path.join(PATH_TO_UNITY, r'Editor\Data\Mono\bin\mono.exe')
	smcs_path = os.path.join(PATH_TO_UNITY, r'Editor\Data\Mono\lib\mono\unity\smcs.exe')
	
	options_file = tempfile.NamedTemporaryFile(mode = 'w', delete=False)
	
	content = CommandFileGenerator( project_root ).generate()
		
	options_file.write( content )
	
	options_file.close()
	
	command_line = 'call "%s" "%s" @"%s"' % (mono_path, smcs_path, options_file.name)
	
	print 'Kicking off', command_line
	
	os.system( command_line )
	
def _extract_assets_path(file_in_project):
	path = file_in_project
	
	while os.path.basename(path) <> 'Assets':
		path = os.path.dirname(path)
		
	return path
		
def run():
	project_root = _extract_assets_path( sys.argv[1] )
	
	print 'Project path is', project_root
	
	_compile( project_root )
    
run()