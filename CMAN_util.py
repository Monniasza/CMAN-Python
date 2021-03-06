import requests
import shutil
import os
import glob
import json
import sys
import tarfile
import zipfile
import tkinter as tk
import tkinter.messagebox as msgbox
import tkinter.simpledialog as dialogs
import tkinter.filedialog as filedialogs
import textwrap

modfolder = "@ERROR@"
versionsfolder = "@ERROR@"
execdir = "@ERROR@"
instance = "@ERROR@"
tkinst = None

version = "2.1.0"

def read_default_instance():
	old_cwd = os.getcwd() #to reset cwd afterward
	os.chdir(os.path.join(execdir, "LocalData")) #at this point in startup, old_cwd is execdir
	try:
		with open("default_instance.txt") as f:
			default = f.read().strip() #don't want leading trailing whitespace/newlines
	except(FileNotFoundError):
		default = "default"
		with open("default_instance.txt", "w") as f:
			f.write(default)

	os.chdir(old_cwd) #restoring cwd
	return default

def check_for_updates():
	response = requests.get('http://raw.githubusercontent.com/Comprehensive-Minecraft-Archive-Network/CMAN-Python/master/version.txt')
	latestversion = response.text
	if (version != str(latestversion)):
		#if (gui):
		#	msgbox.askyesno("Update available", "You are running CMAN " + version + ".\nThe newest version is " + str(latestversion) + ".", parent=tkinst, master=tkinst)
		#else:
		cprint("!!Update Available! You are running CMAN " + version + ". The newest version is " + str(latestversion) + "!!")

def init_config_util(data): #data is a 5-tuple
	global modfolder, versionsfolder, execdir, instance, gui  #makes it edit the global vars rather than create new ones
	modfolder, versionsfolder, execdir, instance, gui = data

def recieve_tkinst_util(data):
	global tkinst
	tkinst = data

def cprint(text): #outputs text to console pane in GUI if gui enabled, otherwise prints it
	if (gui == True):
		tkinst.console.config(state = tk.NORMAL)
		tkinst.console.insert(tk.END, str(text)+"\n")
		tkinst.console.config(state = tk.DISABLED)
		tkinst.console.see(tk.END)
	else:
		print(text)

def iprint(text): #outputs text to info pane in GUI if gui enabled, otherwise prints it
	if (gui == True):
		tkinst.info.config(state = tk.NORMAL)
		tkinst.info.delete("1.0", tk.END)
		tkinst.info.insert(tk.END, str(text))
		tkinst.info.config(state = tk.DISABLED)
	else:
		cprint(text)

def instance_exists(instance):
	with open(execdir+ "/LocalData/config.json") as json_file:
		try:
			json_data = json.load(json_file)
		except(json.decoder.JSONDecodeError):
			cprint("The config JSON appears to be invalid. Delete it and run CMAN again.")
			json_file.close()
			sys.exit()
	return(instance in json_data.keys())

def read_config(instance):
	if (os.path.exists("config.json")):
		with open("config.json") as json_file:
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				cprint("The config JSON appears to be invalid. Delete it and run CMAN again.")
				json_file.close()
				sys.exit()
			json_file.close()
		if(instance in json_data.keys()):
			try:
				modfolder = json_data[instance]["modfolder"] # If config exists, get modfolder and versions folder from that. Else, ask for it.
			except(KeyError): #modfolder data missing
				f = open("config.json", "w")
				json_data[instance]["modfolder"] = input("Enter mod folder location for instance "+instance+" (absolute path): ")
				json.dump(json_data, f)
				f.close()
			try:
				versionsfolder = json_data[instance]["versionsfolder"]
			except(KeyError): #versionsfolder data missing
				f = open("config.json", "w")
				son_data[instance]["versionsfolder"] = input("Enter versions folder location for instance "+instance+" (absolute path): ")
				json.dump(json_data, f)
				f.close()
		else:
			cprint("Config for instance "+instance+" is missing. Setting up config.")
			modfolder = input("Enter mod folder location for instance "+instance+" (absolute path): ")
			versionsfolder = input("Enter versions folder location for instance "+instance+" (absolute path): ")
			f = open("config.json", 'w')
			json_data[instance] = {"modfolder": modfolder, "versionsfolder": versionsfolder}
			json.dump(json_data, f)
			f.close()
	else:
		print("Config for instance "+instance+" is missing. Setting up config.")
		modfolder = input("Enter mod folder location for instance "+instance+" (absolute path): ")
		versionsfolder = input("Enter versions folder location for instance "+instance+" (absolute path): ")
		f = open("config.json", 'w')
		json_data = {instance: {"modfolder": modfolder, "versionsfolder": versionsfolder}}
		json.dump(json_data, f)
		f.close()
	return(modfolder, versionsfolder)

