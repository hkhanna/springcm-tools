# springcm-tools
A collection of SpringCM tools running on the web

## Installation for Development
Installation instructions will go here. 
- [ ] /path/to/python3 -m venv /path/to/venv
- [ ] source /path/to/venv/bin/activate
- [ ] git clone
- [ ] cd into directory
- [ ] pip install -r requirements/local.txt
- [ ] python manage.py migrate
- [ ] python manage.py runserver

## Deployment
1. Deployment currently tested on `debian/stretch`. 
1. Make sure there's a `secrets.env` file in the prod directory. Copy over `secrets.env.example` for an example.
2. In the prod directory, test the deployment with `vagrant up`
3. `ansible-playbook -i vagrant site.yml`
4. Visit `http://127.0.0.1:8080` and make sure the application is running properly.
5. If all is good, run `ansible-playbook -i prod site.yml`
6. Run `vagrant destroy`
 
- [ ] Django deployment checklist
- [ ] Check out deployment section of fullstackpython.com
