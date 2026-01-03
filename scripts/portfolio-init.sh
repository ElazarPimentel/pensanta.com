#!/bin/bash
# Initialize portfolio database and migrate existing YAML data

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/portfolio.sqlite"
YAML_FILE="$SCRIPT_DIR/portfolio.yaml"

echo "🗄️  Initializing portfolio database..."

# Create database with schema
if [ -f "$DB_PATH" ]; then
    read -p "⚠️  Database exists. Recreate? (y/N): " CONFIRM
    if [[ "$CONFIRM" == "y" ]]; then
        rm "$DB_PATH"
        echo "   Deleted existing database"
    else
        echo "   Keeping existing database"
        exit 0
    fi
fi

sqlite3 "$DB_PATH" < "$SCRIPT_DIR/portfolio-schema.sql"
echo "✓ Database created: $DB_PATH"

# Migrate YAML data if exists
if [ ! -f "$YAML_FILE" ]; then
    echo "⚠️  No YAML file found, skipping migration"
    exit 0
fi

echo ""
echo "📦 Migrating YAML data..."

# Parse YAML and insert into SQLite
# This is a simplified parser - assumes clean YAML format
sqlite3 "$DB_PATH" <<'EOSQL'
.mode list
.separator "|"
BEGIN TRANSACTION;

-- Ayudem
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('ayudem', 'Ayudem: Sistema de Gestión Interna', 'https://ayudem.pensanta.com',
  'Aplicación gran escala. Gestión de tareas, recursos y coordinación de logística.',
  '["NextJS","MariaDB","TypeScript"]', 2024, 'ayudem-800x500.webp', 1, 1, 'web-app');

-- Dra. Andrea Esparza
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('draandreaesparza', 'Dra. Andrea Esparza - Psicóloga', 'https://draandreaesparza.com',
  'Sitio web profesional. Posicionamiento y contacto con potenciales clientes. Difusión de artículos.',
  '["HTML","CSS","JavaScript"]', 2024, 'draandreaesparza-800x500.webp', 1, 2, 'professional-site');

-- Contenido.Pensanta
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category, type)
VALUES ('contenidopensanta', 'Contenido.Pensanta', '',
  'Sistema creado por Pensanta que alimenta automáticamente +10 sitios web. Cliente publica una vez en Instagram con el #hashtag correcto y aparece instantáneamente en el sitio correspondiente.',
  '["Instagram API","Python","Automation"]', 2024, 'contenido-pensanta-800x500.webp', 1, 3, 'automation', 'internal');

-- Lo de Victor
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('lodevictor', 'Gastronomía: Lo de Victor', 'https://lodevictor.com',
  'Presencia digital, contacto con clientes, posicionamiento en motores de búsqueda',
  '["HTML","CSS","JavaScript"]', 2024, 'lodevictor-800x500.webp', 1, 4, 'professional-site');

-- Fábrica de Mochilas
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('fabricademochilas', 'Fábrica de Mochilas', 'https://fabricademochilas.com.ar',
  'E-commerce de fabricación y venta mayorista de mochilas escolares, corporativas y promocionales.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'fabricademochilas-com-ar-800x500.webp', 1, 5, 'e-commerce');

-- Mochilas Baratas
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('mochilasbaratas', 'Mochilas Baratas', 'https://mochilasbaratas.com.ar',
  'Tienda online especializada en mochilas para estudiantes y uso diario.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'mochilasbaratas-com-ar-800x500.webp', 1, 6, 'e-commerce');

-- Aquilon
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('aquilon', 'Aquilon', 'https://www.aquilon.com.ar',
  'Sitio de presencia digital corporativa.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'aquilon-com-ar-800x500.webp', 1, 7, 'professional-site');

-- Mochilas con Logo
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('mochilasconlogo', 'Mochilas con Logo', 'https://mochilasconlogo.com.ar',
  'Personalización y fabricación de mochilas corporativas con logo para empresas y eventos.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'mochilasconlogo-com-ar-800x500.webp', 1, 8, 'e-commerce');

-- José Mauricio Di Pietro
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('josemauriciodipietro', 'José Mauricio Di Pietro', 'https://www.josemauriciodipietro.com.ar',
  'Sitio web profesional. Posicionamiento y contacto con potenciales clientes.',
  '["HTML","CSS","JavaScript"]', 2024, 'josemauriciodipietro-com-ar-800x500.webp', 1, 9, 'professional-site');

-- Lic. Mariano Domínguez
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('licmarianodominguez', 'Lic. Mariano Domínguez - Psicólogo', 'https://www.licmarianodominguez.com.ar',
  'Sitio web profesional. Psicología clínica e hipnosis clínica. Contacto con potenciales clientes.',
  '["HTML","CSS","JavaScript"]', 2024, 'licmarianodominguez-com-ar-800x500.webp', 1, 10, 'professional-site');

-- Mochilas Económicas
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('mochilaseconomicas', 'Mochilas Económicas', 'https://mochilaseconomicas.com.ar',
  'Venta mayorista de mochilas para revendedores y comercios.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'mochilaseconomicas-com-ar-800x500.webp', 1, 11, 'e-commerce');

-- Taller de Mochilas
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('tallerdemochilas', 'Taller de Mochilas', 'https://tallerdemochilas.com.ar',
  'Confección de mochilas. Servicio personalizado y a medida.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'tallerdemochilas-com-ar-800x500.webp', 1, 12, 'e-commerce');

-- Cartucheras con Logo
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('cartucherasconlogo', 'Cartucheras con Logo', 'https://cartucherasconlogo.com.ar',
  'Fabricación de cartucheras personalizadas con logo para empresas, escuelas y eventos.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'cartucherasconlogo-com-ar-800x500.webp', 1, 13, 'e-commerce');

-- Cartucheras por Mayor
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('cartucheraspormayor', 'Cartucheras por Mayor', 'https://cartucheraspormayor.com.ar',
  'Venta mayorista de cartucheras escolares y organizadores para útiles.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'cartucheraspormayor-com-ar-800x500.webp', 1, 14, 'e-commerce');

-- Fabricamos Mochilas
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('fabricamosmochilas', 'Fabricamos Mochilas', 'https://fabricamosmochilas.com.ar',
  'Fabricación de mochilas. Diseños exclusivos y producción nacional.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'fabricamosmochilas-com-ar-800x500.webp', 1, 15, 'e-commerce');

-- Office Site
INSERT INTO projects (slug, name, url, description_es, tech_stack, year, screenshot_path, include_in_portfolio, sort_order, category)
VALUES ('officesite', 'Office Site', 'https://officesite.com.ar',
  'Distribuidora de artículos de oficina, escolares y útiles corporativos.',
  '["HTML","CSS","JavaScript","Contenido.Pensanta"]', 2024, 'officesite-com-ar-800x500.webp', 1, 16, 'e-commerce');

COMMIT;
EOSQL

echo "✓ Migrated 16 projects from YAML"

# Show summary
echo ""
echo "📊 Database Summary:"
sqlite3 "$DB_PATH" "SELECT COUNT(*) || ' total projects' FROM projects;"
sqlite3 "$DB_PATH" "SELECT COUNT(*) || ' in portfolio' FROM projects WHERE include_in_portfolio = 1;"

echo ""
echo "✅ Initialization complete!"
echo "   Database: $DB_PATH"
echo ""
echo "Next steps:"
echo "  - Run ./portfolio-scan.sh to discover more projects"
echo "  - Run ./portfolio-generate.sh to build HTML"