def new_config(instance):
		with open(execdir+"/LocalData/config.json") as json_file: #can assume it exists and is valid, the program has loaded before this is called
			json_data = json.load(json_file)
			json_file.close()
		if(instance in json_data.keys()):
			cprint("Instance "+instance+" already exists, cannot add it.")
		else:
			if(gui):
				modfolder = filedialogs.askdirectory(parent=tkinst, title="Select Mod Folder")
				versionsfolder = filedialogs.askdirectory(parent=tkinst, title="Select Versions Folder")
			else:
				modfolder = input("Enter mod folder location for instance "+instance+" (absolute path): ")
				if(modfolder == None):
					return (-1, -1)
				versionsfolder = input("Enter versions folder location for instance "+instance+" (absolute path): ")
			if(versionsfolder == None):
				return (-1, -1)
			f = open(execdir+"/LocalData/config.json", 'w')
			json_data[instance] = {"modfolder": modfolder, "versionsfolder": versionsfolder}
			json.dump(json_data, f)
			f.close()
		cprint("Done.")
		return(modfolder, versionsfolder)

def rm_config(_instance):
	if instance == _instance:
		cprint("Cannot remove instance while it is active! Select another instance first.")
	else:
		with open(execdir+"/LocalData/config.json") as json_file: #can assume it exists, the program has loaded before this is called
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				cprint("The config JSON appears to be invalid. Delete it and run CMAN again.")
				json_file.close()
				sys.exit()
			json_file.close()
		if(_instance in json_data.keys()):
			del json_data[_instance]
			with open(execdir+"/LocalData/config.json", "w") as f:
				json.dump(json_data, f)
			cprint("Removed config data for instance "+_instance+".")
			if(os.path.exists(os.path.join("ModsDownloaded", _instance))):
				if(gui):
					a = msgbox.askyesno("Delete installed mod listing", "Delete installed mod listing for instance "+_instance+"?\nType OK to delete.", parent=tkinst)
				else:
					a = input("Delete installed mod listing for instance "+_instance+"? Type OK to delete, or anything else to skip: ") == "OK"
				if(a):
					shutil.rmtree(os.path.join("ModsDownloaded", _instance))
					cprint("Deleted installed mod listing.")
				else:
					cprint("Skipped installed mod listing.")
	cprint("Done.")

def get_json(modname):
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		os.chdir(execdir + "/Data/CMAN-Archive")
	else:
		cprint("CMAN archive not found. Please update the CMAN archive.")
		return(-1)
	if(os.path.exists(modname + ".json")):
		# JSON parsing
		with open(modname + ".json") as json_file:
			try:
				json_data = json.load(json_file)
				json_file.close()
			except(json.decoder.JSONDecodeError):
				cprint("The JSON file \""+modname+".json\" appears to be invalid. Please update the CMAN archive.")
				json_file.close()
				return
		return(json_data)
	else:
		return(None)

def get_installed_json(modname):
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+instance)):
		os.chdir(execdir + "/LocalData/ModsDownloaded/"+instance)
	else:
		return(None) #no mods installed, so obviously modname isn't installed
	if(os.path.exists(modname + ".installed")):
		# JSON parsing
		with open(modname + ".installed") as json_file:
			try:
				json_data = json.load(json_file)
			except(json.decoder.JSONDecodeError):
				cprint("The JSON file \""+modname+".installed\" appears to be invalid. Using data from CMAN archive.")
				json_data = (get_json(modname))
			finally:
				json_file.close()
		return(json_data)
	else:
		return(None)

def mod_installed(modname):
	if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+instance)):
		os.chdir(execdir + "/LocalData/ModsDownloaded/"+instance)
	else:
		return(False) #no mods installed, so obviously modname isn't installed
	files = glob.glob(modname + ".installed")
	return(len(files)>0)

def get_all_insts():
	with open(execdir + "/LocalData/config.json") as json_file: #can assume it exists and is valid, the program has loaded before this is called
			json_data = json.load(json_file)
			json_file.close()
	insts = json_data.keys()
	return insts


