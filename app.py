from flask import Flask, flash, redirect, url_for, render_template, request, Response, session, jsonify
from flask_session.__init__ import Session
import time, string, random
from optimizer import *
from problem import *
from flask_login import current_user, login_user, logout_user, login_required
from models import db, User, login, Solution
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

app.secret_key = "5af7bbcaa06c3affd04111afb4be6749dc49fd16b46df68605285b6c800bd780192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///max3sat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

db.init_app(app)
login.init_app(app)
login.login_view = 'login'

# dictionary in which keys are sessions' ids and values are of type bool:
#  True - simulation should be active, False - if there was simulation running it must be stopped
active_simulations = dict()

UPLOAD_FOLDER = 'static/uploads/'

def run_experiment(problem, size_of_population, number_of_populations, probability_of_smart_mutation, probability_of_gene_mutation, 
	probability_of_crossover, probability_of_cross_gene, number_of_parents_considered, max_time):
	'''Runs optimization for specified amount of time. If user changes webpage optimization stops.
	Returns tuple:
	first element - number of fulfilled clauses
	second element - percent of fulfilled clauses
	third element - solution genotype'''

	start_time = time.time()
	optimizer = Optimizer(problem, size_of_population, number_of_populations, probability_of_smart_mutation, 
			probability_of_gene_mutation, probability_of_crossover, probability_of_cross_gene, number_of_parents_considered)
	optimizer.initialize()
	
	max_time_running = max_time
	start_time = time.time()
	best = None
	
	while (time.time() - start_time) < max_time_running:
		# check if simulation should be stopped (when active_simulations[session["id"]] == False)
		if not active_simulations[session["id"]]:
			return 0, 0, 0

		optimizer.run_iteration()
		best = optimizer.best_found
		
	return str(best.fitness()), str(best.quality()) + "%", best.code_genotype()

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
	'''Generates id of given size (size) and set of characaters (chars).'''
	return ''.join(random.choice(chars) for _ in range(size))

@app.before_first_request
def create_all():
	'''Creates database.'''
	db.create_all()

@app.route("/", methods=["POST", "GET"])
def home():
	'''Main route. When method is 'GET' renders template with form for optimization parameters and file. 
	When method is 'POST' reads values from form and if they are corrrect starts simulation and
	redirects to '/result".'''

	if request.method == 'POST':
		active_simulations[session["id"]] = False
		size_population = request.form['size_population']
		number_populations = request.form['number_populations']
		number_parents = request.form['number_parents']
		probability_crossover = request.form['probability_crossover']
		probability_gene_crossover = request.form['probability_gene_crossover']
		probability_smart_mutation = request.form['probability_smart_mutation']
		probability_gene_mutation = request.form['probability_gene_mutation']
		run_time = request.form['run_time']
		file_problem = request.files['file_problem']
		session["file_user_name"] = secure_filename(file_problem.filename)[:file_problem.filename.find('.txt')]

		# generate new file_name before upload, using file_name of user's file may cause problems
		# (for example when he tries to run file with same name from diffrent sessions)
		file_name = UPLOAD_FOLDER + id_generator()
		file_problem.save(file_name)
		session["file_name"] = file_name

		# cast parameters of simulation to required type
		try:
			session["size_population"] = int(size_population)
		except:
			flash("Size of population must be an Integer number")
			return redirect("/")

		try:
			session["number_populations"] = int(number_populations)
		except:
			flash("Size of populations must be an Integer number")
			return redirect("/")

		try:
			session["number_parents"] = int(number_parents)
		except:
			flash("Number of parents considered must be an Integer number")
			return redirect("/")

		try:
			session["probability_crossover"] = float(probability_crossover)
		except:
			flash("Probability of crossover must be a Real number")
			return redirect("/")

		try:
			session["probability_gene_crossover"] = float(probability_gene_crossover)
		except:
			flash("Probability of gene crossover must be a Real number")
			return redirect("/")

		try:
			session["probability_smart_mutation"] = float(probability_smart_mutation)
		except:
			flash("Probability of smart mutation must be a Real number")
			return redirect("/")

		try:
			session["probability_gene_mutation"] = float(probability_gene_mutation)
		except:
			flash("Probability of gene mutation must be a Real number")
			return redirect("/")

		try:
			session["run_time"] = int(run_time)
		except:
			flash("Run time must be an Integer number")
			return redirect("/")

		# prepare simulation of Max3Sat
		problem = Problem(3, session["file_name"])

		# proble.load() returns True if format of file was correct and False if there were problems with content
		# of the file
		if not problem.load():
			flash("Invalid content of source file with problem")
			return redirect("/")

		session["number_of_clauses"] = problem.number_of_clauses

		# assign True to active simulation before start of simulation
		active_simulations[session["id"]] = True
		result = run_experiment(problem, session["size_population"], session["number_populations"], session["probability_smart_mutation"], 
			session["probability_gene_mutation"], session["probability_crossover"], session["probability_gene_crossover"], 
			session["number_parents"], session["run_time"])

		session["coded_genotype"] = result[2]
		session["percentage"] = result[1]
		session["fulfilled_clauses"] = result[0]

		return redirect("/result")

	# assigning session id
	if "id" not in session:
		id = uuid.uuid4()
		session["id"] = id

	# assign False to active simulation
	# if there is simulation running, stop it
	active_simulations[session["id"]] = False

	return render_template("index.html")

