#!/bin/bash

set -e

print_section() {
    echo ""
    echo "============================================================"
    echo "  $1"
    echo "============================================================"
    echo ""
}

print_step() {
    echo "→ $1"
}

OSRM_DATA="/data"

REMOTE_MD5_URL="https://download.geofabrik.de/south-america/brazil-latest.osm.pbf.md5"
PBF_URL="https://download.geofabrik.de/south-america/brazil-latest.osm.pbf"
REGION_FILE="$OSRM_DATA/region.osm.pbf"
MD5_FILE="$OSRM_DATA/brazil-latest.osm.pbf.md5"

# Step 1: Fetch remote MD5
print_section "Step 1: Checking for updates"
print_step "Fetching remote MD5 from $REMOTE_MD5_URL"
REMOTE_MD5=$(curl -sL "$REMOTE_MD5_URL" | awk '{print $1}')
if [ -z "$REMOTE_MD5" ] || [ ${#REMOTE_MD5} -ne 32 ]; then
    echo "✗ Failed to fetch valid remote MD5 (got: $REMOTE_MD5). Aborting."
    exit 1
fi
echo "  Remote MD5: $REMOTE_MD5"

# Step 2: Check local file
print_step "Checking local file"
if [ -f "$REGION_FILE" ]; then
    LOCAL_MD5=$(md5sum "$REGION_FILE" | awk '{print $1}')
    echo "  Local MD5:  $LOCAL_MD5"
else
    LOCAL_MD5=""
    echo "  Local file not found"
fi

# Step 3: Compare and decide
print_section "Step 2: Validation"
if [ -n "$LOCAL_MD5" ] && [ "$LOCAL_MD5" = "$REMOTE_MD5" ]; then
    echo "✓ Files are up-to-date! Preprocessing already complete."
    echo "  Using existing: $REGION_FILE"
    exit 0
else
    echo "✗ Files differ or local file missing. Downloading latest version..."
fi

# Step 3: Download data
print_section "Step 3: Downloading data"
print_step "Downloading from $PBF_URL"
# Remove any existing file to ensure clean download
rm -f "$REGION_FILE"
# Download with explicit redirect following and retry on failure
if ! curl -f --location --max-redirs 5 --retry 3 --retry-delay 5 -o "$REGION_FILE" "$PBF_URL"; then
    echo "✗ Download failed after retries" >&2
    exit 1
fi
echo ""

# Step 4: Verify download
print_section "Step 4: Verifying download"
print_step "Calculating MD5 of downloaded file"
NEW_MD5=$(md5sum "$REGION_FILE" | awk '{print $1}')

if [ "$NEW_MD5" != "$REMOTE_MD5" ]; then
    echo "✗ MD5 mismatch after download!" >&2
    echo "  Expected: $REMOTE_MD5" >&2
    echo "  Got:      $NEW_MD5" >&2
    exit 1
fi
echo "✓ Downloaded file verified successfully"
echo "$REMOTE_MD5 region.osm.pbf" > "$MD5_FILE"

# Step 5: OSRM Preprocessing
print_section "Step 5: OSRM Preprocessing"

cd "$OSRM_DATA"

echo ""
echo "Command 1/3:"
print_step "Running: osrm-extract -p /data/profiles/car.lua /data/region.osm.pbf"
osrm-extract -p /data/profiles/car.lua /data/region.osm.pbf

echo ""
echo "Command 2/3:"
print_step "Running: osrm-partition /data/region.osrm"
osrm-partition /data/region.osrm

echo ""
echo "Command 3/3:"
print_step "Running: osrm-customize /data/region.osrm"
osrm-customize /data/region.osrm

# Step 6: Rename files
print_section "Step 6: Finalizing preprocessing"
for file in region.osrm*; do
    if [ -f "$file" ]; then
        new_name="${file//region.osm/brazil-latest.osm}"
        print_step "Renaming $file to $new_name"
        mv "$file" "$new_name"
        echo "  ✓ $new_name"
    fi
done

print_section "✓ Preprocessing complete!"
exit 0
