
wget https://yonghwi-kwon.github.io/class/softsec/pin/pin-3.28-98749-g6643ecee5-gcc-linux.tar.gz

tar -xvf pin-3.28-98749-g6643ecee5-gcc-linux.tar.gz

mv pin-3.28-98749-g6643ecee5-gcc-linux pin

rm pin-3.28-98749-g6643ecee5-gcc-linux.tar.gz

cd pin

wget https://yonghwi-kwon.github.io/class/softsec/script/pin.env
echo "cd $PWD" >> ~/.bashrc
echo "source $PWD/pin.env" >> ~/.bashrc
echo "cd" >> ~/.bashrc

echo "Please restart the terminal window."