@app.route("/about-us")
def aboutus():
	'''Renders template with information about page and used optimization algorithm.'''

	# if  there's id in session, 
	# assign False to active simulation
	# if there is simulation running, stop it
	if "id" in session:
		active_simulations[session["id"]] = False

	return render_template("about_us.html")
 
@app.route('/login', methods=['POST','GET'])
def login():
	'''If user is already authenticated redirects to '/your-account'. 
	On method 'GET' renders template with login (authentication) form. 
	On method 'POST' checks login information. It it's correct logs user otherwise flashes proper information.'''
	
	# if  there's id in session,
	# assign False to active simulation
	# if there is simulation running, stop it
	if "id" in session:
		active_simulations[session["id"]] = False

	if current_user.is_authenticated:
		return redirect('/your-account')
		
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		user = User.query.filter_by(email=email).first()
		
		if user is None:
			flash("Account with this email doesn't exist")
			return redirect('/login')
		elif not user.check_password(password):
			flash("Invalid password")
			return redirect('/login')
		else:
			login_user(user)
			return redirect('/your-account')

	return render_template('login.html')
 
@app.route('/register', methods=['POST','GET'])
def register():
	'''If user is already authenticated redirects to '/your-account'. 
	On method 'GET' renders template with registration (authentication) form. 
	On method 'POST' checks registration information. It it's correct registers user 
	otherwise flashes proper information.'''

	# if  there's id in session,
	# assign False to active simulation
	# if there is simulation running, stop it
	if "id" in session:
		active_simulations[session["id"]] = False

	if current_user.is_authenticated:
		return redirect('/your-account')
		
	if request.method == 'POST':
		email = request.form['email']
		password = request.form['password']
		confirm = request.form['confirm']

		if User.query.filter_by(email=email).first():
			flash('Account linked with this email already exists')
			return redirect('/register')
		elif password != confirm:
			flash("Passwords don't match")
			return redirect('/register')
			
		user = User(email=email)
		user.set_password(password)
		db.session.add(user)
		db.session.commit()
		return redirect('/login')
		
	return render_template('register.html')
 
@app.route('/logout')
def logout():
	'''If user is not authenticated redirects to '/login'. Otherwise logs out user and redirects to '/login'.'''

	# if  there's id in session,
	# assign False to active simulation
	# if there is simulation running, stop it
	if "id" in session:
		active_simulations[session["id"]] = False

	if not current_user.is_authenticated:
		return redirect('/login')

	logout_user()
	flash("Logout succesfull")
	return redirect('/login')

