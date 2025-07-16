"""
Odoo Production Setup Scripts - Python Version
Converts the bash scripts for secure secrets management, deployment, and backup
"""

import os
import sys
import subprocess
import secrets
import string
import bcrypt
import tarfile
import shutil
import socket
import time
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import argparse
import json

class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    NC = '\033[0m'  # No Color


class OdooSetup:
    """Main class for Odoo production setup"""


    def __init__(self):
        self.secrets_dir = Path("/opt/MEIDAI/defaulties")
        self.backup_dir = Path("/opt/MEIDAI/backup")
        self.config_dir = Path("/opt/MEIDAI/config")

        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def print_colored(self, message: str, color: str = Colors.NC):
        """Print colored message to terminal"""
        print(f"{color}{message}{Colors.NC}")

    def generate_password(self, length: int = 25) -> str:
        """Generate a secure random password"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def run_command(self, command: list, capture_output: bool = False) -> subprocess.CompletedProcess:
        """Run a shell command safely"""
        try:
            return subprocess.run(
                command,
                capture_output=capture_output,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            self.print_colored(f"Command failed: {' '.join(command)}", Colors.RED)
            self.print_colored(f"Error: {e}", Colors.RED)
            raise

    def setup_secrets(self):
        """Set up secure secrets for Odoo production"""
        self.print_colored("Setting up secure secrets for Odoo production...", Colors.GREEN)

        # Create secrets directory with proper permissions
        self.secrets_dir.mkdir(exist_ok=True)
        os.chmod(self.secrets_dir, 0o700)

        # Generate passwords for each service
        secrets_config = {
            'postgresCTRL.txt': 'Database password',
            'redisCTRL.txt': 'Redis password',
            'odooADMIN.txt': 'Odoo admin password'
        }

        for filename, description in secrets_config.items():
            filepath = self.secrets_dir / filename
            if not filepath.exists():
                password = self.generate_password()
                filepath.write_text(password)
                os.chmod(filepath, 0o600)
                self.print_colored(f"✓ Generated {description.lower()}", Colors.GREEN)
            else:
                self.print_colored(f"✓ {description} file exists", Colors.YELLOW)

        # Generate Traefik basic auth hash
        traefik_auth_file = self.secrets_dir / "traefik_auth.txt"
        if not traefik_auth_file.exists():
            username = input("Enter username for Traefik dashboard: ")
            password = input("Enter password for Traefik dashboard: ")

            # Generate bcrypt hash
            hash_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            hash_str = hash_bytes.decode('utf-8')

            auth_string = f"{username}:{hash_str}"
            traefik_auth_file.write_text(auth_string)
            os.chmod(traefik_auth_file, 0o600)

            self.print_colored("✓ Generated Traefik authentication", Colors.GREEN)
            self.print_colored("Add this to your .env file:", Colors.YELLOW)
            print(f"TRAEFIK_BASIC_AUTH={auth_string}")
        else:
            self.print_colored("✓ Traefik auth file exists", Colors.YELLOW)

        # Create encrypted backup if GPG is available
        self.create_secrets_backup()

        # Display passwords for initial setup
        self.display_initial_passwords()

        # Create cleanup script
        self.create_cleanup_script()

        self.print_colored("✓ Secrets setup complete!", Colors.GREEN)
        self.print_next_steps()

    def create_secrets_backup(self):
        """Create encrypted backup of secrets if GPG is available"""
        try:
            subprocess.run(['gpg', '--version'], capture_output=True, check=True)
            self.print_colored("Creating encrypted backup of secrets...", Colors.GREEN)

            self.backup_dir.mkdir(exist_ok=True)
            date_str = datetime.now().strftime("%Y%m%d")
            backup_file = self.backup_dir / f"secrets-backup-{date_str}.tar.gz.gpg"

            # Create tar archive and encrypt
            with tarfile.open(mode='w:gz', fileobj=subprocess.Popen(
                ['gpg', '--cipher-algo', 'AES256', '--compress-algo', '1',
                 '--symmetric', '--output', str(backup_file)],
                stdin=subprocess.PIPE
            ).stdin) as tar:
                for file in self.secrets_dir.glob("*.txt"):
                    tar.add(file, arcname=file.name)

            self.print_colored(f"✓ Encrypted backup created in {self.backup_dir}", Colors.GREEN)

        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_colored("⚠ GPG not found, skipping encrypted backup", Colors.YELLOW)

    def display_initial_passwords(self):
        """Display passwords for initial setup"""
        self.print_colored("\n=== INITIAL PASSWORDS (SAVE THESE SECURELY) ===", Colors.GREEN)

        passwords = {
            'Database Password': self.secrets_dir / 'postgresCTRL.txt',
            'Redis Password': self.secrets_dir / 'redisCTRL.txt',
            'Odoo Admin Password': self.secrets_dir / 'odooADMIN.txt'
        }

        for name, file_path in passwords.items():
            if file_path.exists():
                password = file_path.read_text().strip()
                self.print_colored(f"{name}: {password}", Colors.YELLOW)

        self.print_colored("\n⚠ Store these passwords in your password manager!", Colors.RED)
        self.print_colored("⚠ These files will be deleted after first successful startup", Colors.RED)

    def create_cleanup_script(self):
        """Create cleanup script for password files"""
        cleanup_script = self.secrets_dir / "cleanup-displayed-passwords.py"
        cleanup_content = '''#!/usr/bin/env python3

import os
from pathlib import Path

def main():
    print("This will remove the readable password files and keep only the Docker secrets.")
    response = input("Are you sure? (y/N): ").strip().lower()

    if response == 'y':
        secrets_dir = Path("./secrets")
        for file in secrets_dir.glob("*.txt"):
            file.unlink()
        print("Cleaned up temporary password files")
    else:
        print("Cleanup cancelled")

if __name__ == "__main__":
    main()
'''
        cleanup_script.write_text(cleanup_content)
        os.chmod(cleanup_script, 0o755)

    def print_next_steps(self):
        """Print next steps for deployment"""
        self.print_colored("Next steps:", Colors.YELLOW)
        print("1. Update your .env file with the domain and email")
        print("2. Run: python3 setup.py deploy")
        print("3. Test the deployment")
        print("4. Run: python3 /opt/defaulties/cleanup-displayed-passwords.py")

    def load_env_file(self) -> dict:
        """Load environment variables from .env file"""
        env_vars = {}
        env_file = Path('.env')

        if not env_file.exists():
            self.print_colored("Error: .env file not found. Please create one based on the template.", Colors.RED)
            sys.exit(1)

        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip().strip('"\'')

        return env_vars

    def check_dns(self, domain: str) -> bool:
        """Check if DNS is configured for the domain"""
        try:
            socket.gethostbyname(domain)
            return True
        except socket.gaierror:
            return False

    def deploy(self):
        """Deploy Odoo production with Traefik"""                                                             
        self.print_colored("Starting Odoo production deployment with Traefik...", Colors.GREEN)
       # Pre-flight checks
        self.print_colored("Running pre-flight checks...", Colors.YELLOW)                              
        
        # Load environment variables
        env_vars = self.load_env_file()
        # Check if secrets are set up
        if not self.secrets_dir.exists() or not (self.secrets_dir / "postgresCTRL.txt").exists():
            self.print_colored("Setting up secrets first...", Colors.YELLOW)
            self.setup_secrets()

        # Check if config directory exists
        if not self.config_dir.exists():
            self.config_dir.mkdir(exist_ok=True)
            self.print_colored("✓ Created config directory", Colors.GREEN)

        # Validate domain
        domain = env_vars.get('DOMAIN', '')
        if not domain or domain == 'your-domain.com':
            self.print_colored("Error: Please set a valid DOMAIN in your .env file", Colors.RED)
            sys.exit(1)

        # Test DNS resolution
        if not self.check_dns(domain):
            self.print_colored(f"⚠ Warning: DNS for {domain} might not be configured", Colors.YELLOW)
            response = input("Continue anyway? (y/N): ").strip().lower()
            if response != 'y':
                sys.exit(1)

        # Start services
        self.print_colored("Starting services...", Colors.GREEN)
        self.run_command(['docker', 'compose', 'up', '-d'])

        # Wait for services to be ready
        self.print_colored("Waiting for services to be ready...", Colors.YELLOW)
        time.sleep(30)

        # Health check
        self.print_colored("Checking service health...", Colors.YELLOW)
        self.run_command(['docker', 'compose', 'ps'])

        # Test Odoo accessibility
        self.test_odoo_access(domain)

        # Display deployment information
        self.display_deployment_info(domain)

    def test_odoo_access(self, domain: str):
        """Test if Odoo is accessible via HTTPS"""
        try:
            response = requests.get(f"https://{domain}", timeout=10, verify=False)
            if "Odoo" in response.text:
                self.print_colored("✓ Odoo is accessible via HTTPS", Colors.GREEN)
            else:
                self.print_colored("⚠ Odoo might not be ready yet, check logs with: docker compose logs odoo", Colors.YELLOW)
        except requests.RequestException:
            self.print_colored("⚠ Could not verify Odoo accessibility, check logs with: docker compose logs odoo", Colors.YELLOW)

    def display_deployment_info(self, domain: str):
        """Display deployment completion information"""
        self.print_colored("\n=== DEPLOYMENT COMPLETE ===", Colors.GREEN)
        self.print_colored("Access URLs:", Colors.YELLOW)
        print(f"Odoo: https://{domain}")
        print(f"Traefik Dashboard: https://traefik.{domain}")

        self.print_colored("\nUseful commands:", Colors.YELLOW)
        print("View logs: docker logs -f [service]")
        print("Restart: docker restart [service]")
        print("Stop: docker compose down")
        print("Backup: python3 setup.py backup")

    def backup(self, backup_path: str = "/opt/MEIDAI/backups", retention_days: int = 7):
        """Create comprehensive backup of Odoo system"""
        self.print_colored("Starting Odoo backup...", Colors.GREEN)

        backup_dir = Path(backup_path)
        backup_dir.mkdir(parents=True, exist_ok=True)

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Database backup
        self.print_colored("Backing up database...", Colors.YELLOW)
        db_backup_file = backup_dir / f"db_backup_{date_str}.sql.zst"
        with open(db_backup_file, 'wb') as f:
            # Docker exec to dump database and compress
            dump_process = subprocess.Popen(
                ['docker', 'compose', 'exec', '-T', 'db', 'pg_dump', '-U', 'odoo', 'postgres'],
                stdout=subprocess.PIPE
            )
            compress_process = subprocess.Popen(
                ['zstd', '-19'],
                stdin=dump_process.stdout,
                stdout=f
            )
            dump_process.stdout.close()
            compress_process.wait()

        # Filestore backup
        self.print_colored("Backing up filestore...", Colors.YELLOW)
        filestore_backup_file = backup_dir / f"filestore_backup_{date_str}.tar.zst"
        with open(filestore_backup_file, 'wb') as f:
            tar_process = subprocess.Popen([
                'docker', 'run', '--rm',
                '-v', 'odoo_production_setup_odoo_web_data:/data',
                '-v', f"{backup_dir}:/backup",
                'alpine', 'tar', '-cf', '-', '-C', '/data', '.'
            ], stdout=subprocess.PIPE)

            compress_process = subprocess.Popen(
                ['zstd', '-19'],
                stdin=tar_process.stdout,
                stdout=f
            )
            tar_process.stdout.close()
            compress_process.wait()

        # Config backup
        self.print_colored("Backing up configuration...", Colors.YELLOW)
        config_backup_file = backup_dir / f"config_backup_{date_str}.tar.zst"
        with open(config_backup_file, 'wb') as f:
            tar_process = subprocess.Popen(
                ['tar', '-cf', '-', './config', './secrets'],
                stdout=subprocess.PIPE
            )
            compress_process = subprocess.Popen(
                ['zstd', '-19'],
                stdin=tar_process.stdout,
                stdout=f
            )
            tar_process.stdout.close()
            compress_process.wait()

        # Container images backup
        self.print_colored("Backing up container images...", Colors.YELLOW)
        images_backup_file = backup_dir / f"images_backup_{date_str}.tar.zst"
        with open(images_backup_file, 'wb') as f:
            save_process = subprocess.Popen([
                'docker', 'save', 'odoo:17', 'postgres:15-alpine',
                'traefik:v3.0', 'redis:7-alpine'
            ], stdout=subprocess.PIPE)

            compress_process = subprocess.Popen(
                ['zstd', '-19'],
                stdin=save_process.stdout,
                stdout=f
            )
            save_process.stdout.close()
            compress_process.wait()

        # Cleanup old backups
        self.print_colored("Cleaning up old backups...", Colors.YELLOW)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        for backup_file in backup_dir.glob("*.zst"):
            if backup_file.stat().st_mtime < cutoff_date.timestamp():
                backup_file.unlink()

        # Create manifest
        self.print_colored("Creating backup manifest...", Colors.YELLOW)
        manifest_file = backup_dir / f"manifest_{date_str}.txt"
        manifest_content = f"""Odoo Backup Manifest
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Database: db_backup_{date_str}.sql.zst
Filestore: filestore_backup_{date_str}.tar.zst
Config: config_backup_{date_str}.tar.zst
Images: images_backup_{date_str}.tar.zst
"""
        manifest_file.write_text(manifest_content)

        self.print_colored("✓ Backup completed successfully", Colors.GREEN)
        self.print_colored("Backup files created:", Colors.YELLOW)

        # List backup files
        for backup_file in backup_dir.glob(f"*_{date_str}*"):
            size = backup_file.stat().st_size
            size_mb = size / (1024 * 1024)
            print(f"{backup_file.name}: {size_mb:.1f}MB")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Odoo Production Setup')
    parser.add_argument('command', choices=['setup-secrets', 'deploy', 'backup'],
                       help='Command to execute')
    parser.add_argument('--backup-path', default='/opt/MEIDAI/backups',
                       help='Path for backup files')
    parser.add_argument('--retention-days', type=int, default=7,
                       help='Number of days to retain backups')

    args = parser.parse_args()

    setup = OdooSetup()

    if args.command == 'setup-secrets':
        setup.setup_secrets()
    elif args.command == 'deploy':
        setup.deploy()
    elif args.command == 'backup':
        setup.backup(args.backup_path, args.retention_days)


if __name__ == "__main__":
    main()



