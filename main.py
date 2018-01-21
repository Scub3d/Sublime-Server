import sublime, sublime_plugin, io, cgi, ssl, json, os

from subprocess import call
import subprocess

from http.server import BaseHTTPRequestHandler
from urllib import parse

class ServerHandler(BaseHTTPRequestHandler):
	def do_GET(self):
		parsed_path = parse.urlparse(self.path)
		message_parts = [
			'CLIENT VALUES:',
			'client_address={} ({})'.format(
				self.client_address,
				self.address_string()),
			'command={}'.format(self.command),
			'path={}'.format(self.path),
			'real path={}'.format(parsed_path.path),
			'query={}'.format(parsed_path.query),
			'request_version={}'.format(self.request_version),
			'',
			'SERVER VALUES:',
			'server_version={}'.format(self.server_version),
			'sys_version={}'.format(self.sys_version),
			'protocol_version={}'.format(self.protocol_version),
			'',
			'HEADERS RECEIVED:',
		]

		for name, value in sorted(self.headers.items()):
			message_parts.append('{}={}'.format(name, value.rstrip()))

		message_parts.append('')
		message = '\r\n'.join(message_parts)
		self.send_response(200)
		self.send_header('Content-Type', 'text/plain; charset=utf-8')
		self.end_headers()
		self.wfile.write(message.encode('utf-8'))

	def do_POST(self):
		message = None
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)

		intentName = json.loads(str(post_data.decode("utf-8")))["result"]["metadata"]["intentName"] 
		if intentName == "displayMessage":
			displayMessage(json.loads(post_data.decode("utf-8"))["result"]["parameters"]["message"])
		elif intentName == "saveFile":
			saveFile()
		elif intentName == "openFile":
			openFile(json.loads(post_data.decode("utf-8"))["result"]["parameters"]["fileName"])
		elif intentName == "deleteFile":
			deleteFile()
		elif intentName == "selectAll":
			selectAll()
		elif intentName == "deleteSelection":
			deleteSelection()
		elif intentName == "showMenu":
			setMenuVisibility(True)
		elif intentName == "hideMinimap":
			setMinimapVisibility(False)
		elif intentName == "showMinimap":
			setMinimapVisibility(True)
		elif intentName == "showSidebar":
			setSidebarVisibility(True)
		elif intentName == "hideSidebar":
			setSidebarVisibility(False)
		elif intentName == "hideTabs":
			setTabsVisibility(False)
		elif intentName =="createFile":
			newFile()
		elif intentName == "getActiveFiles":
			message = getActiveFiles()
		elif intentName == "getMinimapVis":
			message = etMinimapVisibility()
		elif intentName == "getOpenFiles":
			message = getOpenFiles()
			print("message == > ")
			print(message)
		elif intentName == "getSidebarVis":
			message = getSidebarVisibility()
		elif intentName == "getTabVis":
			message = getTabsVisibility()
		elif intentName == "gitAdd":
			gitAdd()
		elif intentName == "gitCommit":
			gitCommit()
		elif intentName == "gitPull":
			gitPull()
		elif intentName == "gitPush":
			gitPush()
		elif intentName == "hideMenu":
			setMenuVisibility(False)
		elif intentName == "hidePopup":
			hidePopup()
		elif intentName == "showTabs":
			setTabsVisibility(True)
		elif intentName == "replaceAll":
			replace(json.loads(post_data.decode("utf-8"))["result"]["parameters"]["search"], json.loads(post_data.decode("utf-8"))["result"]["parameters"]["replace"])

		self.send_response(200)
		self.send_header('Content-Type', 'text/plain; charset=utf-8')
		self.end_headers()

		if message != None:
			print(respondToGoogleHome(message))
			self.wfile.write(respondToGoogleHome(message))#.encode('utf-8'))


class StartserverCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("I can't believe this actually works.... lmao")
		sublime.set_timeout_async(handleServerSetup, 1000)

def handleServerSetup():
	from http.server import HTTPServer
	server = HTTPServer(('localhost', 8080), ServerHandler)
	print("Serving up spicy memes")
	server.serve_forever()

class DuplicateCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		gitAdd()
		for region in self.view.sel():
			line = self.view.line(region)
			lineContents = '\n' + self.view.substr(line) + '\n\n'
			self.view.insert(edit, line.begin(), lineContents)

class ReplaceCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		replacement = newWord
		thingToFind = oldWord
		thingsToReplace = self.view.find_all(thingToFind)
		for thing in reversed(thingsToReplace):
			self.view.replace(edit, thing, replacement)

class DeleteselectionCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		for region in self.view.sel():
			line = self.view.line(region)
			self.view.erase(edit, line)

################################################
def numberOfWindowsOpen(self, edit):
	ws = sublime.windows()
	return len(sublime.windows())

def displayMessage(message):
	sublime.message_dialog(message)

def saveFile():
	sublime.active_window().active_view().run_command("save")

def openFile(fileName):
	sublime.active_window().open_file(fileName)

def newFile():
	sublime.active_window().new_file()

def replace(oWord, nWord):
	global oldWord, newWord
	oldWord = oWord
	newWord = nWord
	sublime.active_window().active_view().run_command("replace")

def duplicate():
	sublime.active_window().active_view().run_command("duplicate")

def renameFile(newFileName):
	oldFilePath = sublime.active_window().active_view().file_name()
	splitPath = oldFilePath.split("\\")
	splitPath[-1] = newFileName
	sublime.active_window().run_command("close_file")
	os.rename(oldFilePath,"\\".join(splitPath))
	openFile("\\".join(splitPath))

def deleteFile():
	currentFilePath = sublime.active_window().active_view().file_name() 
	sublime.active_window().run_command("close_file")
	os.remove(currentFilePath)

def selectAll():
	sublime.active_window().active_view().sel().add(sublime.Region(0, sublime.active_window().active_view().size()))
	print("sel all")

def setMenuVisibility(state):
	sublime.active_window().set_menu_visible(state)

def setMinimapVisibility(state):
	sublime.active_window().set_minimap_visibile(state)

def setSidebarVisibility(state):
	sublime.active_window().set_sidebar_visible(state)

def setTabsVisibility(state):
	sublime.active_window().set_tabs_visible(state)

def setStatusBarVisibility(state):
	sublime.active_window().set_status_bar_visible(state)

def getMenuVisibility():
	sublime.active_window().is_menu_visible()

def getMinimapVisibility():
	sublime.active_window().is_minimap_visible()

def getSidebarVisibility():
	sublime.active_window().is_sidebar_visible()

def getTabsVisibility():
	sublime.active_window().is_tabs_visible()

def getStatusBarVisibility():
	sublime.active_window().is_status_bar_visible()

def deleteSelection():
	sublime.active_window().run_command("deleteselection")

def getActiveFiles():
	activeFiles = []
	for w in sublime.windows():
		openFiles.append(w.active_view())
	response = "The following files are active: "
	for f in activeFiles:
		response += f
		response += ", "
	return response[:-2]

def getOpenFiles():
	openFiles = []
	for w in sublime.windows():
		for v in w.views():
			openFiles.append(v.file_name())

	print(openFiles)

	response = "The following files are open: "
	for f in openFiles:
		response += f.split("\\")[-1]
		response += ", "
	print(response)
	return response[:-2]

def hidePopup():
	sublime.active_window().active_view().hide_popup()

def gitAdd():
	subprocess.call(["git", "-C", "\\".join(sublime.active_window().active_view().file_name().split("\\")[:-1]), "add", sublime.active_window().active_view().file_name()])

def gitCommit():
	subprocess.call(["git", "-C", "\\".join(sublime.active_window().active_view().file_name().split("\\")[:-1]), "commit", "-m", "Made a commit from a server inside sublime text"])

def gitPull():
	subprocess.call(["git", "-C", "\\".join(sublime.active_window().active_view().file_name().split("\\")[:-1]), "pull"])

def gitPush():
	subprocess.call(["git", "-C", "\\".join(sublime.active_window().active_view().file_name().split("\\")[:-1]), "push"])


def respondToGoogleHome(response):
	resposneJSON = {
	  "speech": response,
	  "displayText": "",
	  "data": {
	    "google": {
	      "expect_user_response": True,
	      "is_ssml": True,
	      "permissions_request": {
	        "permissions": [
	          "NAME",
	          "DEVICE_COARSE_LOCATION",
	          "DEVICE_PRECISE_LOCATION"
	        ]
	      }
	    }
	  },
	  "contextOut": [],
	}
	return bytes(json.dumps(resposneJSON).encode("utf-8"))
