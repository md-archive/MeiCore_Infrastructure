import time 
from jinja2 import Environment, FileSystemLoader 
import os
import argparse

def render_compose(context, template='basic-compose.j2'):
    env = Environment(loader=FileSystemLoader("configurations/templates"))
    template = env.get_template(template)
    return template.render(**context)

parser = argparse.ArgumentParser(description="Generate Docker Compose infrastructure")
parser.add_argument("--service_name", required=True, help="Name of the application/service.")
parser.add_argument("--image", required=True, help="Docker image name")
parser.add_argument("--tag", default="latest", help="Docker image tag.")

args = parser.parse_args()


context = {
    "service_name": args.service_name,
    "image": args.image,
    "tag": args.tag,
    "external_port": args.external_port,
    "internal_port": args.internal_port
}
def banner(version):
    time.sleep(3)
    context = f'''
                                                    __  ___     _     __      _       ____  _____
                                                   /  |/  /__  (_)___/ /___ _(_)     / __ \/ ___/
                                                  / /|_/ / _ \/ / __  / __ `/ /_____/ / / /\__ \\
                                                 / /  / /  __/ / /_/ / /_/ / /_____/ /_/ /___/ /
                                                /_/  /_/\___/_/\__,_/\__,_/_/      \____//____/ v.{version}
                +-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-
                -                                                                                                                -
                +                                  Meidai OS Core Infrastructure Deployment Tool                                 +
                -                                                                                                                -
                +                                This is the first iteration of this piece of software                           +
                -+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
    '''
    
    