#!/usr/bin/env python
import argparse
import json
import os
import trivium


def main():
	parser = build_parser()
	args = parser.parse_args()
	print(args)

	if args.subparser_name == 'new':
		return add_new_template(args)
	else:
		parser.print_help()
		exit(1)



def build_parser():
	parser = argparse.ArgumentParser(prog='templatetools.py')

	# Top-level qargs
	parser.add_argument('--verbose', action='store_true', help='Verbose output')
	
	# Subparsers
	subparsers = parser.add_subparsers(title='subcommands',
									   description='valid subcommands',
									   dest='subparser_name',
									   help='sub-command help')

	# create the parser for the "new" command
	parser_a = subparsers.add_parser('new', help='new help')
	parser_a.add_argument('--model', type=str, required=True, help='Model ID in the form <org:project>')
	parser_a.add_argument('--name', type=str, default='Trivium Template', help='The template name')
	parser_a.add_argument('--description', type=str, default='', help='The template description')

	# Return the parser
	return parser


def add_new_template(args):
	print('Adding new template ...')

	# The ID of the model we will analyze
	model = args.model

	# Verify we have access to trivium
	try:
		me = trivium.api.user.whoami()
		username = me['username']
	except:
		print('Error: Cannot login to Trivium.')
		return 1


	# Verify we have access to the model
	try:
		proj = trivium.api.project.get(model)
		org = proj['org']
		role = proj['permissions'][username]
	except Exception as e:
		print(e)
		print('Error: You do not have access to this model.')
		return 1

	ret = create_template(args, proj)
	return ret


def create_template(args, project):
	model = args.model 

	# Get the model
	fields = ','.join([
		'id', 'name', 'value', 'parent', 'type', 'documentation', 'custom',
		'archived', 'source', 'target'
	])
	element_filter = { 'fields': fields }
	elements = trivium.api.element.get(model, params=element_filter)

	# Make the project directory
	dirname = os.path.join('.', 'templates', project['org'], project['id'])
	os.makedirs(dirname, exist_ok=True)

	# Create the template
	template = {
		'metadata': {
			'id': project['id'],
			'name': project['name']
		},
		'model': elements
	}
	template_filename = os.path.join(dirname, f'{project["id"]}.json')
	with open(template_filename, 'w') as f:
		f.write(json.dumps(template, indent=4))

	# Create the metadata file
	metadata = {
		'id': model,
		'name': args.name,
		'description': args.description
	}
	metadata_filename = os.path.join(dirname, f'metadata.json')
	with open(metadata_filename, 'w') as f:
		f.write(json.dumps(metadata, indent=4))


	readme_filename = os.path.join(dirname, f'README.md')
	with open(readme_filename, 'w') as f:
		f.write(f'# {args.name}')
		f.write(' ')
		f.write(f'{args.description}')

if __name__ == '__main__':
	exit(main())