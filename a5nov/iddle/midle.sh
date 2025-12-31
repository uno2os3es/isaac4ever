#!/data/data/com.termux/files/usr/bin/bash
# save as ~/bin/pyide
echo "Python IDE - Choose an option:"
echo "1. Edit Python file with micro"
echo "2. Run Python file"
echo "3. Python REPL"
read -p "Choice: " opt

case $opt in
  1)
    read -p "Filename: " fname
    micro "$fname"
    ;;
  2)
    read -p "File to run: " fname
    python "$fname"
    ;;
  3)
    python
    ;;
  *)
    echo "Invalid option"
    ;;
esac