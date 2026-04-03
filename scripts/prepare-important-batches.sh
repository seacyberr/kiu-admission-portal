#!/bin/bash
# Script to organize important files into folders of 20 files each
# Creates important-batch-1, important-batch-2, etc.

echo "🚀 Preparing important files in batches of 20..."

# Clean up any previous runs
rm -rf important-batch-*

# Read files from important-files.txt (skip section headers and empty lines)
grep "^\./" important-files.txt > /tmp/files-list.txt

# Create batches of 20 files
BATCH_SIZE=20
batch_num=1
file_count=0

while IFS= read -r file; do
    # Create new batch folder if needed
    if [ $file_count -eq 0 ]; then
        batch_dir="important-batch-$batch_num"
        mkdir -p "$batch_dir"
        echo "📁 Creating $batch_dir/"
    fi
    
    # Copy file to batch (preserving directory structure)
    if [ -f "$file" ]; then
        # Get directory path
        dir_path=$(dirname "$file")
        # Create subdirectory in batch if needed
        mkdir -p "$batch_dir/$dir_path"
        # Copy file
        cp "$file" "$batch_dir/$file" 2>/dev/null
    fi
    
    file_count=$((file_count + 1))
    
    # Start new batch when reaching BATCH_SIZE
    if [ $file_count -eq $BATCH_SIZE ]; then
        echo "   ✅ Added $file_count files to $batch_dir"
        batch_num=$((batch_num + 1))
        file_count=0
    fi
done < /tmp/files-list.txt

# Handle remaining files in last batch
if [ $file_count -gt 0 ]; then
    echo "   ✅ Added $file_count files to $batch_dir"
fi

# Clean up temp file
rm -f /tmp/files-list.txt

echo ""
echo "✅ Successfully organized important files into $((batch_num)) batches"
echo ""
echo "📋 Batches created:"
ls -1d important-batch-* 2>/dev/null
echo ""
echo "📊 Files per batch:"
for dir in important-batch-*; do
    if [ -d "$dir" ]; then
        count=$(find "$dir" -type f | wc -l)
        echo "   $dir: $count files"
    fi
done
echo ""
echo "💡 Tip: You can now upload each batch folder to Claude"