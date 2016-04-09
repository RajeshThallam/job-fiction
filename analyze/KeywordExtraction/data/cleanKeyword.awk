for file in *.key; do awk '{print $2 >FILENAME }' "$file";done
