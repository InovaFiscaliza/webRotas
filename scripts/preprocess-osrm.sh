#!/bin/bash
#
# OSRM Preprocessing Script
# Converts region.osm.pbf to region.osrm using car_avoid.lua profile
# This "bakes in" the avoid zones logic into the routing data
#
# Usage: ./scripts/preprocess-osrm.sh
# Or:    OSRM_DATA=/path/to/data ./scripts/preprocess-osrm.sh
#

set -e

# Configuration
OSRM_DATA=${OSRM_DATA:-.}
PBF_FILE="$OSRM_DATA/region.osm.pbf"
PROFILE="$OSRM_DATA/profiles/car_avoid.lua"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"
echo -e "${YELLOW}  OSRM Preprocessing with car_avoid.lua Profile${NC}"
echo -e "${YELLOW}════════════════════════════════════════════════════════${NC}"

# Validation
echo ""
echo "Validating prerequisites..."

if [ ! -f "$PBF_FILE" ]; then
  echo -e "${RED}✗ Error: PBF file not found: $PBF_FILE${NC}"
  echo ""
  echo "To find your PBF file:"
  echo "  find $OSRM_DATA -name '*.osm.pbf' -o -name '*.pbf'"
  echo ""
  exit 1
fi

if [ ! -f "$PROFILE" ]; then
  echo -e "${RED}✗ Error: Profile not found: $PROFILE${NC}"
  echo "Expected profile at: $PROFILE"
  exit 1
fi

# Check if PBF is readable
if [ ! -r "$PBF_FILE" ]; then
  echo -e "${RED}✗ Error: Cannot read PBF file (permission denied): $PBF_FILE${NC}"
  exit 1
fi

# Check available space
echo ""
echo "Checking available disk space..."
AVAILABLE_GB=$(df "$OSRM_DATA" | tail -1 | awk '{printf "%.1f", $4/1024/1024}')
echo -e "Available space: ${GREEN}${AVAILABLE_GB} GB${NC}"

if (( $(echo "$AVAILABLE_GB < 10" | bc -l) )); then
  echo -e "${YELLOW}⚠ Warning: Less than 10 GB available. Preprocessing may fail.${NC}"
  read -p "Continue anyway? (y/n) " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
  fi
fi

echo -e "${GREEN}✓ Prerequisites validated${NC}"

# Display configuration
echo ""
echo "Configuration:"
echo "  PBF file: $PBF_FILE"
echo "  Profile: $PROFILE"
echo "  Data dir: $OSRM_DATA"

# Ask for confirmation
echo ""
read -p "Continue with preprocessing? This may take 5-30 minutes (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
  echo "Aborted."
  exit 1
fi

# Change to data directory
cd "$OSRM_DATA"

# Step 1: Extract
echo ""
echo -e "${YELLOW}Step 1/4: Extracting (osrm-extract)...${NC}"
echo "Command: osrm-extract -p '$PROFILE' '$PBF_FILE'"
if osrm-extract -p "$PROFILE" "$PBF_FILE"; then
  echo -e "${GREEN}✓ Extract complete${NC}"
else
  echo -e "${RED}✗ Extract failed${NC}"
  exit 1
fi

# Step 2: Contract
echo ""
echo -e "${YELLOW}Step 2/4: Contracting (osrm-contract)...${NC}"
echo "Command: osrm-contract region.osrm"
if osrm-contract region.osrm; then
  echo -e "${GREEN}✓ Contract complete${NC}"
else
  echo -e "${RED}✗ Contract failed${NC}"
  exit 1
fi

# Step 3: Partition
echo ""
echo -e "${YELLOW}Step 3/4: Partitioning (osrm-partition)...${NC}"
echo "Command: osrm-partition region.osrm"
if osrm-partition region.osrm; then
  echo -e "${GREEN}✓ Partition complete${NC}"
else
  echo -e "${RED}✗ Partition failed${NC}"
  exit 1
fi

# Step 4: Customize
echo ""
echo -e "${YELLOW}Step 4/4: Customizing (osrm-customize)...${NC}"
echo "Command: osrm-customize region.osrm"
if osrm-customize region.osrm; then
  echo -e "${GREEN}✓ Customize complete${NC}"
else
  echo -e "${RED}✗ Customize failed${NC}"
  exit 1
fi

# Success
echo ""
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Preprocessing Complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
echo ""
echo "Created files:"
ls -lh region.osrm* 2>/dev/null | awk '{print "  " $9 " (" $5 ")"}'
echo ""
echo "Next steps:"
echo "1. Restart OSRM container:"
echo "   docker-compose restart osrm"
echo ""
echo "2. Wait for OSRM to start:"
echo "   docker logs -f osrm | grep -i 'listening'"
echo ""
echo "3. Test zone avoidance:"
echo "   curl -X POST http://localhost:5002/process \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d @tests/request_grid\\ \\(São\\ Paulo-SP-Avoid\\).json"
echo ""
echo "4. Verify routes avoid zones:"
echo "   Compare with/without avoidZones parameter"
echo ""
