do(x int32,y int8) {
    print(4 + 4 + x);
    print(x*int32(y));
    if 5 == 5 {
        print(12 *2);
        print(10/2);
        print(8%3);
    }
    if 1 != 2 {
        print(11);
    }
    if 1 < 2 {
        print(22);
    }
    if 1 <= 2 {
        print(33);
    }
    if 2 >= 1 {
        print(44);
    }
    if 2 > 1 {
        print(55);
    }
    if 5 == 0 { print(12); }
}

main() {
    let y = 16;
    let z = int8(16);
    do(y, int8(8));
}
