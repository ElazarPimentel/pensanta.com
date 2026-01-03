#!/usr/bin/env python3
"""
Portfolio Manager - SQLite-based portfolio management system
Replaces fragile bash scripts with robust Python
"""

import sqlite3
import json
import argparse
import sys
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime
import re

# Get script directory
SCRIPT_DIR = Path(__file__).parent.resolve()
DB_PATH = SCRIPT_DIR / 'portfolio.sqlite'
PROJECT_ROOT = SCRIPT_DIR.parent
PUBLIC_HTML = PROJECT_ROOT / 'public_html'
SCAN_ROOT = Path.home() / 'Documents/work/pensanta/websites'


class PortfolioManager:
    """Manage portfolio projects in SQLite database"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def init_database(self) -> None:
        """Initialize database with schema"""
        schema_path = SCRIPT_DIR / 'portfolio-schema.sql'

        if not schema_path.exists():
            print(f"❌ Schema file not found: {schema_path}")
            sys.exit(1)

        with open(schema_path) as f:
            self.conn.executescript(f.read())
        self.conn.commit()
        print(f"✓ Database created: {self.db_path}")

    def migrate_yaml(self) -> int:
        """Migrate existing YAML data to database"""
        yaml_file = SCRIPT_DIR / 'portfolio.yaml'

        if not yaml_file.exists():
            print("⚠️  No YAML file found, skipping migration")
            return 0

        # Hardcoded migration data (same as bash script)
        projects = [
            ('ayudem', 'Ayudem: Sistema de Gestión Interna', 'https://ayudem.pensanta.com',
             'Aplicación gran escala. Gestión de tareas, recursos y coordinación de logística.',
             '["NextJS","MariaDB","TypeScript"]', 2024, 'ayudem-800x500.webp', 1, 1, 'web-app'),

            ('draandreaesparza', 'Dra. Andrea Esparza - Psicóloga', 'https://draandreaesparza.com',
             'Sitio web profesional. Posicionamiento y contacto con potenciales clientes. Difusión de artículos.',
             '["HTML","CSS","JavaScript"]', 2024, 'draandreaesparza-800x500.webp', 1, 2, 'professional-site'),

            ('contenidopensanta', 'Contenido.Pensanta', '',
             'Sistema creado por Pensanta que alimenta automáticamente +10 sitios web. Cliente publica una vez en Instagram con el #hashtag correcto y aparece instantáneamente en el sitio correspondiente.',
             '["Instagram API","Python","Automation"]', 2024, 'contenido-pensanta-800x500.webp', 1, 3, 'automation'),

            ('lodevictor', 'Gastronomía: Lo de Victor', 'https://lodevictor.com',
             'Presencia digital, contacto con clientes, posicionamiento en motores de búsqueda',
             '["HTML","CSS","JavaScript"]', 2024, 'lodevictor-800x500.webp', 1, 4, 'professional-site'),

            ('fabricademochilas', 'Fábrica de Mochilas', 'https://fabricademochilas.com.ar',
             'E-commerce de fabricación y venta mayorista de mochilas escolares, corporativas y promocionales.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'fabricademochilas-com-ar-800x500.webp', 1, 5, 'e-commerce'),

            ('mochilasbaratas', 'Mochilas Baratas', 'https://mochilasbaratas.com.ar',
             'Tienda online especializada en mochilas para estudiantes y uso diario.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'mochilasbaratas-com-ar-800x500.webp', 1, 6, 'e-commerce'),

            ('aquilon', 'Aquilon', 'https://www.aquilon.com.ar',
             'Sitio de presencia digital corporativa.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'aquilon-com-ar-800x500.webp', 1, 7, 'professional-site'),

            ('mochilasconlogo', 'Mochilas con Logo', 'https://mochilasconlogo.com.ar',
             'Personalización y fabricación de mochilas corporativas con logo para empresas y eventos.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'mochilasconlogo-com-ar-800x500.webp', 1, 8, 'e-commerce'),

            ('josemauriciodipietro', 'José Mauricio Di Pietro', 'https://www.josemauriciodipietro.com.ar',
             'Sitio web profesional. Posicionamiento y contacto con potenciales clientes.',
             '["HTML","CSS","JavaScript"]', 2024, 'josemauriciodipietro-com-ar-800x500.webp', 1, 9, 'professional-site'),

            ('licmarianodominguez', 'Lic. Mariano Domínguez - Psicólogo', 'https://www.licmarianodominguez.com.ar',
             'Sitio web profesional. Psicología clínica e hipnosis clínica. Contacto con potenciales clientes.',
             '["HTML","CSS","JavaScript"]', 2024, 'licmarianodominguez-com-ar-800x500.webp', 1, 10, 'professional-site'),

            ('mochilaseconomicas', 'Mochilas Económicas', 'https://mochilaseconomicas.com.ar',
             'Venta mayorista de mochilas para revendedores y comercios.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'mochilaseconomicas-com-ar-800x500.webp', 1, 11, 'e-commerce'),

            ('tallerdemochilas', 'Taller de Mochilas', 'https://tallerdemochilas.com.ar',
             'Confección de mochilas. Servicio personalizado y a medida.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'tallerdemochilas-com-ar-800x500.webp', 1, 12, 'e-commerce'),

            ('cartucherasconlogo', 'Cartucheras con Logo', 'https://cartucherasconlogo.com.ar',
             'Fabricación de cartucheras personalizadas con logo para empresas, escuelas y eventos.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'cartucherasconlogo-com-ar-800x500.webp', 1, 13, 'e-commerce'),

            ('cartucheraspormayor', 'Cartucheras por Mayor', 'https://cartucheraspormayor.com.ar',
             'Venta mayorista de cartucheras escolares y organizadores para útiles.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'cartucheraspormayor-com-ar-800x500.webp', 1, 14, 'e-commerce'),

            ('fabricamosmochilas', 'Fabricamos Mochilas', 'https://fabricamosmochilas.com.ar',
             'Fabricación de mochilas. Diseños exclusivos y producción nacional.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'fabricamosmochilas-com-ar-800x500.webp', 1, 15, 'e-commerce'),

            ('officesite', 'Office Site', 'https://officesite.com.ar',
             'Distribuidora de artículos de oficina, escolares y útiles corporativos.',
             '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'officesite-com-ar-800x500.webp', 1, 16, 'e-commerce'),
        ]

        for project in projects:
            self.conn.execute("""
                INSERT OR IGNORE INTO projects
                (slug, name, url, description_es, tech_stack, year, screenshot_path,
                 include_in_portfolio, sort_order, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, project)

        self.conn.commit()
        print(f"✓ Migrated {len(projects)} projects from YAML")
        return len(projects)

    def scan_projects(self) -> int:
        """Scan filesystem for projects and add to database"""
        if not SCAN_ROOT.exists():
            print(f"❌ Scan root not found: {SCAN_ROOT}")
            return 0

        print(f"🔍 Scanning for projects in: {SCAN_ROOT}")
        print()

        added_count = 0

        # Find directories 1-2 levels deep
        for depth1 in SCAN_ROOT.iterdir():
            if not depth1.is_dir():
                continue

            # Process level 1
            for project_dir in [depth1] + list(depth1.iterdir()):
                if not project_dir.is_dir():
                    continue

                # Skip hidden, node_modules, etc
                basename = project_dir.name
                if basename.startswith('.') or basename in ['node_modules', 'scripts', 'docs']:
                    continue

                # Generate slug
                relative = project_dir.relative_to(SCAN_ROOT)
                slug = str(relative).replace('/', '-')

                # Check if exists
                existing = self.conn.execute(
                    "SELECT COUNT(*) FROM projects WHERE slug = ?", (slug,)
                ).fetchone()[0]

                if existing > 0:
                    print(f"⏭️  {slug} (already in database)")
                    continue

                # Detect project name
                name = basename
                package_json = project_dir / 'package.json'
                if package_json.exists():
                    try:
                        with open(package_json) as f:
                            pkg = json.load(f)
                            if 'name' in pkg:
                                name = pkg['name']
                    except:
                        pass

                # Detect URL
                url = ''
                vercel_config = project_dir / '.vercel/project.json'
                if vercel_config.exists():
                    try:
                        with open(vercel_config) as f:
                            config = json.load(f)
                            url = config.get('url', '')
                    except:
                        pass

                # Detect tech stack
                tech_stack = '[]'
                if package_json.exists():
                    try:
                        with open(package_json) as f:
                            pkg = json.load(f)
                            deps = {**pkg.get('dependencies', {}), **pkg.get('devDependencies', {})}
                            if 'next' in deps:
                                tech_stack = '["NextJS"]'
                            elif 'react' in deps:
                                tech_stack = '["React"]'
                            else:
                                tech_stack = '["JavaScript"]'
                    except:
                        pass
                elif (project_dir / 'public_html/index.html').exists():
                    tech_stack = '["HTML","CSS"]'

                # Insert with include_in_portfolio = 0 (not in portfolio by default)
                self.conn.execute("""
                    INSERT INTO projects (slug, name, url, tech_stack, year, include_in_portfolio)
                    VALUES (?, ?, ?, ?, ?, 0)
                """, (slug, name, url, tech_stack, datetime.now().year))

                print(f"✅ {slug} - {name}")
                added_count += 1

        self.conn.commit()
        print()
        print(f"📊 Scan complete! Added {added_count} new projects")
        return added_count

    def list_projects(self, include_all: bool = False) -> None:
        """List all projects"""
        if include_all:
            query = "SELECT slug, name, include_in_portfolio, sort_order FROM projects ORDER BY sort_order, id"
        else:
            query = "SELECT slug, name, sort_order FROM projects WHERE include_in_portfolio = 1 ORDER BY sort_order, id"

        rows = self.conn.execute(query).fetchall()

        print(f"\n📊 Projects ({len(rows)} total):\n")
        for row in rows:
            if include_all:
                status = "✓" if row['include_in_portfolio'] else " "
            else:
                status = "✓"  # All listed items are in portfolio when not showing all
            order = f"[{row['sort_order']}]" if row['sort_order'] < 999 else ""
            print(f"  {status} {row['slug']:<40} {order} {row['name']}")
        print()

    def enable_project(self, slug: str) -> None:
        """Enable project for portfolio"""
        # Get max sort_order
        max_order = self.conn.execute(
            "SELECT COALESCE(MAX(sort_order), 0) FROM projects WHERE include_in_portfolio = 1"
        ).fetchone()[0]

        self.conn.execute("""
            UPDATE projects
            SET include_in_portfolio = 1, sort_order = ?
            WHERE slug = ?
        """, (max_order + 1, slug))

        if self.conn.total_changes > 0:
            self.conn.commit()
            print(f"✓ Enabled {slug} for portfolio (order: {max_order + 1})")
        else:
            print(f"❌ Project not found: {slug}")

    def disable_project(self, slug: str) -> None:
        """Disable project from portfolio"""
        self.conn.execute("""
            UPDATE projects
            SET include_in_portfolio = 0
            WHERE slug = ?
        """, (slug,))

        if self.conn.total_changes > 0:
            self.conn.commit()
            print(f"✓ Disabled {slug} from portfolio")
        else:
            print(f"❌ Project not found: {slug}")

    def get_portfolio_projects(self) -> List[Dict]:
        """Get all projects included in portfolio"""
        rows = self.conn.execute("""
            SELECT * FROM projects
            WHERE include_in_portfolio = 1
            ORDER BY sort_order ASC, id ASC
        """).fetchall()

        projects = []
        for row in rows:
            project = dict(row)
            # Parse tech_stack JSON
            try:
                project['tech_stack'] = json.loads(project['tech_stack'])
            except:
                project['tech_stack'] = []
            projects.append(project)

        return projects


