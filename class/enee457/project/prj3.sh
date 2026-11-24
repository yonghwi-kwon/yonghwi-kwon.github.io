mkdir prj3
cd prj3
mkdir build
wget https://yonghwi-kwon.github.io/class/enee457/project/page_table.py
wget https://yonghwi-kwon.github.io/class/enee457/project/processor_lib.py
wget https://yonghwi-kwon.github.io/class/enee457/project/processor.py
wget https://yonghwi-kwon.github.io/class/enee457/project/build/victim_symbols.json
wget https://yonghwi-kwon.github.io/class/enee457/project/build/victim.elf
wget https://yonghwi-kwon.github.io/class/enee457/project/build/victim.s

mv victim_symbols.json build/victim_symbols.json
mv victim.elf build/victim.elf
mv victim.s build/victim.s

chmod +x processor.py
sudo apt-get install python3-unicorn
sudo apt-get install python3-capstone
