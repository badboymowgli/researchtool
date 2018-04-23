#!/bin/usr/python
# coding: utf-8
import time
from datetime import datetime
from flask import Flask, request, render_template, redirect, send_from_directory
import json
import sys
import os
import glob
import jinja2
import re
import string
import random
import requests
import base64

app = Flask(__name__, template_folder='templates')
app._static_folder = 'assets/'

def random_str(size=4, chars=string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def image(url):
    if 'http' in url:
        response = requests.get(url)
        uri = ("data:" + response.headers['Content-Type'] + ";" + "base64," + base64.b64encode(response.content))
        return uri
    else:
        with open(url, "rb") as image_file:
            uri = "data:image/png;base64," + base64.b64encode(image_file.read())
        return uri

def view_files():
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	dir_list = os.listdir(root)
	title_file_list = []
	for each_file in file_list:
		with open(each_file) as data_file:
			data = json.load(data_file)
			title_file_dict = {}
			title_file_dict["research_title"] = data["research_title"]
			title_file_dict["researcher"] = data["researcher"]
			title_file_dict["researcherID"] = data["researcherID"]
			title_file_dict["research_discription"] = data["research_discription"]
			title_file_dict["research_pic"] = data["research_pic"]
			title_file_dict["research"] = data["research"]
			title_file_dict["file"] = each_file
			title_file_list.append(title_file_dict)
	return title_file_list

##############################################
# APPLICATION DEPENDANT ASSET LOCATION
##############################################
## Static File Rendering

### JS
@app.route('/assets/js/<path:path>')
def send_js(path):
   	return send_from_directory('js', path)

### CSS
@app.route('/assets/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)

##############################################
# FILES
##############################################
## Files View
@app.route('/')
def home_page():
	new = dict()
	vf = view_files()
	new['files'] = vf
	if vf:
		return render_template('files.html', **new)
	else:
		return render_template('files.html', **new)

## File add GET/View
@app.route('/researchfile/add')
def file_add():
	new =  dict(researcher = "BadBoy_Mowgli", researcherID = "BBM", researcher_contact = None, research_title = None, research_discription = None, research = [])
	return render_template('add_research_file.html', **new)

## File add POST
@app.route('/researchfile/add', methods=['POST'])
def do_file_add():
	vf = view_files()
	fc = len(vf) + 1
	nf = "research_file_" + str(fc) + "_" + str(random_str()) + ".json"
	new_file =  dict()
	new_file.update(request.form.to_dict())
	new_file["research"] = []
	#new_file["research_pic"] = image(new_file["research_pic"])
	fileout = json.dumps(new_file, indent=4, separators=(',', ': '))
	text_file = open("research/" + nf, "w")
	text_file.write(fileout)
	text_file.close()
	return redirect('/')

## File edit GET/View
@app.route('/researchfile/<int:fidx>/edit')
def file_edit(fidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	data["url"] = "/researchfile/" + str(fidx) + "/edit"
	return render_template('edit_research_file.html', **data)

## File edit POST
@app.route('/researchfile/<int:fidx>/edit', methods=['POST'])
def do_file_edit(fidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	data.update(request.form.to_dict())
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	return redirect('/')

## File delete
@app.route('/researchfile/<int:fidx>/delete')
def do_file_delete(fidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	os.remove(file_list[fidx])
	return redirect('/')

##############################################
# TOPICS
##############################################
## Topic view
@app.route('/researchfile/<int:fidx>/research/<int:ridx>')
def subjects_page(fidx, ridx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
		data["research"][ridx]["topic_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx)
	return render_template('topic.html', **data["research"][ridx])

## Topic add GET/View
@app.route('/researchfile/<int:fidx>/research/add')
def topic_add(fidx):
	new =  dict(topic_title = None, topic_pic = None, topic_url_resource = None, topic_discription = None, subjects = [] ,topic_url = "/researchfile/" + str(fidx) + "/research/add" )
	return render_template('add_topic.html', **new)

## Topic add POST
@app.route('/researchfile/<int:fidx>/research/add', methods=['POST'])
def do_topics_add(fidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	new_topic = dict(subjects = [])
	new_topic.update(request.form.to_dict())
	#new_topic["topic_pic"] = image(new_topic["topic_pic"])
	data["research"].append(new_topic)
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	return redirect('/')

## Topic edit GET/View
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/edit')
def topic_edit(fidx, ridx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
		data["research"][ridx]["topic_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx)
	return render_template('edit_topic.html', **data["research"][ridx])

## Topic edit POST
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/edit', methods=['POST'])
def do_topic_edit(fidx, ridx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	data["research"][ridx].update(request.form.to_dict())
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	data["research"][ridx]["topic_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx)
	return redirect('/researchfile/' + str(fidx) + '/research/' + str(ridx))

## Topic delete
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/delete')
def topic_delete(fidx, ridx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
	data["research"].pop(ridx)
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	return redirect('/')

##############################################
# SUBJECTS
##############################################
## Subject view
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>')
def notes_page(fidx, ridx, sidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
	data["research"][ridx]["subjects"][sidx]["subject_url"] = "/researchfile/" + str(fidx) + "/research/" + str(ridx) + "/subjects/" + str(sidx)
	return render_template('subject.html', **data["research"][ridx]["subjects"][sidx])

## Subject add GET/View
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/add')
def subject_add(fidx, ridx):
	new =  dict(subject_title = None, subject_pic = None, subject_url_resource = None, subject_discription = None, notes = [] ,subject_url = "/researchfile/" + str(fidx) + "/research/" + str(ridx) + "/add" )
	return render_template('add_subject.html', **new)

## Subject add POST
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/add', methods=['POST'])
def do_subjects_add(fidx, ridx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	new_subject = dict(notes = [])
	new_subject.update(request.form.to_dict())
	#new_subject["subject_pic"] = image(new_subject["subject_pic"])
	data["research"][ridx]["subjects"].append(new_subject)
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	data["research"][ridx]["topic_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx)
	return redirect('/researchfile/' + str(fidx) + '/research/' + str(ridx))

## Subject edit GET/View
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/edit')
def subject_edit(fidx, ridx, sidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
	data["research"][ridx]["subjects"][sidx]["subject_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx) + "/subjects/" + str(sidx)
	return render_template('edit_subject.html', **data["research"][ridx]["subjects"][sidx])

## Subject edit POST
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/edit', methods=['POST'])
def do_subject_edit(fidx, ridx, sidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	data["research"][ridx]["subjects"][sidx].update(request.form.to_dict())
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	data["research"][ridx]["subjects"][sidx]["subject_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx) + "/subjects/" + str(sidx)
	return redirect('/researchfile/' + str(fidx) + '/research/' + str(ridx) + "/subjects/" + str(sidx))

## Subject delete
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/delete')
def subject_delete(fidx, ridx, sidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
	data["research"][ridx]["subjects"].pop(sidx)
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	return redirect('/researchfile/' + str(fidx) + '/research/' + str(ridx))

##############################################
# NOTES
##############################################
## Note add GET/View
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/notes/add')
def note_add(fidx, ridx, sidx):
	new =  dict(note_title = None, note_discription = None, note_linkurl = None, note_linkname = None ,note_url = "/researchfile/" + str(fidx) + "/research/" + str(ridx) + "/subjects/" + str(sidx) +"/notes/add" )
	return render_template('add_note.html', **new)

## Note add POST
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/notes/add', methods=['POST'])
def do_note_add(fidx, ridx, sidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	new_note = dict()
	new_note.update(request.form.to_dict())
	data["research"][ridx]["subjects"][sidx]["notes"].append(new_note)
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	return redirect('/researchfile/' + str(fidx) + '/research/' + str(ridx)+ '/subjects/' + str(sidx))

## Note edit GET/View
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/notes/<int:nidx>/edit')
def note_edit(fidx, ridx, sidx, nidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
	data["research"][ridx]["subjects"][sidx]["note_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx) + "/subjects/" + str(sidx) + "/notes/" + str(nidx)
	return render_template('edit_note.html', **data["research"][ridx]["subjects"][sidx]["notes"][nidx])

## Note edit POST
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/notes/<int:nidx>/edit', methods=['POST'])
def do_note_edit(fidx, ridx, sidx, nidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx], "r") as data_file:
		data = json.load(data_file)
	data["research"][ridx]["subjects"][sidx]["notes"][nidx].update(request.form.to_dict())
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	data["research"][ridx]["subjects"][sidx]["subject_url"] = '/researchfile/' + str(fidx) + '/research/' + str(ridx) + "/subjects/" + str(sidx) + "/notes/" + str(nidx)
	return redirect('/researchfile/' + str(fidx) + '/research/' + str(ridx) + "/subjects/" + str(sidx))

## Note delete
@app.route('/researchfile/<int:fidx>/research/<int:ridx>/subjects/<int:sidx>/notes/<int:nidx>/delete')
def note_delete(fidx, ridx, sidx, nidx):
	root = "research"
	path = os.path.join(root, "research")
	file_list = []
	for path, subdirs, files in os.walk(root):
		for name in files:
			file_list.append(os.path.join(path, name))
	with open(file_list[fidx]) as data_file:
		data = json.load(data_file)
	data["research"][ridx]["subjects"][sidx]["notes"].pop(nidx)
	fileout = json.dumps(data, indent=4, separators=(',', ': '))
	text_file = open(file_list[fidx], "w")
	text_file.write(fileout)
	text_file.close()
	return redirect('/researchfile/' + str(fidx) + '/research/' + str(ridx) + "/subjects/" + str(sidx))

##############################################
# MAIN: Run web server and the application
##############################################
if __name__ == '__main__':
   app.debug = True
   app.run(host='0.0.0.0', port=8090)
