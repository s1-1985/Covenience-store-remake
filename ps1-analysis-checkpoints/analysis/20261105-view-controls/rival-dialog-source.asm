8004d6ec addiu $sp, $sp, -0x48
8004d6f0 sw $ra, 0x44($sp)
8004d6f4 sw $fp, 0x40($sp)
8004d6f8 sw $s1, 0x3c($sp)
8004d6fc sw $s0, 0x38($sp)
8004d700 move $fp, $sp
8004d704 move $s0, $a0
8004d708 move $s1, $a1
8004d70c sw $a2, 0x50($fp)
8004d710 sh $s0, 0x18($fp)
8004d714 sh $s1, 0x1a($fp)
8004d718 addiu $v0, $zero, 2
8004d71c sw $v0, 0x30($fp)
8004d720 addiu $v0, $fp, 0x20
8004d724 addiu $v1, $fp, 0x28
8004d728 addiu $a0, $zero, 6
8004d72c move $a1, $v0
8004d730 move $a2, $v1
8004d734 jal 0x80013f7c
8004d738 nop 
8004d73c lhu $a0, 0x20($fp)
8004d740 nop 
8004d744 andi $v1, $a0, 0xffff
8004d748 lui $a0, 0xffff
8004d74c and $v0, $v0, $a0
8004d750 or $v0, $v0, $v1
8004d754 lhu $v1, 0x22($fp)
8004d758 nop 
8004d75c sll $a0, $v1, 0x10
8004d760 andi $v0, $v0, 0xffff
8004d764 or $v0, $v0, $a0
8004d768 lhu $a1, 0x24($fp)
8004d76c nop 
8004d770 andi $a0, $a1, 0xffff
8004d774 lui $a1, 0xffff
8004d778 and $v1, $v1, $a1
8004d77c or $v1, $v1, $a0
8004d780 lhu $a0, 0x26($fp)
8004d784 nop 
8004d788 sll $a1, $a0, 0x10
8004d78c andi $v1, $v1, 0xffff
8004d790 or $v1, $v1, $a1
8004d794 lhu $a1, 0x28($fp)
8004d798 nop 
8004d79c andi $a0, $a1, 0xffff
8004d7a0 lui $a1, 0xffff
8004d7a4 and $a3, $a3, $a1
8004d7a8 or $a3, $a3, $a0
8004d7ac lhu $a0, 0x2a($fp)
8004d7b0 nop 
8004d7b4 sll $a1, $a0, 0x10
8004d7b8 andi $a3, $a3, 0xffff
8004d7bc or $a3, $a3, $a1
8004d7c0 addiu $a0, $sp, 0x10
8004d7c4 addiu $a1, $fp, 0x2c
8004d7c8 lwl $t1, 3($a1)
8004d7cc lwr $t1, ($a1)
8004d7d0 nop 
8004d7d4 swl $t1, 3($a0)
8004d7d8 swr $t1, ($a0)
8004d7dc lui $a0, 0x8015
8004d7e0 ori $a0, $a0, 0xea00
8004d7e4 move $a1, $v0
8004d7e8 move $a2, $v1
8004d7ec jal 0x80013eac
8004d7f0 nop 
8004d7f4 lw $v0, 0x50($fp)
8004d7f8 nop 
8004d7fc lb $v1, 2($v0)
8004d800 addiu $v0, $zero, 1
8004d804 bne $v1, $v0, 0x8004d87c
8004d808 nop 
8004d80c lh $v0, 0x18($fp)
8004d810 lh $v1, 0x1a($fp)
8004d814 move $a0, $v0
8004d818 move $a1, $v1
8004d81c lw $a2, 0x50($fp)
8004d820 jal 0x8004d8c8
8004d824 nop 
8004d828 j 0x8004d838
8004d82c nop 
8004d830 j 0x8004d874
8004d834 nop 
8004d838 move $a0, $zero
8004d83c jal 0x80041374
8004d840 nop 
8004d844 lui $v1, 0x800d
8004d848 lw $v1, -0x25d8($v1)
8004d84c nop 
8004d850 andi $v0, $v1, 0x60
8004d854 beqz $v0, 0x8004d86c
8004d858 nop 
8004d85c jal 0x80065000
8004d860 nop 
8004d864 j 0x8004d874
8004d868 nop 
8004d86c j 0x8004d828
8004d870 nop 
8004d874 j 0x8004d89c
8004d878 nop 
8004d87c lh $v0, 0x18($fp)
8004d880 lh $v1, 0x1a($fp)
8004d884 move $a0, $v0
8004d888 move $a1, $v1
8004d88c lw $a2, 0x50($fp)
8004d890 jal 0x8004dfac
8004d894 nop 
8004d898 sw $v0, 0x30($fp)
8004d89c lw $v0, 0x30($fp)
8004d8a0 j 0x8004d8a8
8004d8a4 nop 
8004d8a8 move $sp, $fp
8004d8ac lw $ra, 0x44($sp)
8004d8b0 lw $fp, 0x40($sp)
8004d8b4 lw $s1, 0x3c($sp)
8004d8b8 lw $s0, 0x38($sp)
8004d8bc addiu $sp, $sp, 0x48
8004d8c0 jr $ra
8004d8c4 nop 
8004d8c8 addiu $sp, $sp, -0x40
8004d8cc sw $ra, 0x3c($sp)
8004d8d0 sw $fp, 0x38($sp)
8004d8d4 sw $s1, 0x34($sp)
8004d8d8 sw $s0, 0x30($sp)
8004d8dc move $fp, $sp
8004d8e0 move $s0, $a0
8004d8e4 move $s1, $a1
8004d8e8 sw $a2, 0x48($fp)
8004d8ec sh $s0, 0x10($fp)
8004d8f0 sh $s1, 0x12($fp)
8004d8f4 lhu $v0, 0x10($fp)
8004d8f8 nop 
8004d8fc sh $v0, 0x18($fp)
8004d900 lhu $v0, 0x12($fp)
8004d904 nop 
8004d908 sh $v0, 0x1a($fp)
8004d90c addiu $v0, $zero, 8
8004d910 sh $v0, 0x1c($fp)
8004d914 addiu $v0, $zero, 0xd
8004d918 sh $v0, 0x1e($fp)
8004d91c sb $zero, 0x20($fp)
8004d920 addiu $a0, $zero, 4
8004d924 addiu $a1, $zero, 1
8004d928 jal 0x80018940
8004d92c nop 
8004d930 lhu $a0, 0x18($fp)
8004d934 nop 
8004d938 andi $v1, $a0, 0xffff
8004d93c lui $a0, 0xffff
8004d940 and $v0, $v0, $a0
8004d944 or $v0, $v0, $v1
8004d948 lhu $v1, 0x1a($fp)
8004d94c nop 
8004d950 sll $a0, $v1, 0x10
8004d954 andi $v0, $v0, 0xffff
8004d958 or $v0, $v0, $a0
8004d95c lhu $a1, 0x1c($fp)
8004d960 nop 
8004d964 andi $a0, $a1, 0xffff
8004d968 lui $a1, 0xffff
8004d96c and $v1, $v1, $a1
8004d970 or $v1, $v1, $a0
8004d974 lhu $a0, 0x1e($fp)
8004d978 nop 
8004d97c sll $a1, $a0, 0x10
8004d980 andi $v1, $v1, 0xffff
8004d984 or $v1, $v1, $a1
8004d988 lhu $a1, 0x20($fp)
8004d98c nop 
8004d990 andi $a0, $a1, 0xffff
8004d994 lui $a1, 0xffff
8004d998 and $a2, $a2, $a1
8004d99c or $a2, $a2, $a0
8004d9a0 move $a0, $v0
8004d9a4 move $a1, $v1
8004d9a8 jal 0x80017b18
8004d9ac nop 
8004d9b0 jal 0x800157b4
8004d9b4 nop 
8004d9b8 lui $v0, 0x800d
8004d9bc lbu $v0, -0x26b8($v0)
8004d9c0 nop 
8004d9c4 sb $v0, 0x28($fp)
8004d9c8 lw $v0, 0x48($fp)
8004d9cc nop 
8004d9d0 lhu $v1, 4($v0)
8004d9d4 nop 
8004d9d8 andi $v0, $v1, 0x8000
8004d9dc andi $v1, $v0, 0xffff
8004d9e0 bnez $v1, 0x8004da2c
8004d9e4 nop 
8004d9e8 lhu $v0, 0x10($fp)
8004d9ec nop 
8004d9f0 addiu $v1, $v0, 0x10
8004d9f4 sll $a0, $v1, 0x10
8004d9f8 sra $v0, $a0, 0x10
8004d9fc lhu $v1, 0x12($fp)
8004da00 nop 
8004da04 addiu $a0, $v1, 0x10
8004da08 sll $a1, $a0, 0x10
8004da0c sra $v1, $a1, 0x10
8004da10 move $a0, $v0
8004da14 move $a1, $v1
8004da18 addiu $a2, $zero, 0x180
8004da1c jal 0x8004e494
8004da20 nop 
8004da24 j 0x8004da78
8004da28 nop 
8004da2c lhu $v0, 0x10($fp)
8004da30 nop 
8004da34 addiu $v1, $v0, 0x10
8004da38 sll $a0, $v1, 0x10
8004da3c sra $v0, $a0, 0x10
8004da40 lhu $v1, 0x12($fp)
8004da44 nop 
8004da48 addiu $a0, $v1, 0x10
8004da4c sll $a1, $a0, 0x10
8004da50 sra $v1, $a1, 0x10
8004da54 lb $a0, 0x28($fp)
8004da58 nop 
8004da5c addiu $a1, $a0, 0x16a
8004da60 sll $a0, $a1, 0x10
8004da64 sra $a2, $a0, 0x10
8004da68 move $a0, $v0
8004da6c move $a1, $v1
8004da70 jal 0x8004e494
8004da74 nop 
8004da78 lw $v0, 0x48($fp)
8004da7c nop 
8004da80 lhu $v1, 4($v0)
8004da84 nop 
8004da88 andi $v0, $v1, 0x7f
8004da8c andi $v1, $v0, 0xffff
8004da90 lui $at, 0x800d
8004da94 sw $v1, -0x26c8($at)
8004da98 lui $v0, 0x800d
8004da9c lw $v0, -0x26c8($v0)
8004daa0 addiu $v1, $zero, 1
8004daa4 bne $v0, $v1, 0x8004daf0
8004daa8 nop 
8004daac lhu $v0, 0x10($fp)
8004dab0 nop 
8004dab4 addiu $v1, $v0, 0x10
8004dab8 sll $a0, $v1, 0x10
8004dabc sra $v0, $a0, 0x10
8004dac0 lhu $v1, 0x12($fp)
8004dac4 nop 
8004dac8 addiu $a0, $v1, 0x20
8004dacc sll $a1, $a0, 0x10
8004dad0 sra $v1, $a1, 0x10
8004dad4 move $a0, $v0
8004dad8 move $a1, $v1
8004dadc addiu $a2, $zero, 0xc
8004dae0 jal 0x8004e494
8004dae4 nop 
8004dae8 j 0x8004db2c
8004daec nop 
8004daf0 lhu $v0, 0x10($fp)
8004daf4 nop 
8004daf8 addiu $v1, $v0, 0x10
8004dafc sll $a0, $v1, 0x10
8004db00 sra $v0, $a0, 0x10
8004db04 lhu $v1, 0x12($fp)
8004db08 nop 
8004db0c addiu $a0, $v1, 0x20
8004db10 sll $a1, $a0, 0x10
8004db14 sra $v1, $a1, 0x10
8004db18 move $a0, $v0
8004db1c move $a1, $v1
