8005f500 addiu $sp, $sp, -0x48
8005f504 sw $ra, 0x44($sp)
8005f508 sw $fp, 0x40($sp)
8005f50c move $fp, $sp
8005f510 addiu $a0, $fp, 0x10
8005f514 move $a1, $zero
8005f518 jal 0x8001bd78
8005f51c nop 
8005f520 sw $zero, 0x38($fp)
8005f524 lw $v0, 0x38($fp)
8005f528 nop 
8005f52c slti $v1, $v0, 0xa
8005f530 bnez $v1, 0x8005f540
8005f534 nop 
8005f538 j 0x8005f590
8005f53c nop 
8005f540 lw $v0, 0x38($fp)
8005f544 nop 
8005f548 move $v1, $v0
8005f54c sll $v0, $v1, 2
8005f550 addiu $v1, $fp, 0x10
8005f554 addu $v0, $v0, $v1
8005f558 move $v1, $v0
8005f55c lw $v0, ($v1)
8005f560 addiu $v1, $zero, -1
8005f564 bne $v0, $v1, 0x8005f574
8005f568 nop 
8005f56c j 0x8005f590
8005f570 nop 
8005f574 lw $v1, 0x38($fp)
8005f578 nop 
8005f57c addiu $v0, $v1, 1
8005f580 move $v1, $v0
8005f584 sw $v1, 0x38($fp)
8005f588 j 0x8005f524
8005f58c nop 
8005f590 lui $v0, 0x800d
8005f594 lh $v0, -0x2664($v0)
8005f598 lw $v1, 0x38($fp)
8005f59c nop 
8005f5a0 slt $v0, $v0, $v1
8005f5a4 bnez $v0, 0x8005f5c0
8005f5a8 nop 
8005f5ac lhu $v0, 0x38($fp)
8005f5b0 nop 
8005f5b4 addiu $v1, $v0, -1
8005f5b8 lui $at, 0x800d
8005f5bc sh $v1, -0x2664($at)
8005f5c0 lui $v1, 0x800d
8005f5c4 lw $v1, -0x277c($v1)
8005f5c8 nop 
8005f5cc andi $v0, $v1, 0x20
8005f5d0 beqz $v0, 0x8005f6a8
8005f5d4 nop 
8005f5d8 jal 0x80065000
8005f5dc nop 
8005f5e0 addiu $a0, $zero, 0x5ee
8005f5e4 addiu $a1, $zero, 1
8005f5e8 jal 0x80018940
8005f5ec nop 
8005f5f0 addiu $a0, $zero, 0x11
8005f5f4 move $a1, $zero
8005f5f8 jal 0x80018940
8005f5fc nop 
8005f600 lui $v0, 0x800d
8005f604 lh $v0, -0x2664($v0)
8005f608 nop 
8005f60c move $v1, $v0
8005f610 sll $v0, $v1, 2
8005f614 addiu $v1, $fp, 0x10
8005f618 addu $v0, $v0, $v1
8005f61c move $v1, $v0
8005f620 addiu $a0, $zero, 2
8005f624 lw $a1, ($v1)
8005f628 jal 0x80062a4c
8005f62c nop 
8005f630 lui $v0, 0x800d
8005f634 lh $v0, -0x2664($v0)
8005f638 nop 
8005f63c move $v1, $v0
8005f640 sll $v0, $v1, 2
8005f644 addiu $v1, $fp, 0x10
8005f648 addu $v0, $v0, $v1
8005f64c move $v1, $v0
8005f650 lw $v0, ($v1)
8005f654 nop 
8005f658 move $a0, $v0
8005f65c sll $v1, $a0, 2
8005f660 addu $v1, $v1, $v0
8005f664 sll $v0, $v1, 7
8005f668 subu $v0, $v0, $v1
8005f66c sll $v1, $v0, 3
8005f670 lui $v0, 0x8013
8005f674 addiu $v0, $v0, -0x4d08
8005f678 addu $v1, $v0, $v1
8005f67c sw $v1, 0x3c($fp)
8005f680 lw $a0, 0x3c($fp)
8005f684 jal 0x80041218
8005f688 nop 
8005f68c lw $a0, 0x3c($fp)
8005f690 jal 0x8004a27c
8005f694 nop 
8005f698 jal 0x80018a5c
8005f69c nop 
8005f6a0 j 0x8005f7b0
8005f6a4 nop 
8005f6a8 lui $v1, 0x800d
8005f6ac lw $v1, -0x277c($v1)
8005f6b0 nop 
8005f6b4 andi $v0, $v1, 0x50
8005f6b8 beqz $v0, 0x8005f6f8
8005f6bc nop 
8005f6c0 jal 0x80065974
8005f6c4 nop 
8005f6c8 addiu $a0, $zero, 0x10
8005f6cc move $a1, $zero
8005f6d0 jal 0x80018940
8005f6d4 nop 
8005f6d8 move $a0, $zero
8005f6dc move $a1, $zero
8005f6e0 jal 0x80062a4c
8005f6e4 nop 
8005f6e8 jal 0x80065040
8005f6ec nop 
8005f6f0 j 0x8005f7b0
8005f6f4 nop 
8005f6f8 lui $v1, 0x800d
8005f6fc lw $v1, -0x27b0($v1)
8005f700 nop 
8005f704 andi $v0, $v1, 0x4000
8005f708 beqz $v0, 0x8005f758
8005f70c nop 
8005f710 lui $v0, 0x800d
8005f714 lhu $v0, -0x2664($v0)
8005f718 nop 
8005f71c addiu $v1, $v0, 1
8005f720 move $v0, $v1
8005f724 lui $at, 0x800d
8005f728 sh $v0, -0x2664($at)
8005f72c sll $v1, $v0, 0x10
8005f730 sra $v0, $v1, 0x10
8005f734 lw $v1, 0x38($fp)
8005f738 nop 
8005f73c slt $v0, $v0, $v1
8005f740 bnez $v0, 0x8005f750
8005f744 nop 
8005f748 lui $at, 0x800d
8005f74c sh $zero, -0x2664($at)
8005f750 j 0x8005f7b0
8005f754 nop 
8005f758 lui $v1, 0x800d
8005f75c lw $v1, -0x27b0($v1)
8005f760 nop 
8005f764 andi $v0, $v1, 0x1000
8005f768 beqz $v0, 0x8005f7b0
8005f76c nop 
8005f770 lui $v0, 0x800d
8005f774 lhu $v0, -0x2664($v0)
8005f778 nop 
8005f77c addiu $v1, $v0, -1
8005f780 move $v0, $v1
8005f784 lui $at, 0x800d
8005f788 sh $v0, -0x2664($at)
8005f78c sll $v1, $v0, 0x10
8005f790 sra $v0, $v1, 0x10
8005f794 bgez $v0, 0x8005f7b0
8005f798 nop 
8005f79c lhu $v0, 0x38($fp)
8005f7a0 nop 
8005f7a4 addiu $v1, $v0, -1
8005f7a8 lui $at, 0x800d
8005f7ac sh $v1, -0x2664($at)
8005f7b0 lui $v0, 0x800d
8005f7b4 lw $v0, -0x2684($v0)
8005f7b8 addiu $v1, $zero, 1
8005f7bc bne $v0, $v1, 0x8005f7e0
8005f7c0 nop 
8005f7c4 lui $v0, 0x800d
8005f7c8 lh $v0, -0x2664($v0)
8005f7cc nop 
8005f7d0 addiu $v1, $v0, 1
8005f7d4 move $a0, $v1
8005f7d8 jal 0x80051918
8005f7dc nop 
8005f7e0 move $sp, $fp
8005f7e4 lw $ra, 0x44($sp)
8005f7e8 lw $fp, 0x40($sp)
8005f7ec addiu $sp, $sp, 0x48
8005f7f0 jr $ra
8005f7f4 nop 
8005f7f8 addiu $sp, $sp, -8
8005f7fc sw $fp, ($sp)
8005f800 move $fp, $sp
8005f804 move $sp, $fp
8005f808 lw $fp, ($sp)
8005f80c addiu $sp, $sp, 8
8005f810 jr $ra
8005f814 nop 
8005f818 addiu $sp, $sp, -0x40
8005f81c sw $ra, 0x3c($sp)
8005f820 sw $fp, 0x38($sp)
8005f824 move $fp, $sp
8005f828 sb $zero, 0x24($fp)
8005f82c sw $zero, 0x2c($fp)
8005f830 addiu $v0, $zero, 3
8005f834 sw $v0, 0x30($fp)
8005f838 lui $v0, 0x800a
8005f83c lhu $v0, -0x6290($v0)
8005f840 nop 
8005f844 sh $v0, 0x20($fp)
8005f848 lui $v0, 0x800a
8005f84c lhu $v0, -0x628e($v0)
8005f850 nop 
8005f854 addiu $v1, $v0, 0x10
8005f858 sh $v1, 0x22($fp)
8005f85c lhu $v0, 0x20($fp)
8005f860 nop 
8005f864 sh $v0, 0x10($fp)
8005f868 lhu $v0, 0x22($fp)
8005f86c nop 
8005f870 sh $v0, 0x12($fp)
8005f874 addiu $v0, $zero, 0xf0
8005f878 sh $v0, 0x14($fp)
8005f87c addiu $v0, $zero, 0x10
8005f880 sh $v0, 0x16($fp)
8005f884 sb $zero, 0x18($fp)
8005f888 addiu $a0, $zero, 0x10
8005f88c addiu $a1, $zero, 1
8005f890 jal 0x80018940
8005f894 nop 
8005f898 lhu $a0, 0x10($fp)
8005f89c nop 
8005f8a0 andi $v1, $a0, 0xffff
8005f8a4 lui $a0, 0xffff
8005f8a8 and $v0, $v0, $a0
8005f8ac or $v0, $v0, $v1
8005f8b0 lhu $v1, 0x12($fp)
8005f8b4 nop 
8005f8b8 sll $a0, $v1, 0x10
8005f8bc andi $v0, $v0, 0xffff
8005f8c0 or $v0, $v0, $a0
8005f8c4 lhu $a1, 0x14($fp)
8005f8c8 nop 
8005f8cc andi $a0, $a1, 0xffff
8005f8d0 lui $a1, 0xffff
8005f8d4 and $v1, $v1, $a1
8005f8d8 or $v1, $v1, $a0
8005f8dc lhu $a0, 0x16($fp)
8005f8e0 nop 
8005f8e4 sll $a1, $a0, 0x10
8005f8e8 andi $v1, $v1, 0xffff
8005f8ec or $v1, $v1, $a1
8005f8f0 lhu $a1, 0x18($fp)
8005f8f4 nop 
8005f8f8 andi $a0, $a1, 0xffff
8005f8fc lui $a1, 0xffff
8005f900 and $a2, $a2, $a1
8005f904 or $a2, $a2, $a0
8005f908 move $a0, $v0
8005f90c move $a1, $v1
8005f910 move $a3, $zero
8005f914 jal 0x800182d0
8005f918 nop 
8005f91c lui $at, 0x800d
8005f920 sh $v0, -0x25ec($at)
8005f924 jal 0x800157b4
8005f928 nop 
8005f92c lb $v0, 0x24($fp)
8005f930 lui $a0, 0x800a
8005f934 addiu $a0, $a0, -0x6290
8005f938 move $a1, $v0
8005f93c jal 0x8005fb54
8005f940 nop 
8005f944 j 0x8005f954
8005f948 nop 
8005f94c j 0x8005fb18
8005f950 nop 
8005f954 lw $v0, 0x2c($fp)
8005f958 nop 
8005f95c move $v1, $v0
8005f960 sll $v0, $v1, 4
8005f964 move $v1, $v0
8005f968 addiu $v0, $v1, 0x40
8005f96c sll $v1, $v0, 0x10
8005f970 sra $v0, $v1, 0x10
8005f974 addiu $a0, $zero, 0x20
8005f978 move $a1, $v0
8005f97c jal 0x8005fdd4
8005f980 nop 
8005f984 lw $v0, 0x2c($fp)
8005f988 nop 
8005f98c move $v1, $v0
8005f990 sll $v0, $v1, 4
8005f994 move $v1, $v0
8005f998 lhu $v0, 0x22($fp)
8005f99c nop 
8005f9a0 addu $v1, $v1, $v0
8005f9a4 sh $v1, 0x12($fp)
8005f9a8 lhu $a0, 0x10($fp)
8005f9ac nop 
8005f9b0 andi $v1, $a0, 0xffff
8005f9b4 lui $a0, 0xffff
8005f9b8 and $v0, $v0, $a0
8005f9bc or $v0, $v0, $v1
8005f9c0 lhu $v1, 0x12($fp)
8005f9c4 nop 
8005f9c8 sll $a0, $v1, 0x10
8005f9cc andi $v0, $v0, 0xffff
8005f9d0 or $v0, $v0, $a0
8005f9d4 lhu $a1, 0x14($fp)
8005f9d8 nop 
8005f9dc andi $a0, $a1, 0xffff
8005f9e0 lui $a1, 0xffff
8005f9e4 and $v1, $v1, $a1
8005f9e8 or $v1, $v1, $a0
8005f9ec lhu $a0, 0x16($fp)
8005f9f0 nop 
8005f9f4 sll $a1, $a0, 0x10
8005f9f8 andi $v1, $v1, 0xffff
8005f9fc or $v1, $v1, $a1
8005fa00 lhu $a1, 0x18($fp)
8005fa04 nop 
8005fa08 andi $a0, $a1, 0xffff
8005fa0c lui $a1, 0xffff
8005fa10 and $a2, $a2, $a1
8005fa14 or $a2, $a2, $a0
8005fa18 move $a0, $v0
8005fa1c move $a1, $v1
8005fa20 move $a3, $zero
8005fa24 jal 0x800182d0
8005fa28 nop 
8005fa2c jal 0x80018a5c
8005fa30 nop 
8005fa34 move $a0, $zero
8005fa38 jal 0x80041374
8005fa3c nop 
8005fa40 lui $v1, 0x800d
8005fa44 lw $v1, -0x25f4($v1)
8005fa48 nop 
8005fa4c andi $v0, $v1, 0x1000
8005fa50 beqz $v0, 0x8005fa84
8005fa54 nop 
8005fa58 lw $v0, 0x2c($fp)
8005fa5c nop 
8005fa60 addiu $v1, $v0, 1
8005fa64 move $v0, $v1
8005fa68 sw $v0, 0x2c($fp)
8005fa6c lw $v1, 0x30($fp)
8005fa70 nop 
8005fa74 slt $v0, $v0, $v1
8005fa78 beqz $v0, 0x8005fa84
8005fa7c nop 
8005fa80 sw $zero, 0x2c($fp)
8005fa84 lui $v1, 0x800d
8005fa88 lw $v1, -0x25f4($v1)
8005fa8c nop 
8005fa90 andi $v0, $v1, 0x4000
8005fa94 beqz $v0, 0x8005fac8
8005fa98 nop 
8005fa9c lw $v1, 0x2c($fp)
8005faa0 nop 
8005faa4 addiu $v0, $v1, -1
8005faa8 move $v1, $v0
8005faac sw $v1, 0x2c($fp)
8005fab0 bgez $v1, 0x8005fac8
8005fab4 nop 
8005fab8 lw $v0, 0x30($fp)
8005fabc nop 
8005fac0 addiu $v1, $v0, -1
8005fac4 sw $v1, 0x2c($fp)
8005fac8 lui $v1, 0x800d
8005facc lw $v1, -0x25d8($v1)
8005fad0 nop 
8005fad4 andi $v0, $v1, 0x40
8005fad8 beqz $v0, 0x8005faf0
8005fadc nop 
8005fae0 addiu $v0, $zero, -1
8005fae4 sw $v0, 0x2c($fp)
8005fae8 j 0x8005fb18
8005faec nop 
8005faf0 lui $v1, 0x800d
8005faf4 lw $v1, -0x25d8($v1)
8005faf8 nop 
8005fafc andi $v0, $v1, 0x20
8005fb00 beqz $v0, 0x8005fb10
8005fb04 nop 
8005fb08 j 0x8005fb18
8005fb0c nop 
8005fb10 j 0x8005f944
8005fb14 nop 
8005fb18 jal 0x800157b4
8005fb1c nop 
8005fb20 addiu $a0, $zero, 0x10
8005fb24 move $a1, $zero
8005fb28 jal 0x80018940
8005fb2c nop 
8005fb30 lw $v0, 0x2c($fp)
8005fb34 j 0x8005fb3c
8005fb38 nop 
8005fb3c move $sp, $fp
8005fb40 lw $ra, 0x3c($sp)
8005fb44 lw $fp, 0x38($sp)
8005fb48 addiu $sp, $sp, 0x40
8005fb4c jr $ra
8005fb50 nop 
8005fb54 addiu $sp, $sp, -0x48
8005fb58 sw $ra, 0x40($sp)
8005fb5c sw $fp, 0x3c($sp)
8005fb60 sw $s0, 0x38($sp)
8005fb64 move $fp, $sp
8005fb68 sw $a0, 0x48($fp)
8005fb6c move $s0, $a1
8005fb70 sb $s0, 0x10($fp)
8005fb74 lw $v0, 0x48($fp)
8005fb78 nop 
8005fb7c lhu $v1, ($v0)
8005fb80 nop 
8005fb84 sh $v1, 0x18($fp)
8005fb88 lw $v0, 0x48($fp)
8005fb8c nop 
8005fb90 lhu $v1, 2($v0)
8005fb94 nop 
8005fb98 sh $v1, 0x1a($fp)
8005fb9c lw $v0, 0x48($fp)
8005fba0 nop 
8005fba4 lhu $v1, 4($v0)
8005fba8 nop 
8005fbac sh $v1, 0x1c($fp)
8005fbb0 lw $v0, 0x48($fp)
8005fbb4 nop 
8005fbb8 lhu $v1, 6($v0)
8005fbbc nop 
8005fbc0 sh $v1, 0x1e($fp)
8005fbc4 lbu $v0, 0x10($fp)
8005fbc8 nop 
8005fbcc sb $v0, 0x20($fp)
8005fbd0 lhu $a0, 0x18($fp)
8005fbd4 nop 
8005fbd8 andi $v1, $a0, 0xffff
8005fbdc lui $a0, 0xffff
8005fbe0 and $v0, $v0, $a0
8005fbe4 or $v0, $v0, $v1
8005fbe8 lhu $v1, 0x1a($fp)
8005fbec nop 
8005fbf0 sll $a0, $v1, 0x10
8005fbf4 andi $v0, $v0, 0xffff
8005fbf8 or $v0, $v0, $a0
8005fbfc lhu $a1, 0x1c($fp)
8005fc00 nop 
8005fc04 andi $a0, $a1, 0xffff
8005fc08 lui $a1, 0xffff
8005fc0c and $v1, $v1, $a1
8005fc10 or $v1, $v1, $a0
8005fc14 lhu $a0, 0x1e($fp)
8005fc18 nop 
8005fc1c sll $a1, $a0, 0x10
8005fc20 andi $v1, $v1, 0xffff
8005fc24 or $v1, $v1, $a1
8005fc28 lhu $a1, 0x20($fp)
8005fc2c nop 
8005fc30 andi $a0, $a1, 0xffff
8005fc34 lui $a1, 0xffff
8005fc38 and $a2, $a2, $a1
8005fc3c or $a2, $a2, $a0
8005fc40 move $a0, $v0
8005fc44 move $a1, $v1
8005fc48 jal 0x80017798
8005fc4c nop 
8005fc50 lw $v0, 0x48($fp)
8005fc54 nop 
8005fc58 lw $v1, 8($v0)
8005fc5c nop 
8005fc60 sw $v1, 0x30($fp)
8005fc64 sw $zero, 0x34($fp)
8005fc68 lw $v0, 0x34($fp)
8005fc6c nop 
8005fc70 move $v1, $v0
8005fc74 sll $v0, $v1, 1
8005fc78 lw $v1, 0x30($fp)
8005fc7c nop 
8005fc80 addu $v0, $v0, $v1
8005fc84 move $v1, $v0
8005fc88 lh $v0, ($v1)
8005fc8c addiu $v1, $zero, -1
8005fc90 bne $v0, $v1, 0x8005fca0
8005fc94 nop 
8005fc98 j 0x8005fdb8
8005fc9c nop 
8005fca0 lw $v0, 0x34($fp)
8005fca4 nop 
8005fca8 addiu $v1, $v0, 1
8005fcac sw $v1, 0x34($fp)
8005fcb0 sll $v1, $v0, 1
8005fcb4 lw $a0, 0x30($fp)
8005fcb8 nop 
8005fcbc addu $v0, $v1, $a0
8005fcc0 move $v1, $v0
8005fcc4 lhu $v0, ($v1)
8005fcc8 nop 
8005fccc sh $v0, 0x28($fp)
8005fcd0 lw $v0, 0x48($fp)
8005fcd4 lw $v1, 0x34($fp)
8005fcd8 nop 
8005fcdc addiu $a0, $v1, 1
8005fce0 sw $a0, 0x34($fp)
8005fce4 sll $a0, $v1, 1
8005fce8 lw $a1, 0x30($fp)
8005fcec nop 
8005fcf0 addu $v1, $a0, $a1
8005fcf4 move $a0, $v1
8005fcf8 lhu $v0, ($v0)
8005fcfc lhu $v1, ($a0)
8005fd00 nop 
8005fd04 addu $v0, $v0, $v1
8005fd08 sh $v0, 0x2a($fp)
8005fd0c lw $v0, 0x48($fp)
8005fd10 lw $v1, 0x34($fp)
8005fd14 nop 
8005fd18 addiu $a0, $v1, 1
8005fd1c sw $a0, 0x34($fp)
8005fd20 sll $a0, $v1, 1
8005fd24 lw $a1, 0x30($fp)
8005fd28 nop 
8005fd2c addu $v1, $a0, $a1
8005fd30 move $a0, $v1
8005fd34 lhu $v0, 2($v0)
8005fd38 lhu $v1, ($a0)
8005fd3c nop 
8005fd40 addu $v0, $v0, $v1
8005fd44 sh $v0, 0x2c($fp)
8005fd48 lhu $a0, 0x28($fp)
8005fd4c nop 
8005fd50 andi $v1, $a0, 0xffff
8005fd54 lui $a0, 0xffff
8005fd58 and $v0, $v0, $a0
8005fd5c or $v0, $v0, $v1
8005fd60 lhu $v1, 0x2a($fp)
8005fd64 nop 
8005fd68 sll $a0, $v1, 0x10
8005fd6c andi $v0, $v0, 0xffff
8005fd70 or $v0, $v0, $a0
8005fd74 lhu $a1, 0x2c($fp)
8005fd78 nop 
8005fd7c andi $a0, $a1, 0xffff
8005fd80 lui $a1, 0xffff
8005fd84 and $v1, $v1, $a1
8005fd88 or $v1, $v1, $a0
8005fd8c lhu $a0, 0x2e($fp)
8005fd90 nop 
8005fd94 sll $a1, $a0, 0x10
8005fd98 andi $v1, $v1, 0xffff
8005fd9c or $v1, $v1, $a1
8005fda0 move $a0, $v0
8005fda4 move $a1, $v1
8005fda8 jal 0x800155d0
8005fdac nop 
8005fdb0 j 0x8005fc68
8005fdb4 nop 
8005fdb8 move $sp, $fp
8005fdbc lw $ra, 0x40($sp)
8005fdc0 lw $fp, 0x3c($sp)
8005fdc4 lw $s0, 0x38($sp)
8005fdc8 addiu $sp, $sp, 0x48
8005fdcc jr $ra
8005fdd0 nop 
8005fdd4 addiu $sp, $sp, -0x28
8005fdd8 sw $ra, 0x24($sp)
8005fddc sw $fp, 0x20($sp)
8005fde0 sw $s1, 0x1c($sp)
8005fde4 sw $s0, 0x18($sp)
8005fde8 move $fp, $sp
8005fdec move $s0, $a0
8005fdf0 move $s1, $a1
8005fdf4 sh $s0, 0x10($fp)
8005fdf8 sh $s1, 0x12($fp)
8005fdfc lhu $v0, 0x10($fp)
8005fe00 nop 
8005fe04 addiu $v1, $v0, 3
8005fe08 sll $a0, $v1, 0x10
8005fe0c sra $v0, $a0, 0x10
8005fe10 lhu $v1, 0x12($fp)
8005fe14 nop 
8005fe18 addiu $a0, $v1, 3
8005fe1c sll $a1, $a0, 0x10
8005fe20 sra $v1, $a1, 0x10
8005fe24 move $a0, $v0
8005fe28 move $a1, $v1
8005fe2c jal 0x8004e938
8005fe30 nop 
8005fe34 move $sp, $fp
8005fe38 lw $ra, 0x24($sp)
8005fe3c lw $fp, 0x20($sp)
8005fe40 lw $s1, 0x1c($sp)
8005fe44 lw $s0, 0x18($sp)
8005fe48 addiu $sp, $sp, 0x28
8005fe4c jr $ra
8005fe50 nop 
