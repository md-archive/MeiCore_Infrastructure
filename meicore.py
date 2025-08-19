import time 
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

def main():
    parser = argparse.ArgumentParser(
        description="MeiCore Infrastructure Management",
        prog="meicore"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Init command
    init_parser = subparsers.add_parser('init', help='Initialize new project')
    init_parser.add_argument('project_name', help='Name of the project to create')
    init_parser.add_argument('--template', '-t', choices=['core','all'], default='core', help='Project template type')
    init_parser.add_argument('--env_type', '-e', choices=['prod', 'stage', 'dev'], default='dev', help='Set your environment type')
    
    # Deploy command  
    deploy_parser = subparsers.add_parser('deploy', help='Deploy infrastructure')
    deploy_parser.add_argument('--core-only', action='store_true', help='Deploy only core services')
    deploy_parser.add_argument('--all', '-a', action='store_true', help='Deploy everything (core + monitoring + apps)')
    
    # Version Command
    version_parser = subparsers.add_parser('version', help="Current Version")
    
    # 

    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'init':
        init_project(args.project_name, args.template, args.env_type)
    elif args.command == 'deploy':
        deploy_infrastructure(args)
    elif args.command == 'version':
        sw_version(args)
    else:
        parser.print_help()

def init_project(project_name, template, env_type):
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

    config = {
        "project_name": project_name,
        "template": template,
        "created_at": time.time(),
        "core_services": [],
        "applications": {}

    }
    env_gen = {
        "project_name" : project_name,
        "env" : env_type,
     
        }
    env_templates = {
        "prod": "environments/templates/.prod.env.template",
        "stage":    "environments/templates/.stage.env.template",
        "dev": "environemnts/templates/.dev.env.template"
    }
    with open(projectID / "meicore.json", "w") as f:
        json.dump(config, f, indent=2)

    with open(projectID / "environments/templates/{env_gen.env}", "w") as f:
        json.dump(env_gen, f, indent=2)

    for directory in DIR_STRUCT:
        (projectID / directory).mkdir(exist_ok=True)
    
    print(f"Creating project: {project_name} with {template} template")
    

def deploy_infrastructure(args):
    if args.all:
        print("Deploying full infrastructure...")
    elif args.core_only:
        print("Deploying core services only...")
    # Your deploy logic here

def sw_version(args):
    print('version 0B1')

if __name__ == "__main__":
    main()