@app.route('/your-account')
def account():
	'''If user is not authenticated redirects to '/login'. Otherwise renders template with view
	of information stored in databased connected with user account.'''

	# if  there's id in session,
	# assign False to active simulation
	# if there is simulation running, stop it
	if "id" in session:
		active_simulations[session["id"]] = False

	if not current_user.is_authenticated:
		return redirect('/login')

	solutions_of_user = Solution.query.filter_by(user_id=current_user.id).all()

	solutions_ready = []
	index = 0

	for solution in solutions_of_user:
		solutions_ready.append((index, solution))
		index += 1

	return render_template("your_account.html", solutions_of_user=solutions_ready)

@app.route("/result")
def last_result():
	'''If user didn't run optimization algohithm and don't have any solutions to view redirects '/'. 
	Otherwise renders template with results, different template for authenticated and unauthenticated users.'''
	
	# if  there's id in session, 
	# assign False to active simulation
	# if there is simulation running, stop it
	if "id" in session:
		active_simulations[session["id"]] = False

	if "coded_genotype" in session:
		if current_user.is_authenticated:
			return render_template('result_auth.html', file_name=session["file_user_name"], percentage=session["percentage"],
				number_fullfilled_clauses=session["fulfilled_clauses"], number_clauses=session["number_of_clauses"], 
				result=session["coded_genotype"], size_population=session["size_population"], number_populations=session["number_populations"], 
				probability_smart_mutation=session["probability_smart_mutation"], probability_gene_mutation=session["probability_gene_mutation"], 
				probability_crossover=session["probability_crossover"], probability_gene_crossover=session["probability_gene_crossover"], 
				number_parents=session["number_parents"], run_time=session["run_time"])
		else:
			return render_template('result.html', file_name=session["file_user_name"], percentage=session["percentage"], 
				number_fullfilled_clauses=session["fulfilled_clauses"], number_clauses=session["number_of_clauses"], result=session["coded_genotype"], 
				size_population=session["size_population"], number_populations=session["number_populations"], 
				probability_smart_mutation=session["probability_smart_mutation"], probability_gene_mutation=session["probability_gene_mutation"], 
				probability_crossover=session["probability_crossover"], probability_gene_crossover=session["probability_gene_crossover"], 
				number_parents=session["number_parents"], run_time=session["run_time"])
	else:
		flash("No solutions to view.")
		return redirect('/')

@app.route("/get-file")
def get_file():
	'''If user don't have any solutions to download redirects to main route with 
	communicate 'No solutions to download.'.
	Otherwise return Response object and downloads user's solution on his computer.'''
	
	if "coded_genotype" in session:
		results = session["coded_genotype"]
		generator = (cell for row in results
						for cell in row)

		return Response(generator,
						mimetype="text/plain",
						headers={"Content-Disposition":
										f"attachment;filename=solution_{ session['file_user_name'] }.txt"})
	else:
		flash("No solutions to download.")
		return redirect("/")

@app.errorhandler(413)
def request_entity_too_large(error):
	'''Handle too big files.'''
	flash("File size is too big. Max file size is 5 MB.")
	return redirect("/")

@app.route('/save-solution')
def save():
	'''If user is not authenticated redirects to main route with communicate 'Acces denied'. 
	If user is authenticated and don't have any solutions to save redirects to main route with 
	communicate 'No solutions to save on your account.'.
	Otherwise saves user's solution in database and redirects him to view of his saved files.'''
	
	if not current_user.is_authenticated:
		flash("Access denied")
		return redirect('/')

	if "coded_genotype" not in session:
		flash("No solutions to save on your account.")
		return redirect('/')
		
	solution = Solution(user_id=current_user.id, name=session["file_user_name"],
	percentage=session["percentage"],
	solution=session["coded_genotype"],
	size_population=session["size_population"],
	number_populations=session["number_populations"],
	number_parents=session["number_parents"],
	probability_crossover=session["probability_crossover"],
	probability_gene_crossover=session["probability_gene_crossover"],
	probability_smart_mutation=session["probability_smart_mutation"],
	probability_gene_mutation=session["probability_gene_mutation"],
	run_time=session["run_time"])

	db.session.add(solution)
	db.session.commit()
	return redirect("/your-account")

if __name__ == "__main__":
	app.run()
