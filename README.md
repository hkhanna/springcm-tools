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

## Deployment - Part I
1. A vm must exist (on, e.g., DigitalOcean) that has username harry and the appropriate ssh public key installed in `/home/harry/.ssh`. 
1. File `/etc/sudoers.d/harry` must exist with the line `harry ALL=(ALL) NOPASSWD:ALL`
1. Eventually, all this user admin stuff should be handled by an Ansible playbook.


## Deployment - Part II
1. Deployment currently tested on `debian/stretch`. 
1. Make sure there's a `secrets.env` file in the prod directory. Copy over `secrets.env.example` for an example.
1. Run `DJANGO_SECRET_KEY=xxx python manage.py check --deploy --settings=config.settings.production`
2. In the prod directory, test the deployment with `vagrant up`
3. `ansible-playbook -i vagrant.localhost site.yml`
4. Visit `http://127.0.0.1:8080` and make sure the application is running properly. If not, you can get into the vm with `vagrant ssh`.
5. If all is good, run `ansible-playbook -i springcm.khanna.cc site.yml`
6. Run `vagrant destroy`