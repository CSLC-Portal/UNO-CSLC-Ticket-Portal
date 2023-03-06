from app import app

@app.route('/')
def index():
    return 'Future site of the CSLC Tutoring Portal!'