def generate_html(dry_run: bool = False) -> None:
    """Generate portfolio HTML files"""
    from jinja2 import Environment, FileSystemLoader

    template_dir = SCRIPT_DIR / 'templates'
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        print("   Run this script from the scripts/ directory")
        sys.exit(1)

    env = Environment(loader=FileSystemLoader(template_dir))

    with PortfolioManager() as pm:
        projects = pm.get_portfolio_projects()

        print(f"🏗️  Generating portfolio HTML with {len(projects)} projects...")

        # Generate Spanish portfolio
        template_es = env.get_template('portfolio_page_es.html')
        html_es = template_es.render(projects=projects)

        output_es = PUBLIC_HTML / 'es/portfolio/index.html'
        if dry_run:
            print(f"📄 Would write: {output_es}")
        else:
            # Backup original
            if output_es.exists():
                backup = output_es.with_suffix('.html.bak')
                output_es.rename(backup)

            output_es.write_text(html_es)
            print(f"   ✓ Written: {output_es}")

        # Generate English portfolio
        template_en = env.get_template('portfolio_page_en.html')
        html_en = template_en.render(projects=projects)

        output_en = PUBLIC_HTML / 'en/portfolio/index.html'
        if dry_run:
            print(f"📄 Would write: {output_en}")
        else:
            if output_en.exists():
                backup = output_en.with_suffix('.html.bak')
                output_en.rename(backup)

            output_en.write_text(html_en)
            print(f"   ✓ Written: {output_en}")

        print()
        print(f"✅ Generated portfolio pages with {len(projects)} projects!")


