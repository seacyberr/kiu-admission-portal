#!/bin/bash
# Script to list ALL project files grouped in batches of 20
# Creates upload-batches.txt with file groups

echo "📋 Listing ALL project files in batches of 20..."

# Output file
OUTPUT="upload-batches.txt"
> "$OUTPUT"

# Collect all source code files (excluding node_modules, venv, dist, .git, cache, uploads, instance, images, db)
find . -type f \
    ! -path "*/node_modules/*" \
    ! -path "*/venv/*" \
    ! -path "*/.venv/*" \
    ! -path "*/dist/*" \
    ! -path "*/.git/*" \
    ! -path "*/__pycache__/*" \
    ! -path "*/.pytest_cache/*" \
    ! -path "*/uploads/*" \
    ! -path "*/instance/*" \
    ! -path "*/upload-batch-*" \
    ! -path "*/claude-upload/*" \
    ! -name "*.pyc" \
    ! -name "*.pyo" \
    ! -name "*.db" \
    ! -name "*.jpg" \
    ! -name "*.jpeg" \
    ! -name "*.png" \
    ! -name "*.gif" \
    ! -name "*.ico" \
    ! -name "*.svg" \
    | sort \
    | awk 'BEGIN { batch=1; count=0 }
    {
        if (count == 0) {
            print "" >> "upload-batches.txt"
            print "=== BATCH " batch " ===" >> "upload-batches.txt"
        }
        print $0 >> "upload-batches.txt"
        count++
        if (count == 20) {
            batch++
            count=0
        }
    }
    END {
        if (count > 0 && count < 20) {
            print "" >> "upload-batches.txt"
            print "(Last batch has " count " files)" >> "upload-batches.txt"
        }
    }'

echo ""
echo "✅ Created $OUTPUT with file batches"
echo ""
echo "📊 Summary:"
grep -c "=== BATCH" "$OUTPUT" | xargs -I {} echo "   Total batches: {}"
wc -l < "$OUTPUT" | xargs -I {} echo "   Total lines: {}"
echo ""
echo "💡 View the file: cat $OUTPUT"