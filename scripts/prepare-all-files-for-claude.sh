#!/bin/bash
# Script to organize ALL project files into folders of ~20 files each
# Creates upload-batch-1, upload-batch-2, etc.

echo "🚀 Preparing ALL project files for Claude upload..."

# Clean up any previous runs
rm -rf upload-batch-*

# Create arrays to hold files
declare -a all_files

# Function to add files to array
add_files() {
    local dir="$1"
    local pattern="$2"
    while IFS= read -r -d '' file; do
        all_files+=("$file")
    done < <(find "$dir" -name "$pattern" -type f -print0 2>/dev/null)
}

# Backend Python files
echo "📁 Collecting backend files..."
add_files "apps/flask-api" "*.py"

# Backend data files
add_files "apps/flask-api/data" "*.json"

# Backend config files
add_files "apps/flask-api" "*.txt"
add_files "apps/flask-api" "*.ini"

# Frontend TypeScript/TSX files
echo "📁 Collecting frontend files..."
add_files "apps/kiu-portal/src" "*.tsx"
add_files "apps/kiu-portal/src" "*.ts"

# Frontend config files
add_files "apps/kiu-portal" "*.json"

# Shared library files
echo "📁 Collecting shared library files..."
add_files "lib/api-client-react/src" "*.ts"

# Scripts
echo "📁 Collecting scripts..."
add_files "scripts/src" "*.ts"
add_files "scripts" "*.py"
add_files "scripts" "*.sh"
add_files "scripts" "*.json"

# Root configuration files
echo "📁 Collecting root configuration files..."
for file in package.json pnpm-workspace.yaml pyproject.toml tsconfig.json tsconfig.base.json .env.example .gitignore .npmrc; do
    if [ -f "$file" ]; then
        all_files+=("$file")
    fi
done

# Documentation files
echo "📁 Collecting documentation..."
for file in README.md DEPLOYMENT.md CHANGES.md IMPLEMENTATION_PLAN.md IMPLEMENTATION_PHASE2.md IMPLEMENTATION_PHASE3.md; do
    if [ -f "$file" ]; then
        all_files+=("$file")
    fi
done

# E2E test files
add_files "apps/kiu-portal/e2e" "*.ts"

# Test files
add_files "apps/flask-api/tests" "*.py"

echo ""
echo "📊 Total files collected: ${#all_files[@]}"
echo ""

# Create batches of 20 files
BATCH_SIZE=20
batch_num=1
file_count=0

for file in "${all_files[@]}"; do
    # Create new batch folder if needed
    if [ $file_count -eq 0 ]; then
        batch_dir="upload-batch-$batch_num"
        mkdir -p "$batch_dir"
        echo "📁 Creating $batch_dir/"
    fi
    
    # Copy file to batch
    cp "$file" "$batch_dir/" 2>/dev/null
    
    file_count=$((file_count + 1))
    
    # Start new batch when reaching BATCH_SIZE
    if [ $file_count -eq $BATCH_SIZE ]; then
        echo "   ✅ Added $file_count files to $batch_dir"
        batch_num=$((batch_num + 1))
        file_count=0
    fi
done

# Handle remaining files in last batch
if [ $file_count -gt 0 ]; then
    echo "   ✅ Added $file_count files to $batch_dir"
fi

echo ""
echo "✅ Successfully organized ${#all_files[@]} files into $((batch_num)) batches"
echo ""
echo "📋 Batches created:"
ls -1d upload-batch-* 2>/dev/null
echo ""
echo "💡 Tip: You can now upload each batch folder separately to Claude"
echo "   Each batch contains approximately $BATCH_SIZE files"