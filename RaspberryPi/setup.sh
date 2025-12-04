#!/bin/bash

# =====================================================
# SCRIPT DE INSTALACIÓN AUTOMÁTICA
# Sistema de Gestión de Restaurante con MQTT
# =====================================================

set -e  # Detener si hay errores

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funciones de utilidad
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Banner
clear
echo ""
echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════════════════════╗
║                                                       ║
║   🍽️  SISTEMA DE GESTIÓN DE RESTAURANTE              ║
║                                                       ║
║   Instalador Automático                              ║
║   v1.0.0                                             ║
║                                                       ║
╚═══════════════════════════════════════════════════════╝
EOF
echo -e "${NC}"
echo ""

# ==================== VERIFICAR SISTEMA ====================

print_header "1. VERIFICANDO SISTEMA"

# Verificar sistema operativo
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    print_success "Sistema: Linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    print_success "Sistema: macOS"
else
    print_error "Sistema no soportado: $OSTYPE"
    exit 1
fi

# Verificar Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
    print_success "Python $PYTHON_VERSION encontrado"
else
    print_error "Python 3 no encontrado"
    echo "Instala Python 3.8+ antes de continuar"
    exit 1
fi

# Verificar pip
if command -v pip3 &> /dev/null; then
    print_success "pip3 encontrado"
else
    print_error "pip3 no encontrado"
    echo "Instalando pip3..."
    sudo apt-get install -y python3-pip || brew install python3
fi

echo ""

# ==================== CREAR ENTORNO VIRTUAL ====================

print_header "2. CONFIGURANDO ENTORNO VIRTUAL"

if [ -d "venv" ]; then
    print_warning "Entorno virtual ya existe"
    read -p "¿Deseas recrearlo? (s/n): " recreate
    if [ "$recreate" = "s" ]; then
        rm -rf venv
        print_info "Entorno eliminado"
    fi
fi

if [ ! -d "venv" ]; then
    print_info "Creando entorno virtual..."
    python3 -m venv venv
    print_success "Entorno virtual creado"
fi

# Activar entorno
source venv/bin/activate
print_success "Entorno virtual activado"

echo ""

# ==================== INSTALAR DEPENDENCIAS ====================

print_header "3. INSTALANDO DEPENDENCIAS"

if [ -f "requirements.txt" ]; then
    print_info "Instalando paquetes de Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_success "Dependencias instaladas"
else
    print_error "requirements.txt no encontrado"
    exit 1
fi

echo ""

# ==================== CONFIGURAR VARIABLES DE ENTORNO ====================

print_header "4. CONFIGURACIÓN DE VARIABLES"

if [ ! -f ".env" ]; then
    if [ -f "config.env" ]; then
        cp config.env .env
        print_success "Archivo .env creado desde config.env"
    else
        print_error "config.env no encontrado"
        exit 1
    fi
else
    print_warning "Archivo .env ya existe"
fi

echo ""
print_info "Ahora necesitas configurar tus credenciales"
echo ""

# Pedir configuración de base de datos
read -p "Host de PostgreSQL: " db_host
read -p "Puerto (default 5432): " db_port
db_port=${db_port:-5432}
read -p "Nombre de la base de datos: " db_name
read -p "Usuario de PostgreSQL: " db_user
read -s -p "Contraseña de PostgreSQL: " db_password
echo ""

# Actualizar .env con sed
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' "s|DB_HOST=.*|DB_HOST=$db_host|g" .env
    sed -i '' "s|DB_PORT=.*|DB_PORT=$db_port|g" .env
    sed -i '' "s|DB_NAME=.*|DB_NAME=$db_name|g" .env
    sed -i '' "s|DB_USER=.*|DB_USER=$db_user|g" .env
    sed -i '' "s|DB_PASSWORD=.*|DB_PASSWORD=$db_password|g" .env
else
    # Linux
    sed -i "s|DB_HOST=.*|DB_HOST=$db_host|g" .env
    sed -i "s|DB_PORT=.*|DB_PORT=$db_port|g" .env
    sed -i "s|DB_NAME=.*|DB_NAME=$db_name|g" .env
    sed -i "s|DB_USER=.*|DB_USER=$db_user|g" .env
    sed -i "s|DB_PASSWORD=.*|DB_PASSWORD=$db_password|g" .env
fi

print_success "Configuración de BD guardada en .env"

echo ""

# Configuración MQTT
read -p "Broker MQTT (default: broker.emqx.io): " mqtt_broker
mqtt_broker=${mqtt_broker:-broker.emqx.io}

read -p "Puerto MQTT (default: 1883): " mqtt_port
mqtt_port=${mqtt_port:-1883}

if [[ "$OSTYPE" == "darwin"* ]]; then
    sed -i '' "s|MQTT_BROKER=.*|MQTT_BROKER=$mqtt_broker|g" .env
    sed -i '' "s|MQTT_PORT=.*|MQTT_PORT=$mqtt_port|g" .env
else
    sed -i "s|MQTT_BROKER=.*|MQTT_BROKER=$mqtt_broker|g" .env
    sed -i "s|MQTT_PORT=.*|MQTT_PORT=$mqtt_port|g" .env
