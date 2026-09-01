#!/bin/bash

if [[ -z $1 || "$1" == "test" ]]; then
# TEST ASLR
echo "#include <stdio.h>" > a.c
echo "int main() { printf(\"%p\\n\", main); return 0; }" >> a.c
gcc a.c
./a.out > r1
./a.out > r2
diff --brief <(sort r1) <(sort r2) >/dev/null
comp_value=$?

if [ $comp_value -eq 1 ]
then
    echo "ASLR is on. Turning off would make your debugging easy. To turn off ASLR, run './aslr.sh off'"
else
    echo "ASLR is off. Turning on would make your system secure. To turn on ASLR, run './aslr.sh on'"
fi

rm r1
rm r2
rm a.out
rm a.c
exit;
fi

if [ "$1" == "on" ]; then
echo 2 | sudo tee /proc/sys/kernel/randomize_va_space
exit;
fi

if [ "$1" == "off" ]; then
echo 0 | sudo tee /proc/sys/kernel/randomize_va_space
exit;
fi
