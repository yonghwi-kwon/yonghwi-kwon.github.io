mkdir prj1
cd prj1
wget https://yonghwi-kwon.github.io/class/softsec/project/moon-buggy.zip
unzip moon-buggy.zip

sudo apt-get install autoconf automake texinfo
sudo apt-get install libncurses5-dev libncursesw5-dev

./autogen.sh
./configure
make
./moon-buggy