fi

print_success "Configuración MQTT guardada"

echo ""

# ==================== VERIFICAR CONEXIÓN BD ====================

print_header "5. VERIFICANDO CONEXIÓN A BASE DE DATOS"

print_info "Probando conexión a PostgreSQL..."

python3 << EOF
import psycopg2
try:
    conn = psycopg2.connect(
        host='$db_host',
        database='$db_name',
        user='$db_user',
        password='$db_password',
        port=$db_port
    )
    print("✓ Conexión exitosa a PostgreSQL")
    conn.close()
except Exception as e:
    print(f"✗ Error de conexión: {e}")
    exit(1)
EOF

if [ $? -eq 0 ]; then
    print_success "Conexión a PostgreSQL verificada"
else
    print_error "No se pudo conectar a PostgreSQL"
    print_info "Verifica tus credenciales en el archivo .env"
    exit 1
fi

echo ""

# ==================== INSTALAR ESQUEMA DE BD ====================

print_header "6. INSTALANDO ESQUEMA DE BASE DE DATOS"

read -p "¿Deseas instalar el esquema de base de datos? (s/n): " install_schema

if [ "$install_schema" = "s" ]; then
    if [ -f "database_schema.sql" ]; then
        print_info "Instalando esquema..."
        PGPASSWORD=$db_password psql -h $db_host -U $db_user -d $db_name -p $db_port -f database_schema.sql
        print_success "Esquema instalado correctamente"
    else
        print_error "database_schema.sql no encontrado"
    fi
else
    print_warning "Esquema no instalado. Hazlo manualmente más tarde."
fi

echo ""

# ==================== CREAR SERVICIO SYSTEMD (opcional) ====================

print_header "7. CONFIGURAR SERVICIO (Opcional)"

read -p "¿Deseas crear un servicio systemd para auto-inicio? (s/n): " create_service

if [ "$create_service" = "s" ] && [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CURRENT_DIR=$(pwd)
    SERVICE_FILE="/etc/systemd/system/restaurant-mqtt.service"
    
    print_info "Creando servicio systemd..."
    
    sudo tee $SERVICE_FILE > /dev/null <<EOF
[Unit]
Description=Restaurant MQTT Broker Listener
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$CURRENT_DIR
Environment="PATH=$CURRENT_DIR/venv/bin"
ExecStart=$CURRENT_DIR/venv/bin/python $CURRENT_DIR/restaurant_mqtt_broker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    sudo systemctl daemon-reload
    sudo systemctl enable restaurant-mqtt.service
    
    print_success "Servicio systemd creado"
    print_info "Comandos útiles:"
    echo "  • Iniciar:   sudo systemctl start restaurant-mqtt"
    echo "  • Detener:   sudo systemctl stop restaurant-mqtt"
    echo "  • Estado:    sudo systemctl status restaurant-mqtt"
    echo "  • Logs:      sudo journalctl -u restaurant-mqtt -f"
else
    print_info "Servicio no creado. Puedes ejecutar manualmente con:"
    echo "  python restaurant_mqtt_broker.py"
fi

echo ""

# ==================== CREAR SCRIPTS DE INICIO ====================

print_header "8. CREANDO SCRIPTS DE INICIO"

# Script de inicio simple
cat > start.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python restaurant_mqtt_broker.py
EOF

chmod +x start.sh
print_success "Script start.sh creado"

# Script de simulador
cat > simulate.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
python vision_simulator.py
EOF

chmod +x simulate.sh
print_success "Script simulate.sh creado"

echo ""

# ==================== RESUMEN FINAL ====================

print_header "✅ INSTALACIÓN COMPLETADA"

echo ""
echo -e "${GREEN}El sistema está listo para usar!${NC}"
echo ""
echo -e "${BLUE}Archivos creados:${NC}"
echo "  • venv/               - Entorno virtual de Python"
echo "  • .env                - Configuración (credenciales)"
echo "  • start.sh            - Iniciar broker listener"
echo "  • simulate.sh         - Iniciar simulador de visión"
echo ""
echo -e "${BLUE}Próximos pasos:${NC}"
echo ""
echo "1. Para iniciar el broker listener:"
echo -e "   ${YELLOW}./start.sh${NC}"
echo ""
echo "2. Para probar con el simulador (en otra terminal):"
echo -e "   ${YELLOW}./simulate.sh${NC}"
echo ""
echo "3. Para ver los logs:"
echo -e "   ${YELLOW}tail -f restaurant_broker.log${NC}"
echo ""
echo "4. Configura tu frontend para conectarse a:"
echo "   • MQTT Broker: $mqtt_broker:$mqtt_port"
echo "   • PostgreSQL: $db_host:$db_port/$db_name"
echo ""
echo -e "${GREEN}¡Feliz desarrollo! 🚀${NC}"
echo ""

# Preguntar si desea iniciar inmediatamente
read -p "¿Deseas iniciar el broker ahora? (s/n): " start_now

if [ "$start_now" = "s" ]; then
    echo ""
    print_info "Iniciando broker..."
    ./start.sh
fi
