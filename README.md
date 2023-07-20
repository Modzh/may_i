# May I F*ck You Bot -- Sexual Ed Check-up for your future Partner

## Development

 - Check out repo
 - Obtain .env file
 - `virtualenv env --python=python3.12`
 - `source env/bin/activate`
 - `pip install -r may_i/requirements.txt`
 - `export $(grep -v '^#' .env | xargs); python3 may_i/may_i_bot/manage.py runbot`

### Deployment

 - `git push heroku main:main`
