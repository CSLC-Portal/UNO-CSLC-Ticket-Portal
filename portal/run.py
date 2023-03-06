
# NOTE: The following code is for running locally ONLY!
#       This should NOT be used in production.

from app import app

def main():
    app.run(debug=True, host='0.0.0.0', port=8000)

if __name__ == '__main__':
    main()

#
