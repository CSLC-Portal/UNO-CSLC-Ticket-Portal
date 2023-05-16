# UNO-CSLC-Ticket-Portal

The following is an implementation of a ticket portal system for the UNO Computer Science Learning Center (CSLC). This portal will allow students to create tickets that include information about classes and assignments they want help with from the CSLC tutors. It will also be utilized by the CSLC tutors in seeing the available tickets submitted by students and additionally provide anonymous statistics for administrators suggesting classes that most students may be struggling with and the kinds of assignments they are requesting assistance with.

The portal is a public-facing website that allows students to submit a request for help anytime, and anywhere. Students will optionally be allowed to sign in using their UNO-provided email as a way to auto-fill some of the content that may be asked for in the form, otherwise, guests will also be able to submit tickets without authentication (they will need to provide name and contact information if this is the case).

The recent loss of a previous tutoring portal is a major motivation for the development of this project. In addition, the transition to online classes and online tutoring has driven inspiration for some new features as well, such as marking tickets as online/on-campus depending on whether the student has been helped remotely or in person and auto-calculating the time spent on helping a student (which was previously manually provided by a tutor). These features will help in providing useful statistics about the kind of help students are requesting from the tutoring center and how often.

Visit the [docs](https://claytonmsafranek.github.io/UNO-CSLC-Ticket-Portal/) for more info.

## Release Notes

The following is a list of currently existing features in the application:

- Form for submitting a ticket.
- Page for viewing tickets.
- Ability to claim/close tickets.
- Editable tickets (can update most fields set for the ticket).
- Administrative console backend for adding tutors, courses, configuring the portal app and downloading reports.
- Tutor, Admin and Owner permissions (restrict views for authenticated users based on permission level).
- A home page that asks to log in or shows username when logged in.
- Login management; only authenticated users can view certain pages (Unauthenticated users will be redirected to Microsoft sign-in).
- Automatically generated, self-signed SSL certificates for HTTPS connections

Next Milestone [Milestone 6](https://github.com/claytonmsafranek/UNO-CSLC-Ticket-Portal/milestone/6).

## Configuration

### Flask
The program can be run locally for testing and development. The main file is `portal/app/__init__.py` which contains a definition for the `create_app()` factory function (flasks expect this and automatically calls the function). Before you can run the app, you need to install the dependencies via `pip install -r portal/requirements.txt` (assuming your current working directory is in the root folder of this project). This installs the core dependencies for the project, you can also install the development dependencies located in `portal/requirements/dev.txt` if you intend on running tests and linting. The following commands are one way to locally run the program:

```
export FLASK_APP=portal/app
flask run --debug
```

The flask app (located in `portal/`) has a `default_config.py` script providing some default configuration for the project. *This does not need to be changed to configure the project*. If you would like to set additional options or override existing ones, then create a `.env` file in the `portal/` directory which sets the options to the desired values (prefixed with `FLASK_`).

Example `portal/.env`:
```env
# Flask configuration settings (NOTE: true/false must be all lowercase! Must be prefixed with FLASK_)

FLASK_SESSION_COOKIE_SECURE=false
FLASK_SECRET_KEY=my_secret
```

These values will override any values specified in `default_config.py`.

Using flask debug mode is recommended for getting feedback on errors rather than HTTP internal server error status codes. The local flask app will use a local sqlite3 database (which should be created in `portal/instance/` at runtime). This should make it easy to ensure that the application is saving objects to the database correctly. The application needs to be configured with an *owner* account by setting the `FLASK_DEFAULT_OWNER_EMAIL` to a desired email environment variable in the `.env` file. **This is necessary in deployment and development for using the application as certain routes are restricted to higher permission levels only (of which owner is the highest)**. NOTE: You will need to configure Microsoft authentication to login, which is explained later.

#### Visual Studio Code
Additionally, if you are using Visual Studio Code you can configure a `launch.json` and `settings.json` file for debugging and automatic linting. You can download and use the sample [launch.json](https://gist.github.com/Mr-Oregano/9873bebd7f8d871e36e5c5361b4bad9d) and [settings.json](https://gist.github.com/Mr-Oregano/388bbff7736d6fd7f166b697cb6ed48d) files and copy them into a `.vscode/` folder in the root directory of the project. *Make sure you have [flake8](https://pypi.org/project/flake8/) and [pytest](https://pypi.org/project/pytest/) installed!*. You can install these via `pip install -r portal/requirements/dev.txt`

For other IDE/editors you are on your own in terms of setup.
### Microsoft Azure App Directory Authentication

The application uses the Azure App Directory API for authentication and will need to be registered as a legitimate application in the app directory at https://portal.azure.com/. This requires some configuration on behalf of the user.

Besides the client ID, which will be provided by Microsoft when registering the app, the portal requires an authority URL (which would be `https://login.microsoftonline.com/common` for a multi-tenant registration). It currently will also need a client secret, which can be generated on the Azure portal (in the future it is planned to allow a certificate as well). Finally, it will require a redirect URI which matches the URI set on the Azure portal site. Microsoft requires a domain name and connection using HTTPS for this, the API will redirect the user to this URI when the user signs in, which will provide authentication information about the user to the application.

All these values can currently be set as environment variables in the `portal/.env` file. The following is an example:
```
# Application (client) ID of app registration
AAD_CLIENT_ID=some_id_with_a_bunch_of_numbers_2342347882

AAD_CLIENT_SECRET=my_secret_KEEP_THIS_SAFE

# For multi-tenant app
AAD_AUTHORITY=https://login.microsoftonline.com/common

AAD_REDIRECT_PATH=/getAToken
```

This process is covered in more detail in [this quickstart guide](https://learn.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) by Microsoft.

## Deployment Strategies
The project uses docker and docker-compose to orchestrate and manage different subsystems, i.e. databases, reverse proxies, and a web server.

Subservices will exist inside isolated docker containers and will communicate with each other (using docker’s bridge network drivers) to send data back and forth. The Nginx web server container will forward network requests to the portal flask app container which will in turn access the database container to pull and update data.

Clients will interface with the application through a browser and an internet connection.

### Nginx
The Nginx web server can be configured via its `nginx/nginx.conf` file. This configuration file is simply copied into the docker container which is generated by docker-compose and replaces the default configuration for Nginx.

When using URLs or connections to applications in different containers make sure you provide the name of the container as the hostname. Example: `http://portal:8000` would connect to the application on port 8000 in the "portal" container using the HTTP scheme.

### MySQL
By default, the docker-compose file will auto-generate a docker MySQL image and set the `FLASK_SQLALCHEMY_DATABASE_URI` env variable (this will override any settings in `default_config.py` and in `portal/.env`). The MySQL database can be configured via its configuration file located in `mysql/mysql.cnf`, which will extend/override any default configurations existing in the MySQL image.

The Flask app will use the local MySQL docker database when running in production (via docker-compose). However, if you wish to use a custom remote MySQL server then you will need to change the `FLASK_SQLALCHEMY_DATABASE_URI` in the `docker-compose.yml` file to refer to that database. The default installed database connector is `PyMySQL`, if a different one is desired it will need to be installable via pip (so that docker can install it in the container), otherwise, this will require manual intervention from the user.

### Deployment
When deploying this application, however, the portal app uses the gunicorn wsgi web server to run the application instead of flask. This is a production-ready server designed to handle more requests than flask. The `portal` and `mysql` containers will only be accessible through localhost on port 8000 and port 3306 respectively. Instead, the `nginx` container will be remotely accessible on either port 80 (HTTP) or port 443 (HTTPS) which will forward requests to the flask app.

These settings are already automatically configured by docker and docker-compose so there shouldn't be a need to do anything besides running `docker-compose up -d`, which will build the images and then run them. Additional settings can be configured in the `docker-compose.yml` file or the individual `Dockerfile`'s for each subsystem.

The application can be deployed on any system running `docker` and `docker-compose`. If deploying on Microsoft Azure Cloud, the application can be installed as an [App Service](https://learn.microsoft.com/en-us/azure/app-service/overview) running a multi-container app (The `docker-compose.yml` file will need to be modified for this and any pre-generated images will either need to be pushed to azure or docker-hub). Unfortunately, this does not easily support automatic deployment without using the Azure CLI. Automatic deployment is currently being investigated.

### Production
Deploying this project for production currently requires manual intervention from the user to set it up properly. Aside from registering the application on Azure App Directory for Microsoft authentication, a legitimate SSL certificate will need to be generated and renewed in some way (preferably automatically) and provided to the Nginx docker container. By default, the provided configuration will automatically generate a self-signed certificate (in `nginx/Dockerfile`) using some settings from the environment. However, the user will have to provide their own certificate in a production environment.

The Nginx template configuration in `nginx/nginx.conf` will need to be updated to reference these certificates and potentially configure other settings. If generated manually, the certificates will need to be copied into the Nginx docker container (preferably using the `COPY` command in `nginx/Dockerfile`) and will need to be referenced in `nginx/nginx.conf` if they have a different name other than `FLASK_SERVER_NAME`.

The server name will be taken from the `FLASK_SERVER_NAME` environment variable that way this avoids duplication and allows the Flask application to access the hostname as well. A complete, sample .env file might look as follows:

```
# Flask configuration settings (NOTE: true/false must be all lowercase! Must be prefixed with FLASK_)
FLASK_SERVER_NAME=cslc-portal.eastus.cloudapp.azure.com

# Microsoft Azure App Directory Auth

AAD_CLIENT_ID=some_id_with_a_bunch_of_numbers_2342347882
AAD_CLIENT_SECRET=my_secret_KEEP_THIS_SAFE
AAD_AUTHORITY=https://login.microsoftonline.com/common
AAD_REDIRECT_PATH=/getAToken

# Default SSL Certificate Config

CERT_COUNTRY=US
CERT_STATE=NE
CERT_LOC=Omaha
CERT_ORG=GACK
CERT_ORGUNIT=CAPSTONE
```

By default, the SSL `CERT_` values are used in the `docker-compose.yml` and `nginx/Dockerfile` files, and they *could* be used for generating a CA-signed SSL certificate. However, depending on how the user chooses to deal with SSL they may not be needed and the aforementioned files will need to be reconfigured.
