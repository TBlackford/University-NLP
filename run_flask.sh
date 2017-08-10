#TODO: Fix this line so that is just has "export FLASK_APP=nlp"
echo "Exporting Flask app" ; export FLASK_APP=nlp/__init__.py
echo "Setting debug to true" ; export FLASK_DEBUG=true
echo "Running Flask..." ; flask run
