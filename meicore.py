
from datetime import datetime
#from jinja2 import Environment, FileSystemLoader 
import os 
from pathlib import Path
import argparse
import json
"""
def render_compose(context, template='basic-compose.j2'):
    env = Environment(loader=FileSystemLoader("configurations/templates"))
    template = env.get_template(template)
    return template.render(**context)
"""


import argparse

def cli(): 
    
    parser = argparse.ArgumentParser(
        description="MeiCore Infrastructure Management",
        prog="MeiCore"
    )

    # Add a version argument to the main parser
    parser.add_argument(
        '--version',
        '-v',
        action='version',
        version='%(prog)s 1.00.00 BETA',
        help="Show program's version number and exit"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new project')
    init_parser.add_argument('project_name', help='Name of the project to create')
    init_parser.add_argument('--template', '-t', choices=['core','all'], default='core', help='Project template type')
    init_parser.add_argument('--env_type', '-e', choices=['prod', 'stage', 'dev'], default='dev', help='Set your environment type')
    init_parser.add_argument('--network', '-n', default='core', help="set your custom network label that will be used to create seperate connectors in your custom docker composes")
    init_parser.add_argument('--storage', '-s', default='core_vol', help="set your custom mount binds, leave blank if you want to keep the defaults")
    # Deploy command  
    deploy_parser = subparsers.add_parser('deploy', help='Deploy your first stack')
    deploy_parser.add_argument('application', help='Type in the domain your stack will be hosted on (.e.g. domain.com or sub.domain.com)')
    deploy_parser.add_argument('--tag', '-t', required=True, help='Application template (e.g. wordpress/latest)')
    deploy_parser.add_argument('--extend_network', '-ex', required=True, default=True, help="Extend your application stack's network to work with core services proxy")

    return parser.parse_args()

def find_manifest():
    "Search meicore.json for further seeking"
    current = Path.cwd()

    for parent in [current] + list(current.parents):
        manifest_path = parent / 'meicore.json'
        if manifest_path.exists():
            return manifest_path
        print('Err: No meicore.json found. Run \'meicore init\' first.')
        exit(1)
def load_manifest():
    "Manifest loading mechanism"
    manifest_path = find_manifest()
    with open(manifest_path, 'r') as f:
        return json.load(f)
    
def get_path():
    "Getting project parameters"
    config = load_manifest()
    return Path(config["project_name"])

def main():
    # Parse arguments
    args = cli()
    current_time = datetime.now()

    # Handle commands
    if args.command == 'init':
        init_project(args.project_name, args.template, args.env_type, args.network, args.storage, current_time)
    elif args.command == 'deploy':
        deploy_application(args.application, args.tag, args.extend_network)
    # The 'else' block is no longer needed because of 'required=True'

def init_project(project_name, template, env_type, network, storage, current_time):
    projectID = Path(project_name)
    projectID.mkdir(exist_ok=True)

    DIR_STRUCT = [
        "core",
        "environments",
        "environments/templates",
        "configurations",
        "configurations/templates",
        "configurations/services",
        ".containers",
        "applications"
    ]
    
    for directory in DIR_STRUCT:
        (projectID / directory).mkdir(exist_ok=True)
    
    ct = current_time.strftime("%Y-%m-%d %H:%M:%S")
    config = {
        "project_name": project_name,
        "template": template,
        "created_at": ct,
        "core_services": [],
        "applications": {},
        "core_labels": {
            "Network":[network],
            "Volumes": [storage]
            }

    }
    core_manifest = {
        "Manifest Version": "{v0}",
        "created_at": ct,
        "project_tree": [str(projectID)]
    }

    env_templates = {
        "prod": "environments/templates/.prod.env.template",
        "stage":    "environments/templates/.stage.env.template",
        "dev": "environemnts/templates/.dev.env.template"
    }
    with open(projectID / "meicore.json", "w") as f:
        json.dump(config, f, indent=2)

    with open("manifest.json", "w") as f:
        json.dump(core_manifest, f, indent=2)

    with open(projectID / f"environments/templates/.{env_type}.env.template", "w") as f:
        f.write(f"#Environment: {env_type}\n")
        f.write(f"PROJECT_NAME={project_name}\n")
        f.write("# meicore will add pre-created environment variables here, edit values where necessary\n")

    print(f"Creating project: {project_name} with {template} template")
    
def deploy_application(application, tag, extend_network):
    config = load_manifest()
    project_path = Path(config["project_name"])
    app_dir = project_path / "applications" / application
    app_dir.mkdir(exist_ok=True)
    
if __name__ == "__main__":
    main()