# Author: Prof. MM Ghassemi <ghassem3@msu.edu>
import sys
from flask import current_app as app
from flask import render_template, redirect, request
from .utils.database.database  import database
from werkzeug.datastructures import ImmutableMultiDict
from pprint import pprint
import json
import random
db = database()

# # So I don't see a ton of HTTP errors
# import logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)  # Suppress everything below ERROR level
# #

@app.route('/')
def root():
	return redirect('/home')

@app.route('/home')
def home():
	x     = random.choice(['I am Canadian.','I was once the youngest person in the world.','I can solve a Rubik\'s cube.'])
	return render_template('home.html', fun_fact = x)

@app.route('/projects')
def projects():
	return render_template('projects.html')

@app.route('/resume')
def resume():
	resume_data = db.getResumeData()
	pprint(resume_data)

	# Displays layout.html and resume.html's maincontent block is added on.
	# That resume_data variable is used in the for loop in the maincontent
	#   of resume.html that is pasted over layout.html which it extends.
	return render_template('resume.html', resume_data = resume_data)

@app.route('/piano')
def piano():
	pprint("arrived at /piano")
	return render_template('piano.html')


@app.route('/processfeedback', methods = ['POST'])
def processfeedback():
	# Insert the submitted data into the database
	# Extract all data from the database
	# Send that data to feedback.html to display it
	feedback = request.form  # A dictionary {... 'name':__, 'email':__, 'comment':__ ...}
	name_ = feedback.get('name')
	email_ = feedback.get('email')
	comment_ = feedback.get('comment')

	# Prevent a page refresh from making duplicate entries
	equivalent_feedback = db.query("""SELECT * FROM feedback 
	                                     WHERE name = %s AND email = %s AND comment = %s""",
								  parameters=(name_, email_, comment_))
	if not equivalent_feedback:
		db.query("""INSERT INTO feedback (name, email, comment) 
					VALUES (%s, %s, %s)""",
					parameters=(name_, email_, comment_))
	feedback = db.query("""SELECT * FROM feedback""")
	print("\nFeedback entries:")
	print(feedback)
	return render_template('feedback.html', feedback=feedback)







