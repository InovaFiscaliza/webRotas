#!/bin/bash

# OSRM Preprocessing Script with MD5 Validation and Conditional Downloading
# This script checks if the local Brazil OSM data matches the remote version,
# downloads if needed, and runs OSRM preprocessing.

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
REMOTE_MD5_URL="https://download.geofabrik.de/south-america/brazil-latest.osm.pbf.md5"
PBF_URL="https://download.geofabrik.de/south-america/brazil-latest.osm.pbf"
PBF_FILE="${OSRM_DATA}/brazil-latest.osm.pbf"
MD5_FILE="${OSRM_DATA}/brazil-latest.osm.pbf.md5"

if [ -z "${OSRM_DATA}" ]; then
    echo -e "${RED}✗ OSRM_DATA environment variable not set${NC}" >&2
    exit 1
fi

mkdir -p "${OSRM_DATA}"

echo -e "${YELLOW}============================================================${NC}"
echo -e "${YELLOW}  OSRM Data Preprocessing${NC}"
echo -e "${YELLOW}============================================================${NC}"

# Step 1: Fetch remote MD5
echo -e "\n${YELLOW}Step 1: Checking for updates${NC}"
echo -e "→ Fetching remote MD5 from ${REMOTE_MD5_URL}"

if ! REMOTE_MD5=$(curl -s "${REMOTE_MD5_URL}" | awk '{print $1}'); then
    echo -e "${RED}✗ Failed to fetch remote MD5${NC}" >&2
    exit 1
fi
echo -e "  Remote MD5: ${REMOTE_MD5}"

# Step 2: Check local file
echo -e "→ Checking local file"
if [ -f "${PBF_FILE}" ]; then
    LOCAL_MD5=$(md5sum "${PBF_FILE}" | awk '{print $1}')
    echo -e "  Local MD5:  ${LOCAL_MD5}"
else
    LOCAL_MD5=""
    echo -e "  Local file not found"
fi

# Step 3: Compare and decide
echo -e "\n${YELLOW}Step 2: Validation${NC}"
if [ "${LOCAL_MD5}" = "${REMOTE_MD5}" ] && [ -n "${LOCAL_MD5}" ]; then
    echo -e "${GREEN}✓ Files are up-to-date! No download needed.${NC}"
    echo -e "  Using existing: ${PBF_FILE}"
    echo -e "\n${GREEN}============================================================${NC}"
    echo -e "${GREEN}============================================================${NC}"
    exit 0
else
    echo -e "${YELLOW}✗ Files differ or local file missing. Downloading latest version...${NC}"
    
    echo -e "\n${YELLOW}Step 3: Downloading data${NC}"
    echo -e "→ Downloading from ${PBF_URL}"
    
    # Download with curl, showing progress
    if ! curl -L --progress-bar -o "${PBF_FILE}" "${PBF_URL}"; then
        echo -e "${RED}✗ Failed to download file${NC}" >&2
        exit 1
    fi
    
    # Verify downloaded file
    echo -e "\n${YELLOW}Step 4: Verifying download${NC}"
    echo -e "→ Calculating MD5 of downloaded file"
    NEW_MD5=$(md5sum "${PBF_FILE}" | awk '{print $1}')
    
    if [ "${NEW_MD5}" = "${REMOTE_MD5}" ]; then
        echo -e "${GREEN}✓ Downloaded file verified successfully${NC}"
        echo "${REMOTE_MD5} ${PBF_FILE##*/}" > "${MD5_FILE}"
    else
        echo -e "${RED}✗ MD5 mismatch after download!${NC}" >&2
        echo -e "  Expected: ${REMOTE_MD5}" >&2
        echo -e "  Got:      ${NEW_MD5}" >&2
        exit 1
    fi
fi

# Helper function to format duration
format_duration() {
    local seconds=$1
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))
    
    if [ $hours -gt 0 ]; then
        printf "%dh %dm %ds" $hours $minutes $secs
    elif [ $minutes -gt 0 ]; then
        printf "%dm %ds" $minutes $secs
    else
        printf "%ds" $secs
    fi
}

# Step 5: Run OSRM preprocessing
echo -e "\n${YELLOW}Step 5: OSRM Preprocessing${NC}"

echo -e "\nCommand 1/3:"
echo -e "→ Running: osrm-extract"
START_TIME=$(date +%s)
docker run --rm -t -v ${OSRM_DATA}:/data ghcr.io/project-osrm/osrm-backend:latest osrm-extract -p /data/profiles/car_avoid.lua /data/brazil-latest.osm.pbf
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo -e "${GREEN}✓ osrm-extract completed in $(format_duration $DURATION)${NC}"

echo -e "\nCommand 2/3:"
echo -e "→ Running: osrm-partition"
START_TIME=$(date +%s)
docker run --rm -t -v ${OSRM_DATA}:/data ghcr.io/project-osrm/osrm-backend:latest osrm-partition /data/brazil-latest.osrm
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo -e "${GREEN}✓ osrm-partition completed in $(format_duration $DURATION)${NC}"

echo -e "\nCommand 3/3:"
echo -e "→ Running: osrm-customize"
START_TIME=$(date +%s)
docker run --rm -t -v ${OSRM_DATA}:/data ghcr.io/project-osrm/osrm-backend:latest osrm-customize /data/brazil-latest.osrm
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo -e "${GREEN}✓ osrm-customize completed in $(format_duration $DURATION)${NC}"

echo -e "\n${GREEN}============================================================${NC}"
echo -e "${GREEN}✓ Preprocessing complete!${NC}"
echo -e "${GREEN}============================================================${NC}"

