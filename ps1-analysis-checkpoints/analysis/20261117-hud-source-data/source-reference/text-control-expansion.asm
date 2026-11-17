80016580 addiu    $sp, $sp, -0x30
80016584 sw       $ra, 0x28($sp)
80016588 sw       $fp, 0x24($sp)
8001658c sw       $s0, 0x20($sp)
80016590 move     $fp, $sp
80016594 move     $s0, $a0
80016598 sh       $s0, 0x10($fp)
8001659c sw       $zero, 0x14($fp)
800165a0 lh       $v0, 0x10($fp)
800165a4 addiu    $v1, $zero, 0x4006
800165a8 beq      $v0, $v1, 0x800167d0
800165ac nop      
800165b0 slti     $v1, $v0, 0x4007
800165b4 beqz     $v1, 0x80016608
800165b8 nop      
800165bc addiu    $v1, $zero, 0x4003
800165c0 beq      $v0, $v1, 0x80016710
800165c4 nop      
800165c8 slti     $v1, $v0, 0x4004
800165cc beqz     $v1, 0x800165e8
800165d0 nop      
800165d4 addiu    $v1, $zero, 0x4002
800165d8 beq      $v0, $v1, 0x800166bc
800165dc nop      
800165e0 j        0x80016880
800165e4 nop      
800165e8 addiu    $v1, $zero, 0x4004
800165ec beq      $v0, $v1, 0x80016750
800165f0 nop      
800165f4 addiu    $v1, $zero, 0x4005
800165f8 beq      $v0, $v1, 0x80016790
800165fc nop      
80016600 j        0x80016880
80016604 nop      
80016608 addiu    $v1, $zero, 0x400a
8001660c beq      $v0, $v1, 0x80016860
80016610 nop      
80016614 slti     $v1, $v0, 0x400b
80016618 beqz     $v1, 0x80016640
8001661c nop      
80016620 addiu    $v1, $zero, 0x4007
80016624 beq      $v0, $v1, 0x800167e0
80016628 nop      
8001662c addiu    $v1, $zero, 0x4009
80016630 beq      $v0, $v1, 0x80016820
80016634 nop      
80016638 j        0x80016880
8001663c nop      
80016640 addiu    $v1, $zero, 0x400c
80016644 beq      $v0, $v1, 0x80016870
80016648 nop      
8001664c addiu    $v1, $zero, 0x40ff
80016650 beq      $v0, $v1, 0x80016660
80016654 nop      
80016658 j        0x80016880
8001665c nop      
80016660 lui      $v0, 0x800d
80016664 lw       $v0, -0x2880($v0)
80016668 nop      
8001666c move     $v1, $v0
80016670 sll      $v0, $v1, 1
80016674 lui      $v1, 0x8013
80016678 addiu    $v1, $v1, -0x55c0
8001667c addu     $v0, $v0, $v1
80016680 move     $v1, $v0
80016684 lhu      $v0, 0x10($fp)
80016688 nop      
8001668c sh       $v0, ($v1)
80016690 lui      $v1, 0x800d
80016694 lw       $v1, -0x2880($v1)
80016698 nop      
8001669c addiu    $v0, $v1, 1
800166a0 move     $v1, $v0
800166a4 lui      $at, 0x800d
800166a8 sw       $v1, -0x2880($at)
800166ac addiu    $v0, $zero, 1
800166b0 sw       $v0, 0x14($fp)
800166b4 j        0x80016880
800166b8 nop      
800166bc lui      $v0, 0x800d
800166c0 lw       $v0, -0x2880($v0)
800166c4 nop      
800166c8 move     $v1, $v0
800166cc sll      $v0, $v1, 1
800166d0 lui      $v1, 0x8013
800166d4 addiu    $v1, $v1, -0x55c0
800166d8 addu     $v0, $v0, $v1
800166dc move     $v1, $v0
800166e0 lhu      $v0, 0x10($fp)
800166e4 nop      
800166e8 sh       $v0, ($v1)
800166ec lui      $v1, 0x800d
800166f0 lw       $v1, -0x2880($v1)
800166f4 nop      
800166f8 addiu    $v0, $v1, 1
800166fc move     $v1, $v0
80016700 lui      $at, 0x800d
80016704 sw       $v1, -0x2880($at)
80016708 j        0x80016880
8001670c nop      
80016710 lui      $v0, 0x800d
80016714 lw       $v0, -0x2878($v0)
80016718 nop      
8001671c addiu    $v1, $v0, 2
80016720 lui      $at, 0x800d
80016724 sw       $v1, -0x2878($at)
80016728 lhu      $v0, ($v0)
8001672c nop      
80016730 sh       $v0, 0x18($fp)
80016734 lh       $v0, 0x18($fp)
80016738 nop      
8001673c move     $a0, $v0
80016740 jal      0x800168cc
80016744 nop      
80016748 j        0x80016880
8001674c nop      
80016750 lui      $v0, 0x800d
80016754 lw       $v0, -0x2878($v0)
80016758 nop      
8001675c addiu    $v1, $v0, 2
80016760 lui      $at, 0x800d
80016764 sw       $v1, -0x2878($at)
80016768 lhu      $v0, ($v0)
8001676c nop      
80016770 sh       $v0, 0x18($fp)
80016774 lh       $v0, 0x18($fp)
80016778 nop      
8001677c move     $a0, $v0
80016780 jal      0x80016c54
80016784 nop      
80016788 j        0x80016880
8001678c nop      
80016790 lui      $v0, 0x800d
80016794 lw       $v0, -0x2878($v0)
80016798 nop      
8001679c addiu    $v1, $v0, 2
800167a0 lui      $at, 0x800d
800167a4 sw       $v1, -0x2878($at)
800167a8 lhu      $v0, ($v0)
800167ac nop      
800167b0 sh       $v0, 0x18($fp)
800167b4 lh       $v0, 0x18($fp)
800167b8 nop      
800167bc move     $a0, $v0
800167c0 jal      0x800170a8
800167c4 nop      
800167c8 j        0x80016880
800167cc nop      
800167d0 jal      0x80017188
800167d4 nop      
800167d8 j        0x80016880
800167dc nop      
800167e0 lui      $v0, 0x800d
800167e4 lw       $v0, -0x2878($v0)
800167e8 nop      
800167ec addiu    $v1, $v0, 2
800167f0 lui      $at, 0x800d
800167f4 sw       $v1, -0x2878($at)
800167f8 lhu      $v0, ($v0)
800167fc nop      
80016800 sh       $v0, 0x18($fp)
80016804 lh       $v0, 0x18($fp)
80016808 nop      
8001680c move     $a0, $v0
80016810 jal      0x80017270
80016814 nop      
80016818 j        0x80016880
8001681c nop      
80016820 lui      $v0, 0x800d
80016824 lw       $v0, -0x2878($v0)
80016828 nop      
8001682c addiu    $v1, $v0, 2
80016830 lui      $at, 0x800d
80016834 sw       $v1, -0x2878($at)
80016838 lhu      $v0, ($v0)
8001683c nop      
80016840 sh       $v0, 0x18($fp)
80016844 lh       $v0, 0x18($fp)
80016848 nop      
8001684c move     $a0, $v0
80016850 jal      0x80017354
80016854 nop      
80016858 j        0x80016880
8001685c nop      
80016860 jal      0x80017538
80016864 nop      
80016868 j        0x80016880
8001686c nop      
80016870 jal      0x80017620
80016874 nop      
80016878 j        0x80016880
8001687c nop      
80016880 lw       $v0, 0x14($fp)
80016884 addiu    $v1, $zero, 1
80016888 bne      $v0, $v1, 0x800168a4
8001688c nop      
80016890 addiu    $v0, $zero, 1
80016894 j        0x800168b0
80016898 nop      
8001689c j        0x800168b0
800168a0 nop      
800168a4 move     $v0, $zero
800168a8 j        0x800168b0
800168ac nop      
800168b0 move     $sp, $fp
800168b4 lw       $ra, 0x28($sp)
800168b8 lw       $fp, 0x24($sp)
800168bc lw       $s0, 0x20($sp)
800168c0 addiu    $sp, $sp, 0x30
800168c4 jr       $ra
800168c8 nop      
800168cc addiu    $sp, $sp, -0x48
800168d0 sw       $fp, 0x40($sp)
800168d4 move     $fp, $sp
800168d8 move     $v0, $a0
800168dc sh       $v0, ($fp)
800168e0 lui      $v1, 0x800d
800168e4 lw       $v1, -0x26c8($v1)
800168e8 nop      
800168ec sw       $v1, 0x38($fp)
800168f0 lw       $v1, 0x38($fp)
800168f4 lui      $a0, 0x8000
800168f8 and      $v1, $v1, $a0
800168fc beqz     $v1, 0x80016970
80016900 nop      
80016904 lw       $v1, 0x38($fp)
80016908 nop      
8001690c nor      $a0, $zero, $v1
80016910 sw       $a0, 0x38($fp)
80016914 lw       $a0, 0x38($fp)
80016918 nop      
8001691c addiu    $v1, $a0, 1
80016920 move     $a0, $v1
80016924 sw       $a0, 0x38($fp)
80016928 lui      $v1, 0x800d
8001692c lw       $v1, -0x2880($v1)
80016930 nop      
80016934 move     $a0, $v1
80016938 sll      $v1, $a0, 1
8001693c lui      $a0, 0x8013
80016940 addiu    $a0, $a0, -0x55c0
80016944 addu     $v1, $v1, $a0
80016948 move     $a0, $v1
8001694c addiu    $v1, $zero, 0x2e
80016950 sh       $v1, ($a0)
80016954 lui      $a0, 0x800d
80016958 lw       $a0, -0x2880($a0)
8001695c nop      
80016960 addiu    $v1, $a0, 1
80016964 move     $a0, $v1
80016968 lui      $at, 0x800d
8001696c sw       $a0, -0x2880($at)
80016970 sw       $zero, 4($fp)
80016974 lh       $v1, ($fp)
80016978 lw       $a0, 4($fp)
8001697c nop      
80016980 slt      $v1, $a0, $v1
80016984 bnez     $v1, 0x80016994
80016988 nop      
8001698c j        0x800169f8
80016990 nop      
80016994 lui      $v1, 0x800d
80016998 lw       $v1, -0x2880($v1)
8001699c nop      
800169a0 move     $a0, $v1
800169a4 sll      $v1, $a0, 1
800169a8 lui      $a0, 0x8013
800169ac addiu    $a0, $a0, -0x55c0
800169b0 addu     $v1, $v1, $a0
800169b4 move     $a0, $v1
800169b8 addiu    $v1, $zero, 0x3e
800169bc sh       $v1, ($a0)
800169c0 lw       $a0, 4($fp)
800169c4 nop      
800169c8 addiu    $v1, $a0, 1
800169cc move     $a0, $v1
800169d0 sw       $a0, 4($fp)
800169d4 lui      $a0, 0x800d
800169d8 lw       $a0, -0x2880($a0)
800169dc nop      
800169e0 addiu    $v1, $a0, 1
800169e4 move     $a0, $v1
800169e8 lui      $at, 0x800d
800169ec sw       $a0, -0x2880($at)
800169f0 j        0x80016974
800169f4 nop      
800169f8 lw       $v1, 0x38($fp)
800169fc nop      
80016a00 bnez     $v1, 0x80016a1c
80016a04 nop      
80016a08 addiu    $v1, $zero, 1
80016a0c sw       $v1, 4($fp)
80016a10 sh       $zero, 0x18($fp)
80016a14 j        0x80016ae4
80016a18 nop      
80016a1c sw       $zero, 4($fp)
80016a20 lw       $v1, 0x38($fp)
80016a24 nop      
80016a28 bnez     $v1, 0x80016a38
80016a2c nop      
80016a30 j        0x80016ae4
80016a34 nop      
80016a38 lw       $v1, 0x38($fp)
80016a3c lui      $a1, 0x6666
80016a40 ori      $a1, $a1, 0x6667
80016a44 mult     $v1, $a1
80016a48 mfhi     $a0
80016a4c sra      $a1, $a0, 2
80016a50 sra      $a2, $v1, 0x1f
80016a54 subu     $a0, $a1, $a2
80016a58 move     $a2, $a0
80016a5c sll      $a1, $a2, 2
80016a60 addu     $a1, $a1, $a0
80016a64 sll      $a0, $a1, 1
80016a68 subu     $v1, $v1, $a0
80016a6c sw       $v1, 0x3c($fp)
80016a70 lhu      $v1, 0x3c($fp)
80016a74 nop      
80016a78 sh       $v1, 0x14($fp)
80016a7c lw       $v1, 0x38($fp)
80016a80 lui      $a1, 0x6666
80016a84 ori      $a1, $a1, 0x6667
80016a88 mult     $v1, $a1
80016a8c mfhi     $a0
80016a90 sra      $a1, $a0, 2
80016a94 sra      $a0, $v1, 0x1f
80016a98 subu     $v1, $a1, $a0
80016a9c sw       $v1, 0x38($fp)
80016aa0 lw       $v1, 4($fp)
80016aa4 nop      
80016aa8 move     $a0, $v1
80016aac sll      $v1, $a0, 1
80016ab0 addu     $a0, $v1, $fp
80016ab4 addiu    $v1, $a0, 0x18
80016ab8 move     $a0, $v1
80016abc lhu      $v1, 0x14($fp)
80016ac0 nop      
80016ac4 sh       $v1, ($a0)
80016ac8 lw       $a0, 4($fp)
80016acc nop      
80016ad0 addiu    $v1, $a0, 1
80016ad4 move     $a0, $v1
80016ad8 sw       $a0, 4($fp)
80016adc j        0x80016a20
80016ae0 nop      
80016ae4 lui      $v1, 0x800d
80016ae8 lw       $v1, -0x2880($v1)
80016aec nop      
80016af0 addiu    $a0, $v1, -1
80016af4 sw       $a0, 0x10($fp)
80016af8 sw       $zero, 8($fp)
80016afc addiu    $v1, $zero, 1
80016b00 sw       $v1, 0xc($fp)
80016b04 lw       $v1, 8($fp)
80016b08 lw       $a0, 4($fp)
80016b0c nop      
80016b10 slt      $v1, $v1, $a0
80016b14 bnez     $v1, 0x80016b24
80016b18 nop      
80016b1c j        0x80016c40
80016b20 nop      
80016b24 lw       $v1, 0x10($fp)
80016b28 nop      
80016b2c move     $a0, $v1
80016b30 sll      $v1, $a0, 1
80016b34 lui      $a1, 0x8013
80016b38 addiu    $a1, $a1, -0x55c0
80016b3c addu     $a0, $v1, $a1
80016b40 move     $v1, $a0
80016b44 lw       $a0, 8($fp)
80016b48 nop      
80016b4c move     $a1, $a0
80016b50 sll      $a0, $a1, 1
80016b54 addu     $a1, $a0, $fp
80016b58 addiu    $a0, $a1, 0x18
80016b5c move     $a1, $a0
80016b60 lhu      $a0, ($a1)
80016b64 nop      
80016b68 sh       $a0, ($v1)
80016b6c lw       $a0, 0x10($fp)
80016b70 nop      
80016b74 addiu    $v1, $a0, -1
80016b78 move     $a0, $v1
80016b7c sw       $a0, 0x10($fp)
80016b80 lw       $v1, 0xc($fp)
80016b84 lui      $a1, 0x5555
80016b88 ori      $a1, $a1, 0x5556
80016b8c mult     $v1, $a1
80016b90 mfhi     $a0
80016b94 sra      $a1, $v1, 0x1f
80016b98 subu     $a0, $a0, $a1
80016b9c move     $a2, $a0
80016ba0 sll      $a1, $a2, 1
80016ba4 addu     $a1, $a1, $a0
80016ba8 subu     $v1, $v1, $a1
80016bac bnez     $v1, 0x80016c10
80016bb0 nop      
80016bb4 lw       $a0, 8($fp)
80016bb8 nop      
80016bbc addiu    $v1, $a0, 1
80016bc0 lw       $a0, 4($fp)
80016bc4 nop      
80016bc8 beq      $v1, $a0, 0x80016c10
80016bcc nop      
80016bd0 lw       $v1, 0x10($fp)
80016bd4 nop      
80016bd8 move     $a0, $v1
80016bdc sll      $v1, $a0, 1
80016be0 lui      $a0, 0x8013
80016be4 addiu    $a0, $a0, -0x55c0
80016be8 addu     $v1, $v1, $a0
80016bec move     $a0, $v1
80016bf0 addiu    $v1, $zero, 0x2c
80016bf4 sh       $v1, ($a0)
80016bf8 lw       $a0, 0x10($fp)
80016bfc nop      
80016c00 addiu    $v1, $a0, -1
80016c04 move     $a0, $v1
80016c08 sw       $a0, 0x10($fp)
80016c0c sw       $zero, 0xc($fp)
80016c10 lw       $a0, 8($fp)
80016c14 nop      
80016c18 addiu    $v1, $a0, 1
80016c1c move     $a0, $v1
80016c20 sw       $a0, 8($fp)
80016c24 lw       $a0, 0xc($fp)
80016c28 nop      
80016c2c addiu    $v1, $a0, 1
80016c30 move     $a0, $v1
80016c34 sw       $a0, 0xc($fp)
80016c38 j        0x80016b04
80016c3c nop      
80016c40 move     $sp, $fp
80016c44 lw       $fp, 0x40($sp)
80016c48 addiu    $sp, $sp, 0x48
80016c4c jr       $ra
80016c50 nop      
80016c54 addiu    $sp, $sp, -0x50
80016c58 sw       $fp, 0x48($sp)
80016c5c move     $fp, $sp
80016c60 move     $v0, $a0
80016c64 sh       $v0, ($fp)
80016c68 lh       $v1, ($fp)
80016c6c nop      
80016c70 move     $a0, $v1
80016c74 sll      $v1, $a0, 2
80016c78 lui      $a0, 0x800e
80016c7c addiu    $a0, $a0, 0x4000
80016c80 addu     $v1, $v1, $a0
80016c84 move     $a0, $v1
80016c88 lw       $v1, ($a0)
80016c8c nop      
80016c90 sw       $v1, 0x3c($fp)
80016c94 lw       $v1, 0x3c($fp)
80016c98 lui      $a0, 0x8000
80016c9c bne      $v1, $a0, 0x80016ca8
80016ca0 nop      
80016ca4 sw       $zero, 0x3c($fp)
80016ca8 lw       $v1, 0x3c($fp)
80016cac lui      $a0, 0x8000
80016cb0 and      $v1, $v1, $a0
80016cb4 beqz     $v1, 0x80016d78
80016cb8 nop      
80016cbc lw       $v1, 0x3c($fp)
80016cc0 nop      
80016cc4 nor      $a0, $zero, $v1
80016cc8 sw       $a0, 0x3c($fp)
80016ccc lw       $a0, 0x3c($fp)
80016cd0 nop      
80016cd4 addiu    $v1, $a0, 1
80016cd8 move     $a0, $v1
80016cdc sw       $a0, 0x3c($fp)
80016ce0 lui      $v1, 0x800d
80016ce4 lw       $v1, -0x2880($v1)
80016ce8 nop      
80016cec move     $a0, $v1
80016cf0 sll      $v1, $a0, 1
80016cf4 lui      $a0, 0x8013
80016cf8 addiu    $a0, $a0, -0x55c0
80016cfc addu     $v1, $v1, $a0
80016d00 move     $a0, $v1
80016d04 addiu    $v1, $zero, 0x2e
80016d08 sh       $v1, ($a0)
80016d0c lui      $a0, 0x800d
80016d10 lw       $a0, -0x2880($a0)
80016d14 nop      
80016d18 addiu    $v1, $a0, 1
80016d1c move     $a0, $v1
80016d20 lui      $at, 0x800d
80016d24 sw       $a0, -0x2880($at)
80016d28 lui      $v1, 0x800d
80016d2c lw       $v1, -0x2880($v1)
80016d30 nop      
80016d34 move     $a0, $v1
80016d38 sll      $v1, $a0, 1
80016d3c lui      $a0, 0x8013
80016d40 addiu    $a0, $a0, -0x55c0
80016d44 addu     $v1, $v1, $a0
80016d48 move     $a0, $v1
80016d4c addiu    $v1, $zero, 0x24
80016d50 sh       $v1, ($a0)
80016d54 lui      $a0, 0x800d
80016d58 lw       $a0, -0x2880($a0)
80016d5c nop      
80016d60 addiu    $v1, $a0, 1
80016d64 move     $a0, $v1
80016d68 lui      $at, 0x800d
80016d6c sw       $a0, -0x2880($at)
80016d70 j        0x80016dc0
80016d74 nop      
80016d78 lui      $v1, 0x800d
80016d7c lw       $v1, -0x2880($v1)
80016d80 nop      
80016d84 move     $a0, $v1
80016d88 sll      $v1, $a0, 1
80016d8c lui      $a0, 0x8013
80016d90 addiu    $a0, $a0, -0x55c0
80016d94 addu     $v1, $v1, $a0
80016d98 move     $a0, $v1
80016d9c addiu    $v1, $zero, 0x24
80016da0 sh       $v1, ($a0)
80016da4 lui      $a0, 0x800d
80016da8 lw       $a0, -0x2880($a0)
80016dac nop      
80016db0 addiu    $v1, $a0, 1
80016db4 move     $a0, $v1
80016db8 lui      $at, 0x800d
80016dbc sw       $a0, -0x2880($at)
80016dc0 sw       $zero, 4($fp)
80016dc4 j        0x80016dd4
80016dc8 nop      
80016dcc j        0x80016ea4
80016dd0 nop      
80016dd4 lw       $v1, 0x3c($fp)
80016dd8 lui      $a0, 0xcccc
80016ddc ori      $a0, $a0, 0xcccd
80016de0 multu    $v1, $a0
80016de4 mfhi     $a1
80016de8 srl      $a0, $a1, 3
80016dec move     $a2, $a0
80016df0 sll      $a1, $a2, 2
80016df4 addu     $a1, $a1, $a0
80016df8 sll      $a0, $a1, 1
80016dfc subu     $v1, $v1, $a0
80016e00 sw       $v1, 0x40($fp)
80016e04 lhu      $v1, 0x40($fp)
80016e08 nop      
80016e0c sh       $v1, 0x38($fp)
80016e10 lw       $v1, 0x3c($fp)
80016e14 lui      $a1, 0xcccc
80016e18 ori      $a1, $a1, 0xcccd
80016e1c multu    $v1, $a1
80016e20 mfhi     $a0
80016e24 srl      $v1, $a0, 3
80016e28 sw       $v1, 0x3c($fp)
80016e2c lw       $v1, 4($fp)
80016e30 nop      
80016e34 move     $a0, $v1
80016e38 sll      $v1, $a0, 1
80016e3c addu     $a0, $v1, $fp
80016e40 addiu    $v1, $a0, 0x18
80016e44 move     $a0, $v1
80016e48 lhu      $v1, 0x38($fp)
80016e4c nop      
80016e50 sh       $v1, ($a0)
80016e54 lw       $a0, 4($fp)
80016e58 nop      
80016e5c addiu    $v1, $a0, 1
80016e60 move     $a0, $v1
80016e64 sw       $a0, 4($fp)
80016e68 lui      $a0, 0x800d
80016e6c lw       $a0, -0x2880($a0)
80016e70 nop      
80016e74 addiu    $v1, $a0, 1
80016e78 move     $a0, $v1
80016e7c lui      $at, 0x800d
80016e80 sw       $a0, -0x2880($at)
80016e84 lw       $v1, 0x3c($fp)
80016e88 nop      
80016e8c bnez     $v1, 0x80016e9c
80016e90 nop      
80016e94 j        0x80016ea4
80016e98 nop      
80016e9c j        0x80016dc4
80016ea0 nop      
80016ea4 lw       $v1, 4($fp)
80016ea8 lui      $a1, 0x5555
80016eac ori      $a1, $a1, 0x5556
80016eb0 mult     $v1, $a1
80016eb4 mfhi     $a0
80016eb8 sra      $a1, $v1, 0x1f
80016ebc subu     $v1, $a0, $a1
80016ec0 sw       $v1, 8($fp)
80016ec4 lw       $v1, 4($fp)
80016ec8 lui      $a1, 0x5555
80016ecc ori      $a1, $a1, 0x5556
80016ed0 mult     $v1, $a1
80016ed4 mfhi     $a0
80016ed8 sra      $a1, $v1, 0x1f
80016edc subu     $a0, $a0, $a1
80016ee0 move     $a2, $a0
80016ee4 sll      $a1, $a2, 1
80016ee8 addu     $a1, $a1, $a0
80016eec subu     $v1, $v1, $a1
80016ef0 bnez     $v1, 0x80016f1c
80016ef4 nop      
80016ef8 lw       $v1, 8($fp)
80016efc nop      
80016f00 beqz     $v1, 0x80016f1c
80016f04 nop      
80016f08 lw       $a0, 8($fp)
80016f0c nop      
80016f10 addiu    $v1, $a0, -1
80016f14 move     $a0, $v1
80016f18 sw       $a0, 8($fp)
80016f1c lui      $v1, 0x800d
80016f20 lw       $v1, -0x2880($v1)
80016f24 lw       $a0, 8($fp)
80016f28 nop      
80016f2c addu     $v1, $v1, $a0
80016f30 lui      $at, 0x800d
80016f34 sw       $v1, -0x2880($at)
80016f38 lui      $v1, 0x800d
80016f3c lw       $v1, -0x2880($v1)
80016f40 nop      
80016f44 addiu    $a0, $v1, -1
80016f48 sw       $a0, 0x10($fp)
80016f4c sw       $zero, 8($fp)
80016f50 addiu    $v1, $zero, 1
80016f54 sw       $v1, 0xc($fp)
80016f58 lw       $v1, 8($fp)
80016f5c lw       $a0, 4($fp)
80016f60 nop      
80016f64 slt      $v1, $v1, $a0
80016f68 bnez     $v1, 0x80016f78
80016f6c nop      
80016f70 j        0x80017094
80016f74 nop      
80016f78 lw       $v1, 0x10($fp)
80016f7c nop      
80016f80 move     $a0, $v1
80016f84 sll      $v1, $a0, 1
80016f88 lui      $a1, 0x8013
80016f8c addiu    $a1, $a1, -0x55c0
80016f90 addu     $a0, $v1, $a1
80016f94 move     $v1, $a0
80016f98 lw       $a0, 8($fp)
80016f9c nop      
80016fa0 move     $a1, $a0
80016fa4 sll      $a0, $a1, 1
80016fa8 addu     $a1, $a0, $fp
80016fac addiu    $a0, $a1, 0x18
80016fb0 move     $a1, $a0
80016fb4 lhu      $a0, ($a1)
80016fb8 nop      
80016fbc sh       $a0, ($v1)
80016fc0 lw       $a0, 0x10($fp)
80016fc4 nop      
80016fc8 addiu    $v1, $a0, -1
80016fcc move     $a0, $v1
80016fd0 sw       $a0, 0x10($fp)
80016fd4 lw       $v1, 0xc($fp)
80016fd8 lui      $a1, 0x5555
80016fdc ori      $a1, $a1, 0x5556
80016fe0 mult     $v1, $a1
80016fe4 mfhi     $a0
80016fe8 sra      $a1, $v1, 0x1f
80016fec subu     $a0, $a0, $a1
80016ff0 move     $a2, $a0
80016ff4 sll      $a1, $a2, 1
80016ff8 addu     $a1, $a1, $a0
80016ffc subu     $v1, $v1, $a1
80017000 bnez     $v1, 0x80017064
80017004 nop      
80017008 lw       $a0, 8($fp)
8001700c nop      
80017010 addiu    $v1, $a0, 1
80017014 lw       $a0, 4($fp)
80017018 nop      
8001701c beq      $v1, $a0, 0x80017064
80017020 nop      
80017024 lw       $v1, 0x10($fp)
80017028 nop      
8001702c move     $a0, $v1
80017030 sll      $v1, $a0, 1
80017034 lui      $a0, 0x8013
80017038 addiu    $a0, $a0, -0x55c0
8001703c addu     $v1, $v1, $a0
80017040 move     $a0, $v1
80017044 addiu    $v1, $zero, 0x2c
80017048 sh       $v1, ($a0)
8001704c lw       $a0, 0x10($fp)
80017050 nop      
80017054 addiu    $v1, $a0, -1
80017058 move     $a0, $v1
8001705c sw       $a0, 0x10($fp)
80017060 sw       $zero, 0xc($fp)
80017064 lw       $a0, 8($fp)
80017068 nop      
8001706c addiu    $v1, $a0, 1
80017070 move     $a0, $v1
80017074 sw       $a0, 8($fp)
80017078 lw       $a0, 0xc($fp)
8001707c nop      
80017080 addiu    $v1, $a0, 1
80017084 move     $a0, $v1
80017088 sw       $a0, 0xc($fp)
8001708c j        0x80016f58
80017090 nop      
80017094 move     $sp, $fp
80017098 lw       $fp, 0x48($sp)
8001709c addiu    $sp, $sp, 0x50
800170a0 jr       $ra
800170a4 nop      
800170a8 addiu    $sp, $sp, -0x98
800170ac sw       $fp, 0x90($sp)
800170b0 move     $fp, $sp
800170b4 move     $v0, $a0
800170b8 sh       $v0, ($fp)
800170bc lh       $v1, ($fp)
800170c0 nop      
800170c4 move     $a0, $v1
800170c8 sll      $v1, $a0, 2
800170cc addu     $a0, $v1, $fp
800170d0 addiu    $v1, $a0, 8
800170d4 move     $a0, $v1
800170d8 lw       $v1, ($a0)
800170dc nop      
800170e0 sw       $v1, 0x8c($fp)
800170e4 lw       $v1, 0x8c($fp)
800170e8 nop      
800170ec sw       $v1, 0x88($fp)
800170f0 lw       $v1, 0x88($fp)
800170f4 nop      
800170f8 lh       $a0, ($v1)
800170fc addiu    $v1, $zero, 0x40ff
80017100 bne      $a0, $v1, 0x80017110
80017104 nop      
80017108 j        0x80017174
8001710c nop      
80017110 lui      $v1, 0x800d
80017114 lw       $v1, -0x2880($v1)
80017118 nop      
8001711c move     $a0, $v1
80017120 sll      $v1, $a0, 1
80017124 lui      $a1, 0x8013
80017128 addiu    $a1, $a1, -0x55c0
8001712c addu     $a0, $v1, $a1
80017130 move     $v1, $a0
80017134 lw       $a0, 0x88($fp)
80017138 nop      
8001713c addiu    $a1, $a0, 2
80017140 sw       $a1, 0x88($fp)
80017144 lhu      $a0, ($a0)
80017148 nop      
8001714c sh       $a0, ($v1)
80017150 lui      $a0, 0x800d
80017154 lw       $a0, -0x2880($a0)
80017158 nop      
8001715c addiu    $v1, $a0, 1
80017160 move     $a0, $v1
80017164 lui      $at, 0x800d
80017168 sw       $a0, -0x2880($at)
8001716c j        0x800170f0
80017170 nop      
80017174 move     $sp, $fp
80017178 lw       $fp, 0x90($sp)
8001717c addiu    $sp, $sp, 0x98
80017180 jr       $ra
80017184 nop      
80017188 addiu    $sp, $sp, -0x10
8001718c sw       $fp, 8($sp)
80017190 move     $fp, $sp
80017194 nop      
80017198 sh       $zero, ($fp)
8001719c lh       $v0, ($fp)
800171a0 nop      
800171a4 move     $v1, $v0
800171a8 sll      $v0, $v1, 1
800171ac lui      $v1, 0x8013
800171b0 addiu    $v1, $v1, -0x4d38
800171b4 addu     $v0, $v0, $v1
800171b8 move     $v1, $v0
800171bc lh       $v0, ($v1)
800171c0 addiu    $v1, $zero, 0x40ff
800171c4 bne      $v0, $v1, 0x800171d4
800171c8 nop      
800171cc j        0x8001725c
800171d0 nop      
800171d4 lui      $v0, 0x800d
800171d8 lw       $v0, -0x2880($v0)
800171dc nop      
800171e0 move     $v1, $v0
800171e4 sll      $v0, $v1, 1
800171e8 lui      $a0, 0x8013
800171ec addiu    $a0, $a0, -0x55c0
800171f0 addu     $v1, $v0, $a0
800171f4 move     $v0, $v1
800171f8 lh       $v1, ($fp)
800171fc nop      
80017200 move     $a0, $v1
80017204 sll      $v1, $a0, 1
80017208 lui      $a0, 0x8013
8001720c addiu    $a0, $a0, -0x4d38
80017210 addu     $v1, $v1, $a0
80017214 move     $a0, $v1
80017218 lhu      $v1, ($a0)
8001721c nop      
80017220 sh       $v1, ($v0)
80017224 lhu      $v0, ($fp)
80017228 nop      
8001722c addiu    $v1, $v0, 1
80017230 move     $v0, $v1
80017234 sh       $v0, ($fp)
80017238 lui      $v1, 0x800d
8001723c lw       $v1, -0x2880($v1)
80017240 nop      
80017244 addiu    $v0, $v1, 1
80017248 move     $v1, $v0
8001724c lui      $at, 0x800d
80017250 sw       $v1, -0x2880($at)
80017254 j        0x8001719c
80017258 nop      
8001725c move     $sp, $fp
80017260 lw       $fp, 8($sp)
80017264 addiu    $sp, $sp, 0x10
80017268 jr       $ra
8001726c nop      
80017270 addiu    $sp, $sp, -0x18
80017274 sw       $fp, 0x10($sp)
80017278 move     $fp, $sp
8001727c move     $v0, $a0
80017280 sh       $v0, ($fp)
80017284 lh       $v1, ($fp)
80017288 nop      
8001728c move     $a0, $v1
80017290 sll      $v1, $a0, 2
80017294 lui      $a0, 0x800e
80017298 addiu    $a0, $a0, 0x4370
8001729c addu     $v1, $v1, $a0
800172a0 move     $a0, $v1
800172a4 lw       $v1, ($a0)
800172a8 nop      
800172ac sw       $v1, 8($fp)
800172b0 lw       $v1, 8($fp)
800172b4 nop      
800172b8 sw       $v1, 4($fp)
800172bc lw       $v1, 4($fp)
800172c0 nop      
800172c4 lh       $a0, ($v1)
800172c8 addiu    $v1, $zero, 0x40ff
800172cc bne      $a0, $v1, 0x800172dc
800172d0 nop      
800172d4 j        0x80017340
800172d8 nop      
800172dc lui      $v1, 0x800d
800172e0 lw       $v1, -0x2880($v1)
800172e4 nop      
800172e8 move     $a0, $v1
800172ec sll      $v1, $a0, 1
800172f0 lui      $a1, 0x8013
800172f4 addiu    $a1, $a1, -0x55c0
800172f8 addu     $a0, $v1, $a1
800172fc move     $v1, $a0
80017300 lw       $a0, 4($fp)
80017304 nop      
80017308 addiu    $a1, $a0, 2
8001730c sw       $a1, 4($fp)
80017310 lhu      $a0, ($a0)
80017314 nop      
80017318 sh       $a0, ($v1)
8001731c lui      $a0, 0x800d
80017320 lw       $a0, -0x2880($a0)
80017324 nop      
80017328 addiu    $v1, $a0, 1
8001732c move     $a0, $v1
80017330 lui      $at, 0x800d
80017334 sw       $a0, -0x2880($at)
80017338 j        0x800172bc
8001733c nop      
80017340 move     $sp, $fp
80017344 lw       $fp, 0x10($sp)
80017348 addiu    $sp, $sp, 0x18
8001734c jr       $ra
80017350 nop      
80017354 addiu    $sp, $sp, -0x20
80017358 sw       $fp, 0x18($sp)
8001735c move     $fp, $sp
80017360 move     $v0, $a0
80017364 sh       $v0, ($fp)
80017368 sw       $zero, 4($fp)
8001736c lw       $v1, 4($fp)
80017370 nop      
80017374 slti     $a0, $v1, 2
80017378 bnez     $a0, 0x80017388
8001737c nop      
80017380 j        0x800173e8
80017384 nop      
80017388 lui      $v1, 0x800d
8001738c lw       $v1, -0x2880($v1)
80017390 nop      
80017394 move     $a0, $v1
80017398 sll      $v1, $a0, 1
8001739c lui      $a0, 0x8013
800173a0 addiu    $a0, $a0, -0x55c0
800173a4 addu     $v1, $v1, $a0
800173a8 move     $a0, $v1
800173ac sh       $zero, ($a0)
800173b0 lw       $a0, 4($fp)
800173b4 nop      
800173b8 addiu    $v1, $a0, 1
800173bc move     $a0, $v1
800173c0 sw       $a0, 4($fp)
800173c4 lui      $a0, 0x800d
800173c8 lw       $a0, -0x2880($a0)
800173cc nop      
800173d0 addiu    $v1, $a0, 1
800173d4 move     $a0, $v1
800173d8 lui      $at, 0x800d
800173dc sw       $a0, -0x2880($at)
800173e0 j        0x8001736c
800173e4 nop      
800173e8 lui      $v1, 0x800d
800173ec lw       $v1, -0x2880($v1)
800173f0 nop      
800173f4 addiu    $a0, $v1, -1
800173f8 sw       $a0, 8($fp)
800173fc lh       $v1, ($fp)
80017400 nop      
80017404 move     $a0, $v1
80017408 sll      $v1, $a0, 2
8001740c lui      $a0, 0x8015
80017410 addiu    $a0, $a0, -0x3d90
80017414 addu     $v1, $v1, $a0
80017418 move     $a0, $v1
8001741c lw       $v1, ($a0)
80017420 nop      
80017424 sw       $v1, 0x10($fp)
80017428 sw       $zero, 4($fp)
8001742c lw       $v1, 4($fp)
80017430 nop      
80017434 slti     $a0, $v1, 2
80017438 bnez     $a0, 0x80017448
8001743c nop      
80017440 j        0x80017524
80017444 nop      
80017448 lw       $v1, 0x10($fp)
8001744c lui      $a1, 0x6666
80017450 ori      $a1, $a1, 0x6667
80017454 mult     $v1, $a1
80017458 mfhi     $a0
8001745c sra      $a1, $a0, 2
80017460 sra      $a2, $v1, 0x1f
80017464 subu     $a0, $a1, $a2
80017468 move     $a2, $a0
8001746c sll      $a1, $a2, 2
80017470 addu     $a1, $a1, $a0
80017474 sll      $a0, $a1, 1
80017478 subu     $v1, $v1, $a0
8001747c sw       $v1, 0x14($fp)
80017480 lhu      $v1, 0x14($fp)
80017484 nop      
80017488 sh       $v1, 0xc($fp)
8001748c lw       $v1, 0x10($fp)
80017490 lui      $a1, 0x6666
80017494 ori      $a1, $a1, 0x6667
80017498 mult     $v1, $a1
8001749c mfhi     $a0
800174a0 sra      $a1, $a0, 2
800174a4 sra      $a0, $v1, 0x1f
800174a8 subu     $v1, $a1, $a0
800174ac sw       $v1, 0x10($fp)
800174b0 lw       $v1, 8($fp)
800174b4 nop      
800174b8 move     $a0, $v1
800174bc sll      $v1, $a0, 1
800174c0 lui      $a0, 0x8013
800174c4 addiu    $a0, $a0, -0x55c0
800174c8 addu     $v1, $v1, $a0
800174cc move     $a0, $v1
800174d0 lhu      $v1, 0xc($fp)
800174d4 nop      
800174d8 sh       $v1, ($a0)
800174dc lw       $v1, 0x10($fp)
800174e0 nop      
800174e4 bnez     $v1, 0x800174f4
800174e8 nop      
800174ec j        0x80017524
800174f0 nop      
800174f4 lw       $a0, 4($fp)
800174f8 nop      
800174fc addiu    $v1, $a0, 1
80017500 move     $a0, $v1
80017504 sw       $a0, 4($fp)
80017508 lw       $a0, 8($fp)
8001750c nop      
80017510 addiu    $v1, $a0, -1
80017514 move     $a0, $v1
80017518 sw       $a0, 8($fp)
8001751c j        0x8001742c
80017520 nop      
80017524 move     $sp, $fp
80017528 lw       $fp, 0x18($sp)
8001752c addiu    $sp, $sp, 0x20
80017530 jr       $ra
80017534 nop      
80017538 addiu    $sp, $sp, -0x10
8001753c sw       $fp, 8($sp)
80017540 move     $fp, $sp
80017544 nop      
80017548 sw       $zero, ($fp)
8001754c lw       $v0, ($fp)
80017550 nop      
80017554 move     $v1, $v0
80017558 sll      $v0, $v1, 1
8001755c lui      $v1, 0x800e
80017560 addiu    $v1, $v1, 0x3948
80017564 addu     $v0, $v0, $v1
80017568 move     $v1, $v0
8001756c lh       $v0, ($v1)
80017570 addiu    $v1, $zero, 0x40ff
80017574 bne      $v0, $v1, 0x80017584
80017578 nop      
8001757c j        0x8001760c
80017580 nop      
80017584 lui      $v0, 0x800d
80017588 lw       $v0, -0x2880($v0)
8001758c nop      
80017590 move     $v1, $v0
80017594 sll      $v0, $v1, 1
80017598 lui      $a0, 0x8013
8001759c addiu    $a0, $a0, -0x55c0
800175a0 addu     $v1, $v0, $a0
800175a4 move     $v0, $v1
800175a8 lw       $v1, ($fp)
800175ac nop      
800175b0 move     $a0, $v1
800175b4 sll      $v1, $a0, 1
800175b8 lui      $a0, 0x800e
800175bc addiu    $a0, $a0, 0x3948
800175c0 addu     $v1, $v1, $a0
800175c4 move     $a0, $v1
800175c8 lhu      $v1, ($a0)
800175cc nop      
800175d0 sh       $v1, ($v0)
800175d4 lw       $v1, ($fp)
800175d8 nop      
800175dc addiu    $v0, $v1, 1
800175e0 move     $v1, $v0
800175e4 sw       $v1, ($fp)
800175e8 lui      $v1, 0x800d
800175ec lw       $v1, -0x2880($v1)
800175f0 nop      
800175f4 addiu    $v0, $v1, 1
800175f8 move     $v1, $v0
800175fc lui      $at, 0x800d
80017600 sw       $v1, -0x2880($at)
80017604 j        0x8001754c
80017608 nop      
8001760c move     $sp, $fp
80017610 lw       $fp, 8($sp)
80017614 addiu    $sp, $sp, 0x10
80017618 jr       $ra
8001761c nop      
80017620 addiu    $sp, $sp, -0x10
80017624 sw       $fp, 8($sp)
80017628 move     $fp, $sp
8001762c nop      
80017630 sw       $zero, ($fp)
80017634 lw       $v0, ($fp)
80017638 nop      
8001763c slti     $v1, $v0, 5
80017640 bnez     $v1, 0x80017650
80017644 nop      
80017648 j        0x80017704
8001764c nop      
80017650 lui      $v0, 0x800d
80017654 lh       $v0, -0x271a($v0)
80017658 lw       $v1, ($fp)
8001765c nop      
80017660 slt      $v0, $v1, $v0
80017664 beqz     $v0, 0x800176a0
80017668 nop      
8001766c lui      $v0, 0x800d
80017670 lw       $v0, -0x2880($v0)
80017674 nop      
80017678 move     $v1, $v0
8001767c sll      $v0, $v1, 1
80017680 lui      $v1, 0x8013
80017684 addiu    $v1, $v1, -0x55c0
80017688 addu     $v0, $v0, $v1
8001768c move     $v1, $v0
80017690 addiu    $v0, $zero, 0x28b
80017694 sh       $v0, ($v1)
80017698 j        0x800176cc
8001769c nop      
800176a0 lui      $v0, 0x800d
800176a4 lw       $v0, -0x2880($v0)
800176a8 nop      
800176ac move     $v1, $v0
800176b0 sll      $v0, $v1, 1
800176b4 lui      $v1, 0x8013
800176b8 addiu    $v1, $v1, -0x55c0
800176bc addu     $v0, $v0, $v1
800176c0 move     $v1, $v0
800176c4 addiu    $v0, $zero, 0x28c
800176c8 sh       $v0, ($v1)
800176cc lw       $v1, ($fp)
800176d0 nop      
800176d4 addiu    $v0, $v1, 1
800176d8 move     $v1, $v0
800176dc sw       $v1, ($fp)
800176e0 lui      $v1, 0x800d
800176e4 lw       $v1, -0x2880($v1)
800176e8 nop      
800176ec addiu    $v0, $v1, 1
800176f0 move     $v1, $v0
800176f4 lui      $at, 0x800d
800176f8 sw       $v1, -0x2880($at)
800176fc j        0x80017634
80017700 nop      
80017704 move     $sp, $fp
80017708 lw       $fp, 8($sp)
8001770c addiu    $sp, $sp, 0x10
80017710 jr       $ra
80017714 nop      
80017718 addiu    $sp, $sp, -8
8001771c sw       $fp, ($sp)
80017720 move     $fp, $sp
80017724 addiu    $v0, $zero, 2
80017728 lui      $at, 0x800d
8001772c sh       $v0, -0x2708($at)
80017730 move     $sp, $fp
80017734 lw       $fp, ($sp)
80017738 addiu    $sp, $sp, 8
8001773c jr       $ra
80017740 nop      
80017744 addiu    $sp, $sp, -8
80017748 sw       $fp, ($sp)
8001774c move     $fp, $sp
80017750 addiu    $v0, $zero, 1
80017754 lui      $at, 0x800d
80017758 sh       $v0, -0x2708($at)
8001775c move     $sp, $fp
80017760 lw       $fp, ($sp)
80017764 addiu    $sp, $sp, 8
80017768 jr       $ra
8001776c nop      
80017770 addiu    $sp, $sp, -8
80017774 sw       $fp, ($sp)
80017778 move     $fp, $sp
8001777c lui      $at, 0x800d
80017780 sh       $zero, -0x2708($at)
80017784 move     $sp, $fp
80017788 lw       $fp, ($sp)
8001778c addiu    $sp, $sp, 8
80017790 jr       $ra
80017794 nop      
