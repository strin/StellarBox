import dropbox
import argparse
import json
import mechanize
import color, sys

def authenticate(app_key, app_secret, user_config):
	flow = dropbox.client.DropboxOAuth2FlowNoRedirect(app_key, app_secret)
	authorize_url = flow.start()
	print authorize_url
	print '1. Go to: ' + authorize_url
	print '2. Click "Allow" (you might have to log in first)'
	print '3. Copy the authorization code.'
	code = raw_input("Enter the authorization code here: ").strip()
	access_token, user_id = flow.finish(code)
	user_config['id'] = user_id
	user_config['token'] = access_token
	return user_config

def parse_course(course_id):
	pos = course_id.find('.')
	course_number = course_id[:pos]
	return course_number

def stellar_authorize(br, user_config):
	color.beginTitle()
	sys.stdout.write('stellar authentication begins ... ')
	sys.stdout.flush()
	if br.title() == 'Account Provider Selection':
		br.select_form('IdPList')
		br.submit()
		br.form = list(br.forms())[1]
		br.form.find_control('j_username').value = user_config['username']
		br.form.find_control('j_password').value = user_config['password']
		br.submit()
	br.form = list(br.forms())[0] # manual reload.
	br.submit()
	print '[done]'
	color.end()

def stellar_grab(client, br, user_config, depth = 0):
	for link in list(br.links()):
		# recursively look for homework.
		if link.url.find('homework') != -1 and depth < 1:
			br.follow_link(link)
			stellar_grab(client, br, user_config, 1)
			br.back()
		# look for lecture files with given 'ext'.
		for ext in user_config['ext']:
			if url_get_ext(link.url) == ext:
				break
		if url_get_ext(link.url) == ext: # find key files.
			name = url_get_filename(link.url)
			path = output+name
			if dirmap.has_key(name):
				continue
			print '\tfound new file: ', name
			br.follow_link(link)
			response = br.response().read()
			temp = open('temp', 'wb')
			temp.write(response)
			temp.close()
			temp = open('temp', 'rb')
			client.put_file(path, temp)
			br.back()

def url_get_filename(url):
	fs = url.split('/')
	return fs[len(fs)-1]

def url_get_ext(url):
	name = url_get_filename(url)
	name = name.split('.')
	return '.'+name[len(name)-1]

def dropbox_dirmap(client, path):
	dirmap = dict()
	folder_metadata = client.metadata(path)
	for f in folder_metadata['contents']:
		fs = f['path'].split('/')
		dirmap[fs[len(fs)-1]] = 1
	return dirmap


color.beginRed()
print 'StellarBox v1.0'
color.end()

app_key = 'mkk4ergebdfiklv'
app_secret = '6cbulm93inoaas3'

parser = argparse.ArgumentParser()
parser.add_argument('-c', nargs=1)
args = parser.parse_args()

config_path = args.c[0]
# user_config = config.readmap(config_path)
user_config = json.loads(open(config_path).read())

if not user_config.has_key('token') \
		or user_config['token'] == '':
	user_config = authenticate(app_key, app_secret, user_config)
	config.writemap(config_path, user_config)

client = dropbox.client.DropboxClient(user_config['token'])

br = mechanize.Browser()
br.set_handle_robots(False)


for cid in range(len(user_config['course'])):
	course = user_config['course'][cid]
	output = user_config['output'][cid]
	br.open('http://stellar.mit.edu/S/course/'+str(parse_course(course))+'/'+\
		user_config['semester']+'/'+course+'/materials.html')
	if br.title() == 'Account Provider Selection': # authentication needed.
		stellar_authorize(br, user_config)
		br.open('http://stellar.mit.edu/S/course/'+str(parse_course(course))+'/'+\
		user_config['semester']+'/'+course+'/materials.html')
	color.beginRed()
	print 'Diving into course '+course+':'
	color.end()
	dirmap = dropbox_dirmap(client, output)
	
	color.beginRed()
	print '[Done]'
	color.end()

	stellar_grab(client, br, user_config)

