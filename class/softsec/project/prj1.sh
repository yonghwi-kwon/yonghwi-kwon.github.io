mkdir prj1
cd prj1
sudo apt install ncurses*
wget https://yonghwi-kwon.github.io/class/softsec/project/moon-buggy-master.zip
unzip moon-buggy-master.zip

sudo apt-get install autoconf automake texinfo
sudo apt-get install libncurses5-dev libncursesw5-dev

./autogen.sh
./configure
make