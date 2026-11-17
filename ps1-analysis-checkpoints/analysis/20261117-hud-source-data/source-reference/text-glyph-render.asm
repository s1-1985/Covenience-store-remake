800153ec addiu    $sp, $sp, -0x30
800153f0 sw       $ra, 0x2c($sp)
800153f4 sw       $fp, 0x28($sp)
800153f8 move     $fp, $sp
800153fc sw       $a0, 0x30($fp)
80015400 sw       $a1, 0x34($fp)
80015404 lui      $at, 0x800d
80015408 sw       $zero, -0x2880($at)
8001540c lhu      $v0, 0x30($fp)
80015410 nop      
80015414 sh       $v0, 0x20($fp)
80015418 lh       $v0, 0x20($fp)
8001541c nop      
80015420 move     $a0, $v0
80015424 jal      0x800157dc
80015428 nop      
8001542c lhu      $v0, 0x32($fp)
80015430 nop      
80015434 addiu    $v1, $v0, -0xa0
80015438 sh       $v1, 0x24($fp)
8001543c lhu      $v0, 0x32($fp)
80015440 nop      
80015444 addiu    $v1, $v0, -0xa0
80015448 sh       $v1, 0x32($fp)
8001544c lhu      $v0, 0x34($fp)
80015450 nop      
80015454 addiu    $v1, $v0, -0x70
80015458 sh       $v1, 0x26($fp)
8001545c lui      $v0, 0x800d
80015460 lh       $v0, -0x25c2($v0)
80015464 nop      
80015468 sw       $v0, 0x18($fp)
8001546c sw       $zero, 0x1c($fp)
80015470 sw       $zero, 0x10($fp)
80015474 j        0x80015484
80015478 nop      
8001547c j        0x80015590
80015480 nop      
80015484 lw       $v0, 0x10($fp)
80015488 nop      
8001548c move     $v1, $v0
80015490 sll      $v0, $v1, 1
80015494 lui      $v1, 0x8013
80015498 addiu    $v1, $v1, -0x55c0
8001549c addu     $v0, $v0, $v1
800154a0 move     $v1, $v0
800154a4 lhu      $v0, ($v1)
800154a8 nop      
800154ac sh       $v0, 0x22($fp)
800154b0 lw       $v1, 0x10($fp)
800154b4 nop      
800154b8 addiu    $v0, $v1, 1
800154bc move     $v1, $v0
800154c0 sw       $v1, 0x10($fp)
800154c4 lh       $v0, 0x22($fp)
800154c8 nop      
800154cc move     $a0, $v0
800154d0 jal      0x80015888
800154d4 nop      
800154d8 sw       $v0, 0x14($fp)
800154dc lw       $v0, 0x14($fp)
800154e0 nop      
800154e4 beqz     $v0, 0x80015530
800154e8 nop      
800154ec lh       $v0, 0x24($fp)
800154f0 lh       $v1, 0x26($fp)
800154f4 move     $a0, $v0
800154f8 move     $a1, $v1
800154fc lw       $a2, 0x18($fp)
80015500 jal      0x80015fcc
80015504 nop      
80015508 lw       $v1, 0x18($fp)
8001550c nop      
80015510 addiu    $v0, $v1, 1
80015514 move     $v1, $v0
80015518 sw       $v1, 0x18($fp)
8001551c lw       $v1, 0x1c($fp)
80015520 nop      
80015524 addiu    $v0, $v1, 1
80015528 move     $v1, $v0
8001552c sw       $v1, 0x1c($fp)
80015530 addiu    $v0, $fp, 0x24
80015534 addiu    $v1, $fp, 0x26
80015538 lh       $a2, 0x32($fp)
8001553c lh       $a3, 0x22($fp)
80015540 move     $a0, $v0
80015544 move     $a1, $v1
80015548 jal      0x800162d4
8001554c nop      
80015550 lui      $v0, 0x800d
80015554 lh       $v0, -0x271c($v0)
80015558 nop      
8001555c andi     $v1, $v0, 0x8000
80015560 beqz     $v1, 0x80015588
80015564 nop      
80015568 lui      $v0, 0x800d
8001556c lhu      $v0, -0x271c($v0)
80015570 nop      
80015574 andi     $v1, $v0, 0x7fff
80015578 lui      $at, 0x800d
8001557c sh       $v1, -0x271c($at)
80015580 j        0x80015590
80015584 nop      
80015588 j        0x80015474
8001558c nop      
80015590 lui      $v0, 0x800d
80015594 lhu      $v0, -0x25c2($v0)
80015598 lhu      $v1, 0x1c($fp)
8001559c nop      
800155a0 addu     $v0, $v0, $v1
800155a4 lui      $at, 0x800d
800155a8 sh       $v0, -0x25c2($at)
800155ac lw       $v0, 0x1c($fp)
800155b0 j        0x800155b8
800155b4 nop      
800155b8 move     $sp, $fp
800155bc lw       $ra, 0x2c($sp)
800155c0 lw       $fp, 0x28($sp)
800155c4 addiu    $sp, $sp, 0x30
800155c8 jr       $ra
800155cc nop      
800155d0 addiu    $sp, $sp, -0x30
800155d4 sw       $ra, 0x2c($sp)
800155d8 sw       $fp, 0x28($sp)
800155dc move     $fp, $sp
800155e0 sw       $a0, 0x30($fp)
800155e4 sw       $a1, 0x34($fp)
800155e8 lui      $at, 0x800d
800155ec sw       $zero, -0x2880($at)
800155f0 lhu      $v0, 0x30($fp)
800155f4 nop      
800155f8 sh       $v0, 0x20($fp)
800155fc lh       $v0, 0x20($fp)
80015600 nop      
80015604 move     $a0, $v0
80015608 jal      0x800157dc
8001560c nop      
80015610 lhu      $v0, 0x32($fp)
80015614 nop      
80015618 addiu    $v1, $v0, -0xa0
8001561c sh       $v1, 0x24($fp)
80015620 lhu      $v0, 0x32($fp)
80015624 nop      
80015628 addiu    $v1, $v0, -0xa0
8001562c sh       $v1, 0x32($fp)
80015630 lhu      $v0, 0x34($fp)
80015634 nop      
80015638 addiu    $v1, $v0, -0x70
8001563c sh       $v1, 0x26($fp)
80015640 lui      $v0, 0x800d
80015644 lh       $v0, -0x25c4($v0)
80015648 nop      
8001564c sw       $v0, 0x18($fp)
80015650 sw       $zero, 0x1c($fp)
80015654 sw       $zero, 0x10($fp)
80015658 j        0x80015668
8001565c nop      
80015660 j        0x80015774
80015664 nop      
80015668 lw       $v0, 0x10($fp)
8001566c nop      
80015670 move     $v1, $v0
80015674 sll      $v0, $v1, 1
80015678 lui      $v1, 0x8013
8001567c addiu    $v1, $v1, -0x55c0
80015680 addu     $v0, $v0, $v1
80015684 move     $v1, $v0
80015688 lhu      $v0, ($v1)
8001568c nop      
80015690 sh       $v0, 0x22($fp)
80015694 lw       $v1, 0x10($fp)
80015698 nop      
8001569c addiu    $v0, $v1, 1
800156a0 move     $v1, $v0
800156a4 sw       $v1, 0x10($fp)
800156a8 lh       $v0, 0x22($fp)
800156ac nop      
800156b0 move     $a0, $v0
800156b4 jal      0x80015888
800156b8 nop      
800156bc sw       $v0, 0x14($fp)
800156c0 lw       $v0, 0x14($fp)
800156c4 nop      
800156c8 beqz     $v0, 0x80015714
800156cc nop      
800156d0 lh       $v0, 0x24($fp)
800156d4 lh       $v1, 0x26($fp)
800156d8 move     $a0, $v0
800156dc move     $a1, $v1
800156e0 lw       $a2, 0x18($fp)
800156e4 jal      0x80015cc0
800156e8 nop      
800156ec lw       $v1, 0x18($fp)
800156f0 nop      
800156f4 addiu    $v0, $v1, 1
800156f8 move     $v1, $v0
800156fc sw       $v1, 0x18($fp)
80015700 lw       $v1, 0x1c($fp)
80015704 nop      
80015708 addiu    $v0, $v1, 1
8001570c move     $v1, $v0
80015710 sw       $v1, 0x1c($fp)
80015714 addiu    $v0, $fp, 0x24
80015718 addiu    $v1, $fp, 0x26
8001571c lh       $a2, 0x32($fp)
80015720 lh       $a3, 0x22($fp)
80015724 move     $a0, $v0
80015728 move     $a1, $v1
8001572c jal      0x800162d4
80015730 nop      
80015734 lui      $v0, 0x800d
80015738 lh       $v0, -0x271c($v0)
8001573c nop      
80015740 andi     $v1, $v0, 0x8000
80015744 beqz     $v1, 0x8001576c
80015748 nop      
8001574c lui      $v0, 0x800d
80015750 lhu      $v0, -0x271c($v0)
80015754 nop      
80015758 andi     $v1, $v0, 0x7fff
8001575c lui      $at, 0x800d
80015760 sh       $v1, -0x271c($at)
80015764 j        0x80015774
80015768 nop      
8001576c j        0x80015658
80015770 nop      
80015774 lui      $v0, 0x800d
80015778 lhu      $v0, -0x25c4($v0)
8001577c lhu      $v1, 0x1c($fp)
80015780 nop      
80015784 addu     $v0, $v0, $v1
80015788 lui      $at, 0x800d
8001578c sh       $v0, -0x25c4($at)
80015790 lw       $v0, 0x1c($fp)
80015794 j        0x8001579c
80015798 nop      
8001579c move     $sp, $fp
800157a0 lw       $ra, 0x2c($sp)
800157a4 lw       $fp, 0x28($sp)
800157a8 addiu    $sp, $sp, 0x30
800157ac jr       $ra
800157b0 nop      
800157b4 addiu    $sp, $sp, -8
800157b8 sw       $fp, ($sp)
800157bc move     $fp, $sp
800157c0 lui      $at, 0x800d
800157c4 sh       $zero, -0x25c4($at)
800157c8 move     $sp, $fp
800157cc lw       $fp, ($sp)
800157d0 addiu    $sp, $sp, 8
800157d4 jr       $ra
800157d8 nop      
800157dc addiu    $sp, $sp, -0x30
800157e0 sw       $ra, 0x28($sp)
800157e4 sw       $fp, 0x24($sp)
800157e8 sw       $s0, 0x20($sp)
800157ec move     $fp, $sp
800157f0 move     $s0, $a0
800157f4 sh       $s0, 0x10($fp)
800157f8 lui      $v0, 0x800d
800157fc lw       $v0, -0x2880($v0)
80015800 lui      $at, 0x800d
80015804 sw       $v0, -0x287c($at)
80015808 lh       $v0, 0x10($fp)
8001580c nop      
80015810 sw       $v0, 0x18($fp)
80015814 lw       $v0, 0x18($fp)
80015818 nop      
8001581c sll      $v1, $v0, 2
80015820 sw       $v1, 0x18($fp)
80015824 lw       $v0, 0x18($fp)
80015828 lui      $v1, 0x8018
8001582c ori      $v1, $v1, 0x3e00
80015830 addu     $v0, $v0, $v1
80015834 sw       $v0, 0x14($fp)
80015838 lw       $v0, 0x14($fp)
8001583c nop      
80015840 lw       $v1, ($v0)
80015844 nop      
80015848 sw       $v1, 0x18($fp)
8001584c lw       $v0, 0x18($fp)
80015850 lui      $v1, 0x8018
80015854 ori      $v1, $v1, 0x3e00
80015858 addu     $v0, $v0, $v1
8001585c lui      $at, 0x800d
80015860 sw       $v0, -0x2878($at)
80015864 jal      0x80016478
80015868 nop      
8001586c move     $sp, $fp
80015870 lw       $ra, 0x28($sp)
80015874 lw       $fp, 0x24($sp)
80015878 lw       $s0, 0x20($sp)
8001587c addiu    $sp, $sp, 0x30
80015880 jr       $ra
80015884 nop      
80015888 addiu    $sp, $sp, -0x28
8001588c sw       $ra, 0x20($sp)
80015890 sw       $fp, 0x1c($sp)
80015894 sw       $s0, 0x18($sp)
80015898 move     $fp, $sp
8001589c move     $s0, $a0
800158a0 sh       $s0, 0x10($fp)
800158a4 lhu      $v0, 0x10($fp)
800158a8 nop      
800158ac andi     $v1, $v0, 0x4000
800158b0 sll      $a0, $v1, 0x10
800158b4 sra      $v0, $a0, 0x10
800158b8 beqz     $v0, 0x80015918
800158bc nop      
800158c0 lh       $v0, 0x10($fp)
800158c4 addiu    $v1, $zero, 0x4002
800158c8 beq      $v0, $v1, 0x800158fc
800158cc nop      
800158d0 addiu    $v1, $zero, 0x40ff
800158d4 beq      $v0, $v1, 0x800158e4
800158d8 nop      
800158dc j        0x8001590c
800158e0 nop      
800158e4 lhu      $v0, 0x220($gp)
800158e8 addiu    $v1, $zero, -0x8000
800158ec or       $v0, $v0, $v1
800158f0 sh       $v0, 0x220($gp)
800158f4 j        0x8001590c
800158f8 nop      
800158fc lhu      $v0, 0x220($gp)
80015900 nop      
80015904 ori      $v1, $v0, 1
80015908 sh       $v1, 0x220($gp)
8001590c sw       $zero, 0x14($fp)
80015910 j        0x80015964
80015914 nop      
80015918 lui      $v0, 0x800d
8001591c lh       $v0, -0x2708($v0)
80015920 addiu    $v1, $zero, 2
80015924 bne      $v0, $v1, 0x80015948
80015928 nop      
8001592c lh       $v0, 0x10($fp)
80015930 nop      
80015934 move     $a0, $v0
80015938 jal      0x80015bf0
8001593c nop      
80015940 j        0x8001595c
80015944 nop      
80015948 lh       $v0, 0x10($fp)
8001594c nop      
80015950 move     $a0, $v0
80015954 jal      0x8001598c
80015958 nop      
8001595c addiu    $v0, $zero, 1
80015960 sw       $v0, 0x14($fp)
80015964 lw       $v0, 0x14($fp)
80015968 j        0x80015970
8001596c nop      
80015970 move     $sp, $fp
80015974 lw       $ra, 0x20($sp)
80015978 lw       $fp, 0x1c($sp)
8001597c lw       $s0, 0x18($sp)
80015980 addiu    $sp, $sp, 0x28
80015984 jr       $ra
80015988 nop      
8001598c addiu    $sp, $sp, -0x68
80015990 sw       $ra, 0x60($sp)
80015994 sw       $fp, 0x5c($sp)
80015998 sw       $s0, 0x58($sp)
8001599c move     $fp, $sp
800159a0 move     $s0, $a0
800159a4 sh       $s0, 0x10($fp)
800159a8 addiu    $v0, $fp, 0x18
800159ac addiu    $v1, $fp, 0x18
800159b0 lui      $v0, 0x800d
800159b4 addiu    $v0, $v0, -0x2928
800159b8 lwl      $t0, 3($v0)
800159bc lwr      $t0, ($v0)
800159c0 nop      
800159c4 swl      $t0, 3($v1)
800159c8 swr      $t0, ($v1)
800159cc addiu    $v0, $fp, 0x20
800159d0 addiu    $v0, $fp, 0x20
800159d4 lui      $v1, 0x8001
800159d8 addiu    $v1, $v1, 0x54
800159dc move     $a0, $v0
800159e0 move     $a1, $v1
800159e4 addiu    $a2, $zero, 0x22
800159e8 jal      0x8007e57c
800159ec nop      
800159f0 addiu    $v0, $fp, 0x48
800159f4 addiu    $v0, $fp, 0x48
800159f8 lui      $v1, 0x800d
800159fc addiu    $v1, $v1, -0x2924
80015a00 lwl      $t0, 3($v1)
80015a04 lwr      $t0, ($v1)
80015a08 nop      
80015a0c swl      $t0, 3($v0)
80015a10 swr      $t0, ($v0)
80015a14 sw       $zero, 0x50($fp)
80015a18 lw       $v0, 0x50($fp)
80015a1c nop      
80015a20 move     $v1, $v0
80015a24 sll      $v0, $v1, 1
80015a28 addiu    $v1, $fp, 0x10
80015a2c addu     $v0, $v0, $v1
80015a30 addiu    $v1, $v0, 8
80015a34 move     $v0, $v1
80015a38 lh       $v1, 0x10($fp)
80015a3c lh       $v0, ($v0)
80015a40 nop      
80015a44 slt      $v1, $v1, $v0
80015a48 beqz     $v1, 0x80015a58
80015a4c nop      
80015a50 j        0x80015a74
80015a54 nop      
80015a58 lw       $v1, 0x50($fp)
80015a5c nop      
80015a60 addiu    $v0, $v1, 1
80015a64 move     $v1, $v0
80015a68 sw       $v1, 0x50($fp)
80015a6c j        0x80015a18
80015a70 nop      
80015a74 lw       $v0, 0x50($fp)
80015a78 nop      
80015a7c move     $v1, $v0
80015a80 sll      $v0, $v1, 1
80015a84 addiu    $v1, $fp, 0x10
80015a88 addu     $v0, $v0, $v1
80015a8c addiu    $v1, $v0, 0x38
80015a90 move     $v0, $v1
80015a94 lhu      $v1, ($v0)
80015a98 lui      $at, 0x8014
80015a9c sh       $v1, 0x3fc4($at)
80015aa0 lh       $v0, 0x10($fp)
80015aa4 lh       $v1, 0x18($fp)
80015aa8 nop      
80015aac slt      $v0, $v0, $v1
80015ab0 bnez     $v0, 0x80015acc
80015ab4 nop      
80015ab8 lhu      $v0, 0x10($fp)
80015abc lhu      $v1, 0x18($fp)
80015ac0 nop      
80015ac4 subu     $v0, $v0, $v1
80015ac8 sh       $v0, 0x10($fp)
80015acc sw       $zero, 0x50($fp)
80015ad0 lw       $v0, 0x50($fp)
80015ad4 nop      
80015ad8 move     $v1, $v0
80015adc sll      $v0, $v1, 1
80015ae0 addiu    $v1, $fp, 0x10
80015ae4 addu     $v0, $v0, $v1
80015ae8 addiu    $v1, $v0, 0x10
80015aec move     $v0, $v1
80015af0 lh       $v1, 0x10($fp)
80015af4 lh       $v0, ($v0)
80015af8 nop      
80015afc slt      $v1, $v1, $v0
80015b00 beqz     $v1, 0x80015b10
80015b04 nop      
80015b08 j        0x80015b2c
80015b0c nop      
80015b10 lw       $v1, 0x50($fp)
80015b14 nop      
80015b18 addiu    $v0, $v1, 1
80015b1c move     $v1, $v0
80015b20 sw       $v1, 0x50($fp)
80015b24 j        0x80015ad0
80015b28 nop      
80015b2c lw       $v1, 0x50($fp)
80015b30 nop      
80015b34 addiu    $v0, $v1, -1
80015b38 move     $v1, $v0
80015b3c sw       $v1, 0x50($fp)
80015b40 lw       $v0, 0x50($fp)
80015b44 nop      
80015b48 move     $v1, $v0
80015b4c sll      $v0, $v1, 4
80015b50 lui      $at, 0x8014
80015b54 sb       $v0, 0x3fc7($at)
80015b58 lh       $v0, 0x10($fp)
80015b5c lh       $v1, 0x22($fp)
80015b60 nop      
80015b64 slt      $v0, $v0, $v1
80015b68 beqz     $v0, 0x80015b78
80015b6c nop      
80015b70 j        0x80015b94
80015b74 nop      
80015b78 lhu      $v0, 0x10($fp)
80015b7c lhu      $v1, 0x22($fp)
80015b80 nop      
80015b84 subu     $v0, $v0, $v1
80015b88 sh       $v0, 0x10($fp)
80015b8c j        0x80015b58
80015b90 nop      
80015b94 lh       $v0, 0x10($fp)
80015b98 nop      
80015b9c move     $a0, $v0
80015ba0 sll      $v1, $a0, 1
80015ba4 addu     $v1, $v1, $v0
80015ba8 sll      $v0, $v1, 2
80015bac lui      $at, 0x8014
80015bb0 sb       $v0, 0x3fc6($at)
80015bb4 lui      $at, 0x8014
80015bb8 sh       $zero, 0x3fc8($at)
80015bbc addiu    $v0, $zero, 0x1e0
80015bc0 lui      $at, 0x8014
80015bc4 sh       $v0, 0x3fca($at)
80015bc8 addiu    $v0, $zero, 0xc
80015bcc lui      $at, 0x8014
80015bd0 sh       $v0, 0x3fc0($at)
80015bd4 move     $sp, $fp
80015bd8 lw       $ra, 0x60($sp)
80015bdc lw       $fp, 0x5c($sp)
80015be0 lw       $s0, 0x58($sp)
80015be4 addiu    $sp, $sp, 0x68
80015be8 jr       $ra
80015bec nop      
80015bf0 addiu    $sp, $sp, -0x10
80015bf4 sw       $fp, 8($sp)
80015bf8 move     $fp, $sp
80015bfc move     $v0, $a0
80015c00 sh       $v0, ($fp)
80015c04 addiu    $v1, $zero, 0xf
80015c08 lui      $at, 0x8014
80015c0c sh       $v1, 0x3fc4($at)
80015c10 lh       $v1, ($fp)
80015c14 nop      
80015c18 move     $a0, $v1
80015c1c bgez     $a0, 0x80015c28
80015c20 nop      
80015c24 addiu    $a0, $a0, 0xf
80015c28 sra      $a0, $a0, 4
80015c2c move     $a1, $a0
80015c30 sll      $a0, $a1, 4
80015c34 subu     $v1, $v1, $a0
80015c38 sh       $v1, 2($fp)
80015c3c lh       $v1, 2($fp)
80015c40 nop      
80015c44 move     $a0, $v1
80015c48 sll      $v1, $a0, 4
80015c4c lui      $at, 0x8014
80015c50 sb       $v1, 0x3fc6($at)
80015c54 lh       $a0, ($fp)
80015c58 nop      
80015c5c move     $v1, $a0
80015c60 bgez     $v1, 0x80015c6c
80015c64 nop      
80015c68 addiu    $v1, $v1, 0xf
80015c6c sra      $v1, $v1, 4
80015c70 sh       $v1, 2($fp)
80015c74 lh       $v1, 2($fp)
80015c78 nop      
80015c7c move     $a0, $v1
80015c80 sll      $v1, $a0, 4
80015c84 lui      $at, 0x8014
80015c88 sb       $v1, 0x3fc7($at)
80015c8c lui      $at, 0x8014
80015c90 sh       $zero, 0x3fc8($at)
80015c94 addiu    $v1, $zero, 0x1e0
80015c98 lui      $at, 0x8014
80015c9c sh       $v1, 0x3fca($at)
80015ca0 addiu    $v1, $zero, 0x10
80015ca4 lui      $at, 0x8014
80015ca8 sh       $v1, 0x3fc0($at)
80015cac move     $sp, $fp
80015cb0 lw       $fp, 8($sp)
80015cb4 addiu    $sp, $sp, 0x10
80015cb8 jr       $ra
80015cbc nop      
80015cc0 addiu    $sp, $sp, -0x10
80015cc4 sw       $fp, 8($sp)
80015cc8 move     $fp, $sp
80015ccc move     $v0, $a0
80015cd0 move     $v1, $a1
80015cd4 sw       $a2, 0x18($fp)
80015cd8 sh       $v0, ($fp)
80015cdc sh       $v1, 2($fp)
80015ce0 lw       $a0, 0x18($fp)
80015ce4 nop      
80015ce8 move     $a2, $a0
80015cec sll      $a1, $a2, 3
80015cf0 addu     $a1, $a1, $a0
80015cf4 sll      $a0, $a1, 2
80015cf8 lui      $at, 0x800e
80015cfc addu     $at, $at, $a0
80015d00 sw       $zero, -0x3380($at)
80015d04 lw       $a0, 0x18($fp)
80015d08 nop      
80015d0c move     $a2, $a0
80015d10 sll      $a1, $a2, 3
80015d14 addu     $a1, $a1, $a0
80015d18 sll      $a0, $a1, 2
80015d1c lui      $a1, 0x8014
80015d20 lhu      $a1, 0x3fc0($a1)
80015d24 lui      $at, 0x800e
80015d28 addu     $at, $at, $a0
80015d2c sh       $a1, -0x3378($at)
80015d30 lw       $a0, 0x18($fp)
80015d34 nop      
80015d38 move     $a2, $a0
80015d3c sll      $a1, $a2, 3
80015d40 addu     $a1, $a1, $a0
80015d44 sll      $a0, $a1, 2
80015d48 addiu    $a1, $zero, 0x10
80015d4c lui      $at, 0x800e
80015d50 addu     $at, $at, $a0
80015d54 sh       $a1, -0x3376($at)
80015d58 lw       $a0, 0x18($fp)
80015d5c nop      
80015d60 move     $a2, $a0
80015d64 sll      $a1, $a2, 3
80015d68 addu     $a1, $a1, $a0
80015d6c sll      $a0, $a1, 2
80015d70 lhu      $a1, ($fp)
80015d74 lui      $at, 0x800e
80015d78 addu     $at, $at, $a0
80015d7c sh       $a1, -0x337c($at)
80015d80 lw       $a0, 0x18($fp)
80015d84 nop      
80015d88 move     $a2, $a0
80015d8c sll      $a1, $a2, 3
80015d90 addu     $a1, $a1, $a0
80015d94 sll      $a0, $a1, 2
80015d98 lhu      $a1, 2($fp)
80015d9c lui      $at, 0x800e
80015da0 addu     $at, $at, $a0
80015da4 sh       $a1, -0x337a($at)
80015da8 lw       $a0, 0x18($fp)
80015dac nop      
80015db0 move     $a2, $a0
80015db4 sll      $a1, $a2, 3
80015db8 addu     $a1, $a1, $a0
80015dbc sll      $a0, $a1, 2
80015dc0 lui      $at, 0x800e
80015dc4 addu     $at, $at, $a0
80015dc8 sh       $zero, -0x3368($at)
80015dcc lw       $a0, 0x18($fp)
80015dd0 nop      
80015dd4 move     $a2, $a0
80015dd8 sll      $a1, $a2, 3
80015ddc addu     $a1, $a1, $a0
80015de0 sll      $a0, $a1, 2
80015de4 lui      $at, 0x800e
80015de8 addu     $at, $at, $a0
80015dec sh       $zero, -0x3366($at)
80015df0 lw       $a0, 0x18($fp)
80015df4 nop      
80015df8 move     $a2, $a0
80015dfc sll      $a1, $a2, 3
80015e00 addu     $a1, $a1, $a0
80015e04 sll      $a0, $a1, 2
80015e08 lui      $a1, 0x8014
80015e0c lhu      $a1, 0x3fc4($a1)
80015e10 lui      $at, 0x800e
80015e14 addu     $at, $at, $a0
80015e18 sh       $a1, -0x3374($at)
80015e1c lw       $a0, 0x18($fp)
80015e20 nop      
80015e24 move     $a2, $a0
80015e28 sll      $a1, $a2, 3
80015e2c addu     $a1, $a1, $a0
80015e30 sll      $a0, $a1, 2
80015e34 lui      $a1, 0x8014
80015e38 lbu      $a1, 0x3fc6($a1)
80015e3c lui      $at, 0x800e
80015e40 addu     $at, $at, $a0
80015e44 sb       $a1, -0x3372($at)
80015e48 lw       $a0, 0x18($fp)
80015e4c nop      
80015e50 move     $a2, $a0
80015e54 sll      $a1, $a2, 3
80015e58 addu     $a1, $a1, $a0
80015e5c sll      $a0, $a1, 2
80015e60 lui      $a1, 0x8014
80015e64 lbu      $a1, 0x3fc7($a1)
80015e68 lui      $at, 0x800e
80015e6c addu     $at, $at, $a0
80015e70 sb       $a1, -0x3371($at)
80015e74 lw       $a0, 0x18($fp)
80015e78 nop      
80015e7c move     $a2, $a0
80015e80 sll      $a1, $a2, 3
80015e84 addu     $a1, $a1, $a0
80015e88 sll      $a0, $a1, 2
80015e8c lui      $a1, 0x8014
80015e90 lhu      $a1, 0x3fc8($a1)
80015e94 lui      $at, 0x800e
80015e98 addu     $at, $at, $a0
80015e9c sh       $a1, -0x3370($at)
80015ea0 lw       $a0, 0x18($fp)
80015ea4 nop      
80015ea8 move     $a2, $a0
80015eac sll      $a1, $a2, 3
80015eb0 addu     $a1, $a1, $a0
80015eb4 sll      $a0, $a1, 2
80015eb8 lui      $a1, 0x8014
80015ebc lhu      $a1, 0x3fca($a1)
80015ec0 lui      $at, 0x800e
80015ec4 addu     $at, $at, $a0
80015ec8 sh       $a1, -0x336e($at)
80015ecc lw       $a0, 0x18($fp)
80015ed0 nop      
80015ed4 move     $a2, $a0
80015ed8 sll      $a1, $a2, 3
80015edc addu     $a1, $a1, $a0
80015ee0 sll      $a0, $a1, 2
80015ee4 addiu    $a1, $zero, 0x80
80015ee8 lui      $at, 0x800e
80015eec addu     $at, $at, $a0
80015ef0 sb       $a1, -0x336c($at)
80015ef4 lw       $a0, 0x18($fp)
80015ef8 nop      
80015efc move     $a2, $a0
80015f00 sll      $a1, $a2, 3
80015f04 addu     $a1, $a1, $a0
80015f08 sll      $a0, $a1, 2
80015f0c addiu    $a1, $zero, 0x80
80015f10 lui      $at, 0x800e
80015f14 addu     $at, $at, $a0
80015f18 sb       $a1, -0x336b($at)
80015f1c lw       $a0, 0x18($fp)
80015f20 nop      
80015f24 move     $a2, $a0
80015f28 sll      $a1, $a2, 3
80015f2c addu     $a1, $a1, $a0
80015f30 sll      $a0, $a1, 2
80015f34 addiu    $a1, $zero, 0x80
80015f38 lui      $at, 0x800e
80015f3c addu     $at, $at, $a0
80015f40 sb       $a1, -0x336a($at)
80015f44 lw       $a0, 0x18($fp)
80015f48 nop      
80015f4c move     $a2, $a0
80015f50 sll      $a1, $a2, 3
80015f54 addu     $a1, $a1, $a0
80015f58 sll      $a0, $a1, 2
80015f5c lui      $at, 0x800e
80015f60 addu     $at, $at, $a0
80015f64 sw       $zero, -0x3360($at)
80015f68 lw       $a0, 0x18($fp)
80015f6c nop      
80015f70 move     $a2, $a0
80015f74 sll      $a1, $a2, 3
80015f78 addu     $a1, $a1, $a0
80015f7c sll      $a0, $a1, 2
80015f80 addiu    $a1, $zero, 0x1000
80015f84 lui      $at, 0x800e
80015f88 addu     $at, $at, $a0
80015f8c sh       $a1, -0x3364($at)
80015f90 lw       $a0, 0x18($fp)
80015f94 nop      
80015f98 move     $a2, $a0
80015f9c sll      $a1, $a2, 3
80015fa0 addu     $a1, $a1, $a0
80015fa4 sll      $a0, $a1, 2
80015fa8 addiu    $a1, $zero, 0x1000
80015fac lui      $at, 0x800e
80015fb0 addu     $at, $at, $a0
80015fb4 sh       $a1, -0x3362($at)
80015fb8 move     $sp, $fp
80015fbc lw       $fp, 8($sp)
80015fc0 addiu    $sp, $sp, 0x10
80015fc4 jr       $ra
80015fc8 nop      
80015fcc addiu    $sp, $sp, -0x10
80015fd0 sw       $fp, 8($sp)
80015fd4 move     $fp, $sp
80015fd8 move     $v0, $a0
80015fdc move     $v1, $a1
80015fe0 sw       $a2, 0x18($fp)
80015fe4 sh       $v0, ($fp)
80015fe8 sh       $v1, 2($fp)
80015fec lw       $a0, 0x18($fp)
80015ff0 nop      
80015ff4 move     $a2, $a0
80015ff8 sll      $a1, $a2, 3
80015ffc addu     $a1, $a1, $a0
80016000 sll      $a0, $a1, 2
80016004 lui      $at, 0x800e
80016008 addu     $at, $at, $a0
8001600c sw       $zero, -0xf60($at)
80016010 lw       $a0, 0x18($fp)
80016014 nop      
80016018 move     $a2, $a0
8001601c sll      $a1, $a2, 3
80016020 addu     $a1, $a1, $a0
80016024 sll      $a0, $a1, 2
80016028 addiu    $a1, $zero, 0xc
8001602c lui      $at, 0x800e
80016030 addu     $at, $at, $a0
80016034 sh       $a1, -0xf58($at)
80016038 lw       $a0, 0x18($fp)
8001603c nop      
80016040 move     $a2, $a0
80016044 sll      $a1, $a2, 3
80016048 addu     $a1, $a1, $a0
8001604c sll      $a0, $a1, 2
80016050 addiu    $a1, $zero, 0xf
80016054 lui      $at, 0x800e
80016058 addu     $at, $at, $a0
8001605c sh       $a1, -0xf56($at)
80016060 lw       $a0, 0x18($fp)
80016064 nop      
80016068 move     $a2, $a0
8001606c sll      $a1, $a2, 3
80016070 addu     $a1, $a1, $a0
80016074 sll      $a0, $a1, 2
80016078 lhu      $a1, ($fp)
8001607c lui      $at, 0x800e
80016080 addu     $at, $at, $a0
80016084 sh       $a1, -0xf5c($at)
80016088 lw       $a0, 0x18($fp)
8001608c nop      
80016090 move     $a2, $a0
80016094 sll      $a1, $a2, 3
80016098 addu     $a1, $a1, $a0
8001609c sll      $a0, $a1, 2
800160a0 lhu      $a1, 2($fp)
800160a4 lui      $at, 0x800e
800160a8 addu     $at, $at, $a0
800160ac sh       $a1, -0xf5a($at)
800160b0 lw       $a0, 0x18($fp)
800160b4 nop      
800160b8 move     $a2, $a0
800160bc sll      $a1, $a2, 3
800160c0 addu     $a1, $a1, $a0
800160c4 sll      $a0, $a1, 2
800160c8 lui      $at, 0x800e
800160cc addu     $at, $at, $a0
800160d0 sh       $zero, -0xf48($at)
800160d4 lw       $a0, 0x18($fp)
800160d8 nop      
800160dc move     $a2, $a0
800160e0 sll      $a1, $a2, 3
800160e4 addu     $a1, $a1, $a0
800160e8 sll      $a0, $a1, 2
800160ec lui      $at, 0x800e
800160f0 addu     $at, $at, $a0
800160f4 sh       $zero, -0xf46($at)
800160f8 lw       $a0, 0x18($fp)
800160fc nop      
80016100 move     $a2, $a0
80016104 sll      $a1, $a2, 3
80016108 addu     $a1, $a1, $a0
8001610c sll      $a0, $a1, 2
80016110 lui      $a1, 0x8014
80016114 lhu      $a1, 0x3fc4($a1)
80016118 lui      $at, 0x800e
8001611c addu     $at, $at, $a0
80016120 sh       $a1, -0xf54($at)
80016124 lw       $a0, 0x18($fp)
80016128 nop      
8001612c move     $a2, $a0
80016130 sll      $a1, $a2, 3
80016134 addu     $a1, $a1, $a0
80016138 sll      $a0, $a1, 2
8001613c lui      $a1, 0x8014
80016140 lbu      $a1, 0x3fc6($a1)
80016144 lui      $at, 0x800e
80016148 addu     $at, $at, $a0
8001614c sb       $a1, -0xf52($at)
80016150 lw       $a0, 0x18($fp)
80016154 nop      
80016158 move     $a2, $a0
8001615c sll      $a1, $a2, 3
80016160 addu     $a1, $a1, $a0
80016164 sll      $a0, $a1, 2
80016168 lui      $a1, 0x8014
8001616c lbu      $a1, 0x3fc7($a1)
80016170 lui      $at, 0x800e
80016174 addu     $at, $at, $a0
80016178 sb       $a1, -0xf51($at)
8001617c lw       $a0, 0x18($fp)
80016180 nop      
80016184 move     $a2, $a0
80016188 sll      $a1, $a2, 3
8001618c addu     $a1, $a1, $a0
80016190 sll      $a0, $a1, 2
80016194 lui      $a1, 0x8014
80016198 lhu      $a1, 0x3fc8($a1)
8001619c lui      $at, 0x800e
800161a0 addu     $at, $at, $a0
800161a4 sh       $a1, -0xf50($at)
800161a8 lw       $a0, 0x18($fp)
800161ac nop      
800161b0 move     $a2, $a0
800161b4 sll      $a1, $a2, 3
800161b8 addu     $a1, $a1, $a0
800161bc sll      $a0, $a1, 2
800161c0 lui      $a1, 0x8014
800161c4 lhu      $a1, 0x3fca($a1)
800161c8 lui      $at, 0x800e
800161cc addu     $at, $at, $a0
800161d0 sh       $a1, -0xf4e($at)
800161d4 lw       $a0, 0x18($fp)
800161d8 nop      
800161dc move     $a2, $a0
800161e0 sll      $a1, $a2, 3
800161e4 addu     $a1, $a1, $a0
800161e8 sll      $a0, $a1, 2
800161ec addiu    $a1, $zero, 0x80
800161f0 lui      $at, 0x800e
800161f4 addu     $at, $at, $a0
800161f8 sb       $a1, -0xf4c($at)
800161fc lw       $a0, 0x18($fp)
80016200 nop      
80016204 move     $a2, $a0
80016208 sll      $a1, $a2, 3
8001620c addu     $a1, $a1, $a0
80016210 sll      $a0, $a1, 2
80016214 addiu    $a1, $zero, 0x80
80016218 lui      $at, 0x800e
8001621c addu     $at, $at, $a0
80016220 sb       $a1, -0xf4b($at)
80016224 lw       $a0, 0x18($fp)
80016228 nop      
8001622c move     $a2, $a0
80016230 sll      $a1, $a2, 3
80016234 addu     $a1, $a1, $a0
80016238 sll      $a0, $a1, 2
8001623c addiu    $a1, $zero, 0x80
80016240 lui      $at, 0x800e
80016244 addu     $at, $at, $a0
80016248 sb       $a1, -0xf4a($at)
8001624c lw       $a0, 0x18($fp)
80016250 nop      
80016254 move     $a2, $a0
80016258 sll      $a1, $a2, 3
8001625c addu     $a1, $a1, $a0
80016260 sll      $a0, $a1, 2
80016264 lui      $at, 0x800e
80016268 addu     $at, $at, $a0
8001626c sw       $zero, -0xf40($at)
80016270 lw       $a0, 0x18($fp)
80016274 nop      
80016278 move     $a2, $a0
8001627c sll      $a1, $a2, 3
80016280 addu     $a1, $a1, $a0
80016284 sll      $a0, $a1, 2
80016288 addiu    $a1, $zero, 0x1000
8001628c lui      $at, 0x800e
80016290 addu     $at, $at, $a0
80016294 sh       $a1, -0xf44($at)
80016298 lw       $a0, 0x18($fp)
8001629c nop      
800162a0 move     $a2, $a0
800162a4 sll      $a1, $a2, 3
800162a8 addu     $a1, $a1, $a0
800162ac sll      $a0, $a1, 2
800162b0 addiu    $a1, $zero, 0x1000
800162b4 lui      $at, 0x800e
800162b8 addu     $at, $at, $a0
800162bc sh       $a1, -0xf42($at)
800162c0 move     $sp, $fp
800162c4 lw       $fp, 8($sp)
800162c8 addiu    $sp, $sp, 0x10
800162cc jr       $ra
800162d0 nop      
800162d4 addiu    $sp, $sp, -0x10
800162d8 sw       $fp, 8($sp)
800162dc move     $fp, $sp
800162e0 sw       $a0, 0x10($fp)
800162e4 sw       $a1, 0x14($fp)
800162e8 move     $v0, $a2
800162ec move     $v1, $a3
800162f0 sh       $v0, ($fp)
800162f4 sh       $v1, 2($fp)
800162f8 lhu      $a0, 0x220($gp)
800162fc nop      
80016300 andi     $a1, $a0, 1
80016304 sll      $a2, $a1, 0x10
80016308 sra      $a0, $a2, 0x10
8001630c beqz     $a0, 0x80016358
80016310 nop      
80016314 lw       $a0, 0x14($fp)
80016318 lw       $a1, 0x14($fp)
8001631c nop      
80016320 lhu      $a2, ($a1)
80016324 nop      
80016328 addiu    $a1, $a2, 0x10
8001632c sh       $a1, ($a0)
80016330 lw       $a0, 0x10($fp)
80016334 lhu      $a1, ($fp)
80016338 nop      
8001633c sh       $a1, ($a0)
80016340 lhu      $a0, 0x220($gp)
80016344 addiu    $a1, $zero, -2
80016348 and      $a0, $a0, $a1
8001634c sh       $a0, 0x220($gp)
80016350 j        0x80016464
80016354 nop      
80016358 lhu      $a0, 2($fp)
8001635c nop      
80016360 andi     $a1, $a0, 0x4000
80016364 sll      $a2, $a1, 0x10
80016368 sra      $a0, $a2, 0x10
8001636c beqz     $a0, 0x8001637c
80016370 nop      
80016374 j        0x80016464
80016378 nop      
8001637c lh       $a0, 2($fp)
80016380 nop      
80016384 slti     $a1, $a0, 0x3f
80016388 beqz     $a1, 0x80016448
8001638c nop      
80016390 lui      $a0, 0x800d
80016394 lh       $a0, -0x2708($a0)
80016398 addiu    $a1, $zero, 1
8001639c beq      $a0, $a1, 0x800163f8
800163a0 nop      
800163a4 slti     $a1, $a0, 2
800163a8 beqz     $a1, 0x800163c0
800163ac nop      
800163b0 beqz     $a0, 0x800163d4
800163b4 nop      
800163b8 j        0x80016440
800163bc nop      
800163c0 addiu    $a1, $zero, 2
800163c4 beq      $a0, $a1, 0x8001641c
800163c8 nop      
800163cc j        0x80016440
800163d0 nop      
800163d4 lw       $a0, 0x10($fp)
800163d8 lw       $a1, 0x10($fp)
800163dc nop      
800163e0 lhu      $a2, ($a1)
800163e4 nop      
800163e8 addiu    $a1, $a2, 8
800163ec sh       $a1, ($a0)
800163f0 j        0x80016440
800163f4 nop      
800163f8 lw       $a0, 0x10($fp)
800163fc lw       $a1, 0x10($fp)
80016400 nop      
80016404 lhu      $a2, ($a1)
80016408 nop      
8001640c addiu    $a1, $a2, 0xc
80016410 sh       $a1, ($a0)
80016414 j        0x80016440
80016418 nop      
8001641c lw       $a0, 0x10($fp)
80016420 lw       $a1, 0x10($fp)
80016424 nop      
80016428 lhu      $a2, ($a1)
8001642c nop      
80016430 addiu    $a1, $a2, 0xe
80016434 sh       $a1, ($a0)
80016438 j        0x80016440
8001643c nop      
80016440 j        0x80016464
80016444 nop      
80016448 lw       $a0, 0x10($fp)
8001644c lw       $a1, 0x10($fp)
80016450 nop      
80016454 lhu      $a2, ($a1)
80016458 nop      
8001645c addiu    $a1, $a2, 0xc
80016460 sh       $a1, ($a0)
80016464 move     $sp, $fp
80016468 lw       $fp, 8($sp)
8001646c addiu    $sp, $sp, 0x10
80016470 jr       $ra
80016474 nop      
80016478 addiu    $sp, $sp, -0x20
8001647c sw       $ra, 0x1c($sp)
80016480 sw       $fp, 0x18($sp)
80016484 move     $fp, $sp
80016488 sw       $zero, 0x14($fp)
8001648c j        0x8001649c
80016490 nop      
80016494 j        0x80016568
80016498 nop      
8001649c lui      $v0, 0x800d
800164a0 lw       $v0, -0x2878($v0)
800164a4 nop      
800164a8 addiu    $v1, $v0, 2
800164ac lui      $at, 0x800d
800164b0 sw       $v1, -0x2878($at)
800164b4 lhu      $v0, ($v0)
800164b8 nop      
800164bc sh       $v0, 0x10($fp)
800164c0 lhu      $v0, 0x10($fp)
800164c4 nop      
800164c8 andi     $v1, $v0, 0x4000
800164cc sll      $a0, $v1, 0x10
800164d0 sra      $v0, $a0, 0x10
800164d4 beqz     $v0, 0x800164fc
800164d8 nop      
800164dc lh       $v0, 0x10($fp)
800164e0 nop      
800164e4 move     $a0, $v0
800164e8 jal      0x80016580
800164ec nop      
800164f0 sw       $v0, 0x14($fp)
800164f4 j        0x80016548
800164f8 nop      
800164fc lui      $v0, 0x800d
80016500 lw       $v0, -0x2880($v0)
80016504 nop      
80016508 move     $v1, $v0
8001650c sll      $v0, $v1, 1
80016510 lui      $v1, 0x8013
80016514 addiu    $v1, $v1, -0x55c0
80016518 addu     $v0, $v0, $v1
8001651c move     $v1, $v0
80016520 lhu      $v0, 0x10($fp)
80016524 nop      
80016528 sh       $v0, ($v1)
8001652c lui      $v1, 0x800d
80016530 lw       $v1, -0x2880($v1)
80016534 nop      
80016538 addiu    $v0, $v1, 1
8001653c move     $v1, $v0
80016540 lui      $at, 0x800d
80016544 sw       $v1, -0x2880($at)
80016548 lw       $v0, 0x14($fp)
8001654c nop      
80016550 beqz     $v0, 0x80016560
80016554 nop      
80016558 j        0x80016568
8001655c nop      
80016560 j        0x8001648c
80016564 nop      
80016568 move     $sp, $fp
8001656c lw       $ra, 0x1c($sp)
80016570 lw       $fp, 0x18($sp)
80016574 addiu    $sp, $sp, 0x20
80016578 jr       $ra
8001657c nop      
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
