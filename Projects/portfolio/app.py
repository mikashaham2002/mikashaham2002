from flask import Flask, render_template

# Creates a new web application called app
app = Flask(__name__)

# Defines a route: which is the URL path visitors use to access a page
@app.route('/')
def home():
    print("Home route accessed")
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

# If the file is run directly, start the flask development server
if __name__ == '__main__':
    app.run(debug=True)