def get_installed_jsons(inst = None, allinst=True):
	jsons = []
	if(inst == None and allinst):
		with open(execdir + "/LocalData/config.json") as json_file: #can assume it exists and is valid, the program has loaded before this is called
			json_data = json.load(json_file)
			json_file.close()
		insts = json_data.keys()
	elif(inst == None and not allinst):
		insts = [instance]
	else:
		insts = [inst]
	for inst in insts:
		if(os.path.exists(execdir + "/LocalData/ModsDownloaded/"+inst)):
			mods = os.listdir(execdir + "/LocalData/ModsDownloaded/"+inst)
			os.chdir(execdir + "/LocalData/ModsDownloaded/"+inst)
			for mod in mods:
				json_data = get_installed_json(mod[:-10]) #[:-10] cuts off the .installed extension
				jsons.append(json_data)
	return(jsons)


def get_all_jsons():
	jsons = []
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		mods = os.listdir(execdir + "/Data/CMAN-Archive")
		for mod in mods:
			json_data = get_json(mod[:-5]) #[:-5] cuts off the .json extension
			if json_data != None:
				jsons.append(json_data)
	return(jsons)

def switch_path_dir(path, dir): #switches tkinst of path to dir given
	pathsplit = path.split(os.sep)
	pathsplit[0] = dir.split(os.sep)[-1] #just in case it ends with os.sep
	return(os.sep.join(pathsplit))

def listmods(output=True, allinst=True):
	modsinstalled = get_installed_jsons(inst = None, allinst=allinst)
	if output:
		cprint("Installed mods:")
		cprint(str(modsinstalled))
	else:
		return modsinstalled

def listmods_all(output=True):
	mods = get_all_jsons()
	if output:
		cprint("Mods:")
		cprint(str(mods))
	else:
		return mods

def mergedirs(dir1, dir2):
	files1 = []
	files2 = []
	for tuple1 in os.walk(dir1):
		files1.append(tuple1[0])
		for file1 in tuple1[2]:
			files1.append(os.path.join(tuple1[0], file1))
	for file_ in files1: #file_ because file() is a builtin function
		if(os.path.split(file_)[0] == ''): #if file_ == dir1
			continue #skip it
		if(not os.path.exists(os.path.split(switch_path_dir(file_, dir2))[0])): #if parent dir does not exist in dir2
			cprint(file_)
			os.makedirs(os.path.split(switch_path_dir(file_, dir2))[0]) #make parent dir in dir2
		if(os.path.isfile(file_)):
			shutil.copy(file_, switch_path_dir(file_, dir2))
		else: #if it is a dir, because it can only be either a file or a dir
			if(not os.path.exists(switch_path_dir(file_, dir2))):
				os.mkdir(switch_path_dir(file_, dir2))

def fix_names(path, oldname, name):
	old_cwd = os.getcwd() #to reset cwd afterwards
	os.chdir(path)
	os.rename(oldname+".jar", name+".jar")
	os.rename(oldname+".json", name+".json")
	with open(name+".json") as f:
		data = json.load(f)
		f.close()
	data["id"] = name
	with open(name+".json", "w") as f:
		json.dump(data, f)
		f.close()
	os.chdir(old_cwd) #restoring cwd

def display_versions(versions): #just makes the version list into a nicer string for printing (minus the brackets and quotes)
	versionstr = ""
	for version in versions:
		versionstr = versionstr + version +", "
	return(versionstr[:-2]) #cuts off the extra ", " at the end

def get_deps(modname):
	json_data = get_json(modname)
	deps = json_data["Requirements"]
	return(deps)

def update_archive(start=False):
	#Delete old archive
	os.chdir(execdir + "/Data")
	if(os.path.exists(execdir + "/Data/CMAN-Archive")):
		shutil.rmtree("CMAN-Archive")
	# Archive Download
	url = "https://github.com/Comprehensive-Minecraft-Archive-Network/CMAN-Archive/tarball/master"
	file_name = "CMAN.tar.gz"
	cprint("Downloading Archive...")
	# Download it.
	try:
		with open(file_name, 'wb') as out_file:
			response = requests.get('https://github.com/Comprehensive-Minecraft-Archive-Network/CMAN-Archive/tarball/master')
			out_file.write(response.content)
		cprint("Done.")
	except Exception as e:
		cprint("Something went wrong while downloading the archive.")
		cprint("Error: " + str(e))
		if(gui and not start):
			msgbox.showerror("Archive download failed", "Something went wrong while downloading the archive.", parent=tkinst)
		if(start):
			print("CMAN: fatal: Something went wrong while downloading the archive.")
			sys.exit()
		else:
			return -1
	cprint("Extracting Archive...")
	tar = tarfile.open("CMAN.tar.gz")  # untar
	tar.extractall()
	tarlist = tar.getnames()
	os.rename(tarlist[0], "CMAN-Archive") #rename the resulting folder to CMAN-Archive
	cprint("Done.")
	if(gui and not start):
		msgbox.showinfo("Archive updated", "The CMAN archive has been successfully updated.", parent=tkinst)

