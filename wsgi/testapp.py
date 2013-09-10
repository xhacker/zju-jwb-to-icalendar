#sucks 

import os
import random
import bottle

data_dir = os.getenv('OPENSHIFT_DATA_DIR', '~/app-root/data/')
repo_dir = os.getenv('OPENSHIFT_REPO_DIR', '~/app-root/repo/')
temp_dir = os.getenv('OPENSHIFT_TMP_DIR', '/tmp/')

@bottle.get('/')
@bottle.view(repo_dir + 'wsgi/view/index.html')
def index():
    return {}

@bottle.post('/grab')
def grab():
    param = list(map(bottle.request.forms.get, ['zju_username', 'zju_password']))
    if not all(param):
        # TODO: post a redirection to '/' or at least add  a link to it
        return 'Incomplete input fields. Needs username and password'
    temp_filename = '%.8x_%s.ics' %(random.getrandbits(32), param[0])
    # TODO: replace this with subprocess 
    err = os.popen('%s %s %s %s' %(
        repo_dir + 'grabber.py', 
        param[0], param[1], 
        '%s/%s' %(temp_dir, temp_filename))).read()
    if os.path.exists('%s/%s' %(temp_dir, temp_filename)):
        return bottle.static_file(temp_filename, root=temp_dir, download='%s.ics' %param[0])
    else:
        return err

# This must be added in order to do correct path lookups for the views
bottle.TEMPLATE_PATH.append(
    os.path.join(os.environ['OPENSHIFT_HOMEDIR'], 'runtime/repo/wsgi/views/'))

bottle.debug(True)
application = bottle.default_app()
