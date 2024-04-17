#!/bin/bash

# Path to PostgreSQL and uWSGI configuration files
PG_CONF="/etc/postgresql/14/main/postgresql.conf"
UWSGI_INI="/etc/uwsgi/sites/drumpler.ini"

# Fetch the number of CPU cores
CPU_CORES=$(grep -c ^processor /proc/cpuinfo)
# Fetch total memory in MB
TOTAL_MEM_MB=$(grep MemTotal /proc/meminfo | awk '{print int($2/1024)}')

# Calculate PostgreSQL settings
# Setting shared_buffers to 25% of total memory, capped at 8192 MB (8GB)
SHARED_BUFFERS=$((TOTAL_MEM_MB / 4 > 8192 ? 8192 : TOTAL_MEM_MB / 4))
# Setting effective_cache_size to 75% of total memory
EFFECTIVE_CACHE_SIZE=$((3 * TOTAL_MEM_MB / 4))
# Setting maintenance_work_mem higher for more CPU cores, capped at 2048 MB
MAINTENANCE_WORK_MEM=$((CPU_CORES * 64 > 2048 ? 2048 : CPU_CORES * 64))
# Setting max_worker_processes to number of CPU cores
MAX_WORKER_PROCESSES=$CPU_CORES

# Update PostgreSQL configuration
sed -i "s/^shared_buffers = .*/shared_buffers = ${SHARED_BUFFERS}MB/" $PG_CONF
sed -i "s/^effective_cache_size = .*/effective_cache_size = ${EFFECTIVE_CACHE_SIZE}MB/" $PG_CONF
sed -i "s/^maintenance_work_mem = .*/maintenance_work_mem = ${MAINTENANCE_WORK_MEM}MB/" $PG_CONF
sed -i "s/^max_worker_processes = .*/max_worker_processes = ${MAX_WORKER_PROCESSES}/" $PG_CONF

# Calculate uWSGI settings (assuming each process can handle 2*CPU_CORES threads)
UWSGI_PROCESSES=$CPU_CORES
UWSGI_THREADS=$((2 * CPU_CORES))

# Update uWSGI configuration
sed -i "s/^processes = .*/processes = ${UWSGI_PROCESSES}/" $UWSGI_INI
sed -i "s/^threads = .*/threads = ${UWSGI_THREADS}/" $UWSGI_INI

# Restart PostgreSQL and uWSGI to apply changes
systemctl restart postgresql@14-main
systemctl restart uwsgi

echo "Configuration updated and services restarted successfully."