def main():
    parser = argparse.ArgumentParser(
        description='Portfolio Manager - Manage project portfolio database',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s init          # Initialize database
  %(prog)s scan          # Scan for projects
  %(prog)s list --all    # List all projects
  %(prog)s enable ayudem # Add project to portfolio
  %(prog)s generate      # Build HTML files
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # init command
    subparsers.add_parser('init', help='Initialize database and migrate YAML data')

    # scan command
    subparsers.add_parser('scan', help='Scan filesystem for projects')

    # list command
    list_parser = subparsers.add_parser('list', help='List projects')
    list_parser.add_argument('--all', action='store_true', help='Show all projects (not just portfolio)')

    # enable command
    enable_parser = subparsers.add_parser('enable', help='Enable project for portfolio')
    enable_parser.add_argument('slug', help='Project slug')

    # disable command
    disable_parser = subparsers.add_parser('disable', help='Disable project from portfolio')
    disable_parser.add_argument('slug', help='Project slug')

    # generate command
    generate_parser = subparsers.add_parser('generate', help='Generate HTML portfolio pages')
    generate_parser.add_argument('--dry-run', action='store_true', help='Show what would be generated')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Handle commands
    if args.command == 'init':
        if DB_PATH.exists():
            response = input(f"⚠️  Database exists: {DB_PATH}\nRecreate? (y/N): ")
            if response.lower() != 'y':
                print("Aborted.")
                sys.exit(0)
            DB_PATH.unlink()

        with PortfolioManager() as pm:
            pm.init_database()
            pm.migrate_yaml()

        # Show summary
        with PortfolioManager() as pm:
            total = pm.conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            portfolio = pm.conn.execute("SELECT COUNT(*) FROM projects WHERE include_in_portfolio = 1").fetchone()[0]
            print()
            print(f"📊 Database Summary:")
            print(f"   {total} total projects")
            print(f"   {portfolio} in portfolio")

    elif args.command == 'scan':
        with PortfolioManager() as pm:
            pm.scan_projects()
            total = pm.conn.execute("SELECT COUNT(*) FROM projects").fetchone()[0]
            print(f"   {total} total projects in database")

    elif args.command == 'list':
        with PortfolioManager() as pm:
            pm.list_projects(include_all=args.all)

    elif args.command == 'enable':
        with PortfolioManager() as pm:
            pm.enable_project(args.slug)

    elif args.command == 'disable':
        with PortfolioManager() as pm:
            pm.disable_project(args.slug)

    elif args.command == 'generate':
        generate_html(dry_run=args.dry_run)


if __name__ == '__main__':
    main()