def get_info_console(modname, output=False):
	istr = []
	ostr = ""
	if(modname == None):
		modname = input("Enter mod name: ")

	json_data = get_json(modname)
	if(json_data == -1):
		return
	else:
		if (json_data != None):
			if(json_data["Unstable"] == "false"):
				stable = "Stable"
			else:
				stable = "Unstable"
			istr.append(json_data["Name"]+":"+"\n\n")
			istr.append("Version: "+json_data["Version"]+" ("+stable+")"+"\n\n")
			istr.append("Author(s): "+json_data["Author"]+"\n\n")
			istr.append("Description: "+json_data["Desc"]+"\n\n")
			istr.append("Requirements: "+str(json_data["Requirements"])+"\n\n")
			istr.append("Known Incompatibilities: "+str(json_data["Incompatibilities"])+"\n\n")
			istr.append("Download Link: "+str(json_data["Link"])+"\n\n")
			istr.append("License: "+json_data["License"])
		else:
			istr.append("Mod "+modname+" not found.")
		if(output):
			cprint(istr)
		else:
			for _istr in istr:
				_istr = textwrap.fill(_istr, 46)
				ostr = ostr+_istr+"\n\n"
			#print(textwrap.fill(istr, 46).replace("  *", "\n\n"))
			return(ostr)


def get_info(modname, output=True):
	istr = ""
	if(modname == None):
		modname = input("Enter mod name: ")

	json_data = get_json(modname)
	if(json_data == -1):
		return
	else:
		if (json_data != None):
			if(json_data["Unstable"] == "false"):
				stable = "Stable"
			else:
				stable = "Unstable"
			istr = istr+json_data["Name"]+":"+"\n"
			istr = istr+"\tVersion: "+json_data["Version"]+" ("+stable+")"+"\n"
			istr = istr+"\tAuthor(s): "+json_data["Author"]+"\n"
			istr = istr+"\tDescription: "+json_data["Desc"]+"\n"
			istr = istr+"\tRequirements: "+str(json_data["Requirements"])+"\n"
			istr = istr+"\tKnown Incompatibilities: "+str(json_data["Incompatibilities"])+"\n"
			istr = istr+"\tDownload Link: "+str(json_data["Link"])+"\n"
			istr = istr+"\tLicense: "+json_data["License"]
		else:
			istr = istr+"Mod "+modname+" not found."
		if(output):
			cprint(istr)
		else:
			return(istr)


def print_help():
	cprint("Commands:")
	cprint(" install 'mod': install the mod 'mod'")
	cprint(" installm: install multiple mods")
	cprint(" info 'mod': get info for the mod 'mod'")
	cprint(" remove 'mod': remove the mod 'mod'")
	cprint(" removem: remove multiple mods")
	cprint(" upgrade 'mod': upgrade the mod 'mod'")
	cprint(" upgradem: upgrade multiple mods")
	cprint(" upgradeall: upgrade all outdated mods for Minecraft instance 'inst', or use '*' to check all instances")
	cprint(" upgrades 'inst': list available mod upgrades for Minecraft instance 'inst', or use '*' to check all instances")
	cprint(" update: update the CMAN archive")
	cprint(" help: display this help message")
	cprint(" version: display the CMAN version number")
	cprint(" list: list installed mods")
	cprint(" export 'name': export a modlist with the name 'name' , which can be imported later")
	cprint(" import 'pathtomodlist': import the modlist 'pathtomodlist'")
	cprint(" inst 'inst': switches to Minecraft instance 'inst'")
	cprint(" defaultinst 'inst': sets default Minecraft instance to 'inst'")
	cprint(" addinst 'inst': adds the Minecraft instance 'inst'")
	cprint(" rminst 'inst': removes the Minecraft instance 'inst'")
	cprint(" insts: lists all Minecraft instances")
	cprint(" exit: exit CMAN")
