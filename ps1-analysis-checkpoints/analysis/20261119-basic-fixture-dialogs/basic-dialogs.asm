8004594c: addiu $sp, $sp, -0x58
80045950: sw $ra, 0x50($sp)
80045954: sw $fp, 0x4c($sp)
80045958: sw $s0, 0x48($sp)
8004595c: move $fp, $sp
80045960: sw $a0, 0x58($fp)
80045964: move $s0, $a1
80045968: sb $s0, 0x10($fp)
8004596c: addiu $v0, $zero, 0x40
80045970: sh $v0, 0x40($fp)
80045974: addiu $a0, $zero, 4
80045978: addiu $a1, $zero, 1
8004597c: jal 0x80018940
80045980: nop
80045984: lhu $v0, 0x40($fp)
80045988: nop
8004598c: sh $v0, 0x18($fp)
80045990: addiu $v0, $zero, 0x30
80045994: sh $v0, 0x1a($fp)
80045998: addiu $v0, $zero, 0xc
8004599c: sh $v0, 0x1c($fp)
800459a0: addiu $v0, $zero, 7
800459a4: sh $v0, 0x1e($fp)
800459a8: sb $zero, 0x20($fp)
800459ac: lhu $a0, 0x18($fp)
800459b0: nop
800459b4: andi $v1, $a0, 0xffff
800459b8: lui $a0, 0xffff
800459bc: and $v0, $v0, $a0
800459c0: or $v0, $v0, $v1
800459c4: lhu $v1, 0x1a($fp)
800459c8: nop
800459cc: sll $a0, $v1, 0x10
800459d0: andi $v0, $v0, 0xffff
800459d4: or $v0, $v0, $a0
800459d8: lhu $a1, 0x1c($fp)
800459dc: nop
800459e0: andi $a0, $a1, 0xffff
800459e4: lui $a1, 0xffff
800459e8: and $v1, $v1, $a1
800459ec: or $v1, $v1, $a0
800459f0: lhu $a0, 0x1e($fp)
800459f4: nop
800459f8: sll $a1, $a0, 0x10
800459fc: andi $v1, $v1, 0xffff
80045a00: or $v1, $v1, $a1
80045a04: lhu $a1, 0x20($fp)
80045a08: nop
80045a0c: andi $a0, $a1, 0xffff
80045a10: lui $a1, 0xffff
80045a14: and $a2, $a2, $a1
80045a18: or $a2, $a2, $a0
80045a1c: move $a0, $v0
80045a20: move $a1, $v1
80045a24: jal 0x80017b18
80045a28: nop
80045a2c: addiu $a0, $zero, 0x80e
80045a30: addiu $a1, $zero, 1
80045a34: jal 0x80018940
80045a38: nop
80045a3c: jal 0x800419e0
80045a40: nop
80045a44: move $a0, $zero
80045a48: move $a1, $zero
80045a4c: jal 0x80045eec
80045a50: nop
80045a54: addiu $a0, $zero, 0x28
80045a58: addiu $a1, $zero, 1
80045a5c: jal 0x80045eec
80045a60: nop
80045a64: lhu $v0, 0x40($fp)
80045a68: nop
80045a6c: addiu $v1, $v0, 0x4c
80045a70: sll $a0, $v1, 0x10
80045a74: sra $v0, $a0, 0x10
80045a78: move $a0, $v0
80045a7c: addiu $a1, $zero, 0x8c
80045a80: jal 0x8004e938
80045a84: nop
80045a88: sw $zero, 0x34($fp)
80045a8c: sw $zero, 0x30($fp)
80045a90: lui $v0, 0x800e
80045a94: lhu $v0, -0x519a($v0)
80045a98: nop
80045a9c: addiu $v1, $v0, -2
80045aa0: lui $at, 0x800e
80045aa4: sh $v1, -0x519a($at)
80045aa8: j 0x80045ab8
80045aac: nop
80045ab0: j 0x80045ec4
80045ab4: nop
80045ab8: jal 0x800157b4
80045abc: nop
80045ac0: addiu $v0, $zero, 0x21
80045ac4: sh $v0, 0x28($fp)
80045ac8: lhu $v0, 0x40($fp)
80045acc: nop
80045ad0: addiu $v1, $v0, 0x10
80045ad4: sh $v1, 0x2a($fp)
80045ad8: addiu $v0, $zero, 0x40
80045adc: sh $v0, 0x2c($fp)
80045ae0: lhu $a0, 0x28($fp)
80045ae4: nop
80045ae8: andi $v1, $a0, 0xffff
80045aec: lui $a0, 0xffff
80045af0: and $v0, $v0, $a0
80045af4: or $v0, $v0, $v1
80045af8: lhu $v1, 0x2a($fp)
80045afc: nop
80045b00: sll $a0, $v1, 0x10
80045b04: andi $v0, $v0, 0xffff
80045b08: or $v0, $v0, $a0
80045b0c: lhu $a1, 0x2c($fp)
80045b10: nop
80045b14: andi $a0, $a1, 0xffff
80045b18: lui $a1, 0xffff
80045b1c: and $v1, $v1, $a1
80045b20: or $v1, $v1, $a0
80045b24: lhu $a0, 0x2e($fp)
80045b28: nop
80045b2c: sll $a1, $a0, 0x10
80045b30: andi $v1, $v1, 0xffff
80045b34: or $v1, $v1, $a1
80045b38: move $a0, $v0
80045b3c: move $a1, $v1
80045b40: jal 0x800155d0
80045b44: nop
80045b48: lhu $v0, 0x40($fp)
80045b4c: nop
80045b50: addiu $v1, $v0, 0x10
80045b54: sll $a0, $v1, 0x10
80045b58: sra $v0, $a0, 0x10
80045b5c: move $a0, $v0
80045b60: addiu $a1, $zero, 0x50
80045b64: lui $a2, 0x800c
80045b68: addiu $a2, $a2, -0x6b74
80045b6c: jal 0x80067338
80045b70: nop
80045b74: lw $v1, 0x30($fp)
80045b78: nop
80045b7c: addiu $v0, $v1, 0x30
80045b80: move $a0, $v0
80045b84: sll $v1, $a0, 1
80045b88: addu $v1, $v1, $v0
80045b8c: sll $a0, $v1, 4
80045b90: addu $a0, $a0, $v0
80045b94: sll $v0, $a0, 2
80045b98: lui $at, 0x800a
80045b9c: addu $at, $at, $v0
80045ba0: lw $v1, -0x60f0($at)
80045ba4: lui $at, 0x800e
80045ba8: sw $v1, 0x4004($at)
80045bac: lui $a0, 0x800e
80045bb0: lw $a0, 0x4004($a0)
80045bb4: jal 0x80065820
80045bb8: nop
80045bbc: addiu $v1, $zero, 6
80045bc0: subu $v0, $v1, $v0
80045bc4: move $v1, $v0
80045bc8: sll $v0, $v1, 3
80045bcc: sw $v0, 0x3c($fp)
80045bd0: lhu $v0, 0x3c($fp)
80045bd4: lhu $v1, 0x40($fp)
80045bd8: nop
80045bdc: addu $v0, $v0, $v1
80045be0: move $v1, $v0
80045be4: addiu $v0, $v1, 0x40
80045be8: sll $v1, $v0, 0x10
80045bec: sra $v0, $v1, 0x10
80045bf0: move $a0, $v0
80045bf4: addiu $a1, $zero, 0x50
80045bf8: addiu $a2, $zero, 0x1c
80045bfc: jal 0x8004e494
80045c00: nop
80045c04: lhu $v0, 0x40($fp)
80045c08: nop
80045c0c: addiu $v1, $v0, 0x10
80045c10: sll $a0, $v1, 0x10
80045c14: sra $v0, $a0, 0x10
80045c18: move $a0, $v0
80045c1c: addiu $a1, $zero, 0x60
80045c20: lui $a2, 0x800c
80045c24: addiu $a2, $a2, -0x6b7c
80045c28: jal 0x80067338
80045c2c: nop
80045c30: lw $v1, 0x30($fp)
80045c34: nop
80045c38: addiu $v0, $v1, 0x30
80045c3c: move $a0, $v0
80045c40: sll $v1, $a0, 1
80045c44: addu $v1, $v1, $v0
80045c48: sll $a0, $v1, 4
80045c4c: addu $a0, $a0, $v0
80045c50: sll $v1, $a0, 2
80045c54: lui $at, 0x800a
80045c58: addu $at, $at, $v1
80045c5c: lw $v0, -0x60ec($at)
80045c60: nop
80045c64: move $a0, $v0
80045c68: sll $v1, $a0, 1
80045c6c: addu $v1, $v1, $v0
80045c70: sll $v0, $v1, 3
80045c74: lui $at, 0x800e
80045c78: sw $v0, 0x4000($at)
80045c7c: lui $a0, 0x800e
80045c80: lw $a0, 0x4000($a0)
80045c84: jal 0x80065820
80045c88: nop
80045c8c: addiu $v1, $zero, 6
80045c90: subu $v0, $v1, $v0
80045c94: move $v1, $v0
80045c98: sll $v0, $v1, 3
80045c9c: sw $v0, 0x3c($fp)
80045ca0: lhu $v0, 0x3c($fp)
80045ca4: lhu $v1, 0x40($fp)
80045ca8: nop
80045cac: addu $v0, $v0, $v1
80045cb0: move $v1, $v0
80045cb4: addiu $v0, $v1, 0x40
80045cb8: sll $v1, $v0, 0x10
80045cbc: sra $v0, $v1, 0x10
80045cc0: move $a0, $v0
80045cc4: addiu $a1, $zero, 0x60
80045cc8: addiu $a2, $zero, 0x128
80045ccc: jal 0x8004e494
80045cd0: nop
80045cd4: lw $v0, 0x34($fp)
80045cd8: lw $v1, 0x30($fp)
80045cdc: nop
80045ce0: beq $v0, $v1, 0x80045d94
80045ce4: nop
80045ce8: lw $v0, 0x34($fp)
80045cec: nop
80045cf0: move $a0, $v0
80045cf4: sll $v1, $a0, 3
80045cf8: addu $v1, $v1, $v0
80045cfc: sll $v0, $v1, 2
80045d00: lw $v1, 0x34($fp)
80045d04: nop
80045d08: move $a1, $v1
80045d0c: sll $a0, $a1, 3
80045d10: addu $a0, $a0, $v1
80045d14: sll $v1, $a0, 2
80045d18: lui $at, 0x800e
80045d1c: addu $at, $at, $v1
80045d20: lhu $a0, -0x519a($at)
80045d24: nop
80045d28: addiu $v1, $a0, 2
80045d2c: lui $at, 0x800e
80045d30: addu $at, $at, $v0
80045d34: sh $v1, -0x519a($at)
80045d38: lw $v0, 0x30($fp)
80045d3c: nop
80045d40: sw $v0, 0x34($fp)
80045d44: lw $v0, 0x34($fp)
80045d48: nop
80045d4c: move $a0, $v0
80045d50: sll $v1, $a0, 3
80045d54: addu $v1, $v1, $v0
80045d58: sll $v0, $v1, 2
80045d5c: lw $v1, 0x34($fp)
80045d60: nop
80045d64: move $a1, $v1
80045d68: sll $a0, $a1, 3
80045d6c: addu $a0, $a0, $v1
80045d70: sll $v1, $a0, 2
80045d74: lui $at, 0x800e
80045d78: addu $at, $at, $v1
80045d7c: lhu $a0, -0x519a($at)
80045d80: nop
80045d84: addiu $v1, $a0, -2
80045d88: lui $at, 0x800e
80045d8c: addu $at, $at, $v0
80045d90: sh $v1, -0x519a($at)
80045d94: move $a0, $zero
80045d98: jal 0x80041374
80045d9c: nop
80045da0: lui $v1, 0x800d
80045da4: lw $v1, -0x25f4($v1)
80045da8: nop
80045dac: andi $v0, $v1, 0x2000
80045db0: beqz $v0, 0x80045df4
80045db4: nop
80045db8: lw $v0, 0x30($fp)
80045dbc: nop
80045dc0: bnez $v0, 0x80045df4
80045dc4: nop
80045dc8: lw $v1, 0x30($fp)
80045dcc: nop
80045dd0: addiu $v0, $v1, 1
80045dd4: move $v1, $v0
80045dd8: sw $v1, 0x30($fp)
80045ddc: lui $v0, 0x800e
80045de0: lhu $v0, -0x51c4($v0)
80045de4: nop
80045de8: addiu $v1, $v0, 0x28
80045dec: lui $at, 0x800e
80045df0: sh $v1, -0x51c4($at)
80045df4: lui $v1, 0x800d
80045df8: lw $v1, -0x25f4($v1)
80045dfc: nop
80045e00: andi $v0, $v1, 0x8000
80045e04: beqz $v0, 0x80045e48
80045e08: nop
80045e0c: lw $v0, 0x30($fp)
80045e10: addiu $v1, $zero, 1
80045e14: bne $v0, $v1, 0x80045e48
80045e18: nop
80045e1c: lw $v1, 0x30($fp)
80045e20: nop
80045e24: addiu $v0, $v1, -1
80045e28: move $v1, $v0
80045e2c: sw $v1, 0x30($fp)
80045e30: lui $v0, 0x800e
80045e34: lhu $v0, -0x51c4($v0)
80045e38: nop
80045e3c: addiu $v1, $v0, -0x28
80045e40: lui $at, 0x800e
80045e44: sh $v1, -0x51c4($at)
80045e48: lui $v1, 0x800d
80045e4c: lw $v1, -0x25d8($v1)
80045e50: nop
80045e54: andi $v0, $v1, 0x20
80045e58: beqz $v0, 0x80045e7c
80045e5c: nop
80045e60: lw $v0, 0x30($fp)
80045e64: nop
80045e68: sw $v0, 0x38($fp)
80045e6c: jal 0x80065000
80045e70: nop
80045e74: j 0x80045ec4
80045e78: nop
80045e7c: lb $v0, 0x10($fp)
80045e80: nop
80045e84: beqz $v0, 0x80045ebc
80045e88: nop
80045e8c: lui $v1, 0x800d
80045e90: lw $v1, -0x25d8($v1)
80045e94: nop
80045e98: andi $v0, $v1, 0x40
80045e9c: beqz $v0, 0x80045ebc
80045ea0: nop
80045ea4: addiu $v0, $zero, -1
80045ea8: sw $v0, 0x38($fp)
80045eac: jal 0x80065040
80045eb0: nop
80045eb4: j 0x80045ec4
80045eb8: nop
80045ebc: j 0x80045aa8
80045ec0: nop
80045ec4: lw $v0, 0x38($fp)
80045ec8: j 0x80045ed0
80045ecc: nop
80045ed0: move $sp, $fp
80045ed4: lw $ra, 0x50($sp)
80045ed8: lw $fp, 0x4c($sp)
80045edc: lw $s0, 0x48($sp)
80045ee0: addiu $sp, $sp, 0x58
80045ee4: jr $ra
80045ee8: nop
80045eec: addiu $sp, $sp, -0x78
80045ef0: sw $ra, 0x74($sp)
80045ef4: sw $fp, 0x70($sp)
80045ef8: sw $s1, 0x6c($sp)
80045efc: sw $s0, 0x68($sp)
80045f00: move $fp, $sp
80045f04: move $s0, $a0
80045f08: move $s1, $a1
80045f0c: sh $s0, 0x30($fp)
80045f10: sh $s1, 0x32($fp)
80045f14: addiu $v0, $zero, 0x40
80045f18: sh $v0, 0x60($fp)
80045f1c: addiu $v0, $zero, 0x20
80045f20: sh $v0, 0x42($fp)
80045f24: addiu $v0, $zero, 0x20
80045f28: sh $v0, 0x40($fp)
80045f2c: lhu $v0, 0x30($fp)
80045f30: nop
80045f34: addiu $v1, $v0, -0x70
80045f38: lhu $v0, 0x60($fp)
80045f3c: nop
80045f40: addu $v0, $v0, $v1
80045f44: sh $v0, 0x3c($fp)
80045f48: sh $zero, 0x3e($fp)
80045f4c: addiu $v0, $zero, 0x19
80045f50: sh $v0, 0x44($fp)
80045f54: lh $v0, 0x32($fp)
80045f58: nop
80045f5c: move $v1, $v0
80045f60: sll $v0, $v1, 5
80045f64: move $v1, $v0
80045f68: addiu $v0, $v1, 0x60
80045f6c: sb $v0, 0x46($fp)
80045f70: addiu $v0, $zero, 0xc0
80045f74: sb $v0, 0x47($fp)
80045f78: sh $zero, 0x48($fp)
80045f7c: addiu $v0, $zero, 0x1eb
80045f80: sh $v0, 0x4a($fp)
80045f84: lh $v0, 0x32($fp)
80045f88: sw $zero, 0x28($sp)
80045f8c: addiu $v1, $sp, 0x10
80045f90: addiu $a0, $fp, 0x44
80045f94: lw $t1, ($a0)
80045f98: lw $t2, 4($a0)
80045f9c: lw $t3, 8($a0)
80045fa0: lw $t0, 0xc($a0)
80045fa4: sw $t1, ($v1)
80045fa8: sw $t2, 4($v1)
80045fac: sw $t3, 8($v1)
80045fb0: sw $t0, 0xc($v1)
80045fb4: lw $t1, 0x10($a0)
80045fb8: lw $t2, 0x14($a0)
80045fbc: sw $t1, 0x10($v1)
80045fc0: sw $t2, 0x14($v1)
80045fc4: lw $a1, 0x38($fp)
80045fc8: lw $a2, 0x3c($fp)
80045fcc: lw $a3, 0x40($fp)
80045fd0: move $a0, $v0
80045fd4: jal 0x80041630
80045fd8: nop
80045fdc: move $sp, $fp
80045fe0: lw $ra, 0x74($sp)
80045fe4: lw $fp, 0x70($sp)
80045fe8: lw $s1, 0x6c($sp)
80045fec: lw $s0, 0x68($sp)
80045ff0: addiu $sp, $sp, 0x78
80045ff4: jr $ra
80045ff8: nop
8006966c: addiu $sp, $sp, -0x40
80069670: sw $ra, 0x3c($sp)
80069674: sw $fp, 0x38($sp)
80069678: move $fp, $sp
8006967c: sw $zero, 0x18($fp)
80069680: sw $zero, 0x1c($fp)
80069684: j 0x80069694
80069688: nop
8006968c: j 0x80069b90
80069690: nop
80069694: jal 0x80065974
80069698: nop
8006969c: addiu $v0, $zero, 0x28
800696a0: sh $v0, 0x28($fp)
800696a4: addiu $v0, $zero, 0x18
800696a8: sh $v0, 0x2a($fp)
800696ac: addiu $v0, $zero, 0xf
800696b0: sh $v0, 0x2c($fp)
800696b4: addiu $v0, $zero, 7
800696b8: sh $v0, 0x2e($fp)
800696bc: sb $zero, 0x30($fp)
800696c0: lhu $a0, 0x28($fp)
800696c4: nop
800696c8: andi $v1, $a0, 0xffff
800696cc: lui $a0, 0xffff
800696d0: and $v0, $v0, $a0
800696d4: or $v0, $v0, $v1
800696d8: lhu $v1, 0x2a($fp)
800696dc: nop
800696e0: sll $a0, $v1, 0x10
800696e4: andi $v0, $v0, 0xffff
800696e8: or $v0, $v0, $a0
800696ec: lhu $a1, 0x2c($fp)
800696f0: nop
800696f4: andi $a0, $a1, 0xffff
800696f8: lui $a1, 0xffff
800696fc: and $v1, $v1, $a1
80069700: or $v1, $v1, $a0
80069704: lhu $a0, 0x2e($fp)
80069708: nop
8006970c: sll $a1, $a0, 0x10
80069710: andi $v1, $v1, 0xffff
80069714: or $v1, $v1, $a1
80069718: lhu $a1, 0x30($fp)
8006971c: nop
80069720: andi $a0, $a1, 0xffff
80069724: lui $a1, 0xffff
80069728: and $a2, $a2, $a1
8006972c: or $a2, $a2, $a0
80069730: move $a0, $v0
80069734: move $a1, $v1
80069738: jal 0x80017b18
8006973c: nop
80069740: addiu $a0, $zero, 0x58
80069744: addiu $a1, $zero, 0x28
80069748: lui $a2, 0x800c
8006974c: addiu $a2, $a2, -0x6cf8
80069750: jal 0x80067338
80069754: nop
80069758: addiu $a0, $zero, 0x38
8006975c: addiu $a1, $zero, 0x38
80069760: lui $a2, 0x800c
80069764: addiu $a2, $a2, -0x6d24
80069768: jal 0x80067338
8006976c: nop
80069770: lw $v0, 0x1c($fp)
80069774: nop
80069778: move $v1, $v0
8006977c: sll $v0, $v1, 2
80069780: lui $v1, 0x800c
80069784: addiu $v1, $v1, -0x66f0
80069788: addu $v0, $v0, $v1
8006978c: move $v1, $v0
80069790: lw $v0, ($v1)
80069794: nop
80069798: move $a0, $v0
8006979c: sll $v1, $a0, 1
800697a0: addu $v1, $v1, $v0
800697a4: sll $a0, $v1, 4
800697a8: addu $a0, $a0, $v0
800697ac: sll $v0, $a0, 2
800697b0: lui $at, 0x800a
800697b4: addu $at, $at, $v0
800697b8: lw $v1, -0x60e8($at)
800697bc: lui $at, 0x800d
800697c0: sw $v1, -0x26c8($at)
800697c4: addiu $a0, $zero, 0xac
800697c8: addiu $a1, $zero, 0x38
800697cc: addiu $a2, $zero, 0x170
800697d0: jal 0x8004e494
800697d4: nop
800697d8: addiu $a0, $zero, 0x38
800697dc: addiu $a1, $zero, 0x48
800697e0: lui $a2, 0x800c
800697e4: addiu $a2, $a2, -0x6b74
800697e8: jal 0x80067338
800697ec: nop
800697f0: lw $v0, 0x1c($fp)
800697f4: nop
800697f8: move $v1, $v0
800697fc: sll $v0, $v1, 2
80069800: lui $v1, 0x800c
80069804: addiu $v1, $v1, -0x66f0
80069808: addu $v0, $v0, $v1
8006980c: move $v1, $v0
80069810: lw $v0, ($v1)
80069814: nop
80069818: move $a0, $v0
8006981c: sll $v1, $a0, 1
80069820: addu $v1, $v1, $v0
80069824: sll $a0, $v1, 4
80069828: addu $a0, $a0, $v0
8006982c: sll $v0, $a0, 2
80069830: lui $at, 0x800a
80069834: addu $at, $at, $v0
80069838: lw $v1, -0x60f0($at)
8006983c: lui $at, 0x800e
80069840: sw $v1, 0x4004($at)
80069844: lui $a0, 0x800e
80069848: lw $a0, 0x4004($a0)
8006984c: jal 0x80065820
80069850: nop
80069854: addiu $v1, $zero, 6
80069858: subu $v0, $v1, $v0
8006985c: move $v1, $v0
80069860: sll $v0, $v1, 3
80069864: sw $v0, 0x20($fp)
80069868: lw $v1, 0x20($fp)
8006986c: nop
80069870: addiu $v0, $v1, 0x58
80069874: move $a0, $v0
80069878: addiu $a1, $zero, 0x48
8006987c: addiu $a2, $zero, 0x1c
80069880: jal 0x8004e494
80069884: nop
80069888: addiu $a0, $zero, 0x98
8006988c: addiu $a1, $zero, 0x48
80069890: lui $a2, 0x800c
80069894: addiu $a2, $a2, -0x6b7c
80069898: jal 0x80067338
8006989c: nop
800698a0: lw $v0, 0x1c($fp)
800698a4: nop
800698a8: move $v1, $v0
800698ac: sll $v0, $v1, 2
800698b0: lui $v1, 0x800c
800698b4: addiu $v1, $v1, -0x66f0
800698b8: addu $v0, $v0, $v1
800698bc: move $v1, $v0
800698c0: lw $v0, ($v1)
800698c4: nop
800698c8: move $a0, $v0
800698cc: sll $v1, $a0, 1
800698d0: addu $v1, $v1, $v0
800698d4: sll $a0, $v1, 4
800698d8: addu $a0, $a0, $v0
800698dc: sll $v1, $a0, 2
800698e0: lui $at, 0x800a
800698e4: addu $at, $at, $v1
800698e8: lw $v0, -0x60ec($at)
800698ec: nop
800698f0: move $a0, $v0
800698f4: sll $v1, $a0, 1
800698f8: addu $v1, $v1, $v0
800698fc: sll $v0, $v1, 3
80069900: lui $at, 0x800e
80069904: sw $v0, 0x4000($at)
80069908: lui $a0, 0x800e
8006990c: lw $a0, 0x4000($a0)
80069910: jal 0x80065820
80069914: nop
80069918: addiu $v1, $zero, 6
8006991c: subu $v0, $v1, $v0
80069920: move $v1, $v0
80069924: sll $v0, $v1, 3
80069928: sw $v0, 0x20($fp)
8006992c: lw $v1, 0x20($fp)
80069930: nop
80069934: addiu $v0, $v1, 0xc0
80069938: move $a0, $v0
8006993c: addiu $a1, $zero, 0x48
80069940: addiu $a2, $zero, 0x128
80069944: jal 0x8004e494
80069948: nop
8006994c: sw $zero, 0x10($fp)
80069950: lw $v0, 0x10($fp)
80069954: nop
80069958: slti $v1, $v0, 4
8006995c: bnez $v1, 0x8006996c
80069960: nop
80069964: j 0x80069a38
80069968: nop
8006996c: lw $v0, 0x10($fp)
80069970: lui $a0, 0x6666
80069974: ori $a0, $a0, 0x6667
80069978: mult $v0, $a0
8006997c: mfhi $v1
80069980: sra $a0, $v1, 1
80069984: sra $a1, $v0, 0x1f
80069988: subu $v1, $a0, $a1
8006998c: move $a1, $v1
80069990: sll $a0, $a1, 2
80069994: addu $a0, $a0, $v1
80069998: subu $v0, $v0, $a0
8006999c: move $a0, $v0
800699a0: sll $v1, $a0, 2
800699a4: addu $v1, $v1, $v0
800699a8: sll $a0, $v1, 3
800699ac: addiu $v0, $a0, 0x40
800699b0: lw $v1, 0x10($fp)
800699b4: lui $a1, 0x6666
800699b8: ori $a1, $a1, 0x6667
800699bc: mult $v1, $a1
800699c0: mfhi $a0
800699c4: sra $a1, $a0, 1
800699c8: sra $a0, $v1, 0x1f
800699cc: subu $v1, $a1, $a0
800699d0: move $a1, $v1
800699d4: sll $a0, $a1, 2
800699d8: addu $a0, $a0, $v1
800699dc: sll $a1, $a0, 3
800699e0: addiu $v1, $a1, 0x48
800699e4: lw $a0, 0x10($fp)
800699e8: nop
800699ec: move $a1, $a0
800699f0: sll $a0, $a1, 2
800699f4: lui $a1, 0x800c
800699f8: addiu $a1, $a1, -0x66f0
800699fc: addu $a0, $a0, $a1
80069a00: move $a2, $a0
80069a04: move $a0, $v0
80069a08: move $a1, $v1
80069a0c: lw $a2, ($a2)
80069a10: move $a3, $zero
80069a14: jal 0x800687c4
80069a18: nop
80069a1c: lw $v1, 0x10($fp)
80069a20: nop
80069a24: addiu $v0, $v1, 1
80069a28: move $v1, $v0
80069a2c: sw $v1, 0x10($fp)
80069a30: j 0x80069950
80069a34: nop
80069a38: lw $v0, 0x1c($fp)
80069a3c: lui $a0, 0x6666
80069a40: ori $a0, $a0, 0x6667
80069a44: mult $v0, $a0
80069a48: mfhi $v1
80069a4c: sra $a0, $v1, 1
80069a50: sra $a1, $v0, 0x1f
80069a54: subu $v1, $a0, $a1
80069a58: move $a1, $v1
80069a5c: sll $a0, $a1, 2
80069a60: addu $a0, $a0, $v1
80069a64: subu $v0, $v0, $a0
80069a68: move $a0, $v0
80069a6c: sll $v1, $a0, 2
80069a70: addu $v1, $v1, $v0
80069a74: sll $v0, $v1, 3
80069a78: move $v1, $v0
80069a7c: addiu $v0, $v1, 0x64
80069a80: sll $v1, $v0, 0x10
80069a84: sra $v0, $v1, 0x10
80069a88: lw $v1, 0x1c($fp)
80069a8c: lui $a1, 0x6666
80069a90: ori $a1, $a1, 0x6667
80069a94: mult $v1, $a1
80069a98: mfhi $a0
80069a9c: sra $a1, $a0, 1
80069aa0: sra $a0, $v1, 0x1f
80069aa4: subu $v1, $a1, $a0
80069aa8: move $a1, $v1
80069aac: sll $a0, $a1, 2
80069ab0: addu $a0, $a0, $v1
80069ab4: sll $v1, $a0, 3
80069ab8: move $a0, $v1
80069abc: addiu $v1, $a0, 0x6c
80069ac0: sll $a0, $v1, 0x10
80069ac4: sra $v1, $a0, 0x10
80069ac8: move $a0, $v0
80069acc: move $a1, $v1
80069ad0: jal 0x8005fdd4
80069ad4: nop
80069ad8: move $a0, $zero
80069adc: jal 0x80041374
80069ae0: nop
80069ae4: lui $v1, 0x800d
80069ae8: lw $v1, -0x25d8($v1)
80069aec: nop
80069af0: andi $v0, $v1, 0x20
80069af4: beqz $v0, 0x80069b0c
80069af8: nop
80069afc: jal 0x80065000
80069b00: nop
80069b04: j 0x80069b90
80069b08: nop
80069b0c: lui $v1, 0x800d
80069b10: lw $v1, -0x25f4($v1)
80069b14: nop
80069b18: andi $v0, $v1, 0x2000
80069b1c: beqz $v0, 0x80069b4c
80069b20: nop
80069b24: lw $v0, 0x1c($fp)
80069b28: nop
80069b2c: slti $v1, $v0, 3
80069b30: beqz $v1, 0x80069b4c
80069b34: nop
80069b38: lw $v1, 0x1c($fp)
80069b3c: nop
80069b40: addiu $v0, $v1, 1
80069b44: move $v1, $v0
80069b48: sw $v1, 0x1c($fp)
80069b4c: lui $v1, 0x800d
80069b50: lw $v1, -0x25f4($v1)
80069b54: nop
80069b58: andi $v0, $v1, 0x8000
80069b5c: beqz $v0, 0x80069b88
80069b60: nop
80069b64: lw $v0, 0x1c($fp)
80069b68: nop
80069b6c: blez $v0, 0x80069b88
80069b70: nop
80069b74: lw $v1, 0x1c($fp)
80069b78: nop
80069b7c: addiu $v0, $v1, -1
80069b80: move $v1, $v0
80069b84: sw $v1, 0x1c($fp)
80069b88: j 0x80069684
80069b8c: nop
80069b90: jal 0x80065974
80069b94: nop
80069b98: lw $v0, 0x1c($fp)
80069b9c: j 0x80069ba4
80069ba0: nop
80069ba4: move $sp, $fp
80069ba8: lw $ra, 0x3c($sp)
80069bac: lw $fp, 0x38($sp)
80069bb0: addiu $sp, $sp, 0x40
80069bb4: jr $ra
80069bb8: nop
80076bd4: lui $v0, 0x800d
80076bd8: lw $v0, -0x2810($v0)
80076bdc: addiu $v1, $zero, 4
80076be0: bne $v0, $v1, 0x80076c44
80076be4: nop
80076be8: lui $v0, 0x800d
80076bec: lw $v0, -0x25d0($v0)
80076bf0: nop
80076bf4: move $v1, $v0
80076bf8: sll $v0, $v1, 2
80076bfc: lui $v1, 0x800d
80076c00: addiu $v1, $v1, -0x28a0
80076c04: addu $v0, $v0, $v1
80076c08: move $v1, $v0
80076c0c: lw $v0, ($v1)
80076c10: nop
80076c14: move $a0, $v0
80076c18: sll $v1, $a0, 1
80076c1c: addu $v1, $v1, $v0
80076c20: sll $a0, $v1, 4
80076c24: addu $a0, $a0, $v0
80076c28: sll $v0, $a0, 2
80076c2c: lui $v1, 0x800a
80076c30: addiu $v1, $v1, -0x60f4
80076c34: addu $v0, $v1, $v0
80076c38: sw $v0, 0x18($fp)
80076c3c: j 0x80076d1c
80076c40: nop
80076c44: lui $v0, 0x800d
80076c48: lw $v0, -0x2810($v0)
80076c4c: addiu $v1, $zero, 5
80076c50: bne $v0, $v1, 0x80076cb4
80076c54: nop
80076c58: lui $v0, 0x800d
80076c5c: lw $v0, -0x25d0($v0)
80076c60: nop
80076c64: move $v1, $v0
80076c68: sll $v0, $v1, 2
80076c6c: lui $v1, 0x800c
80076c70: addiu $v1, $v1, -0x66f0
80076c74: addu $v0, $v0, $v1
80076c78: move $v1, $v0
80076c7c: lw $v0, ($v1)
80076c80: nop
80076c84: move $a0, $v0
80076c88: sll $v1, $a0, 1
80076c8c: addu $v1, $v1, $v0
80076c90: sll $a0, $v1, 4
80076c94: addu $a0, $a0, $v0
80076c98: sll $v0, $a0, 2
80076c9c: lui $v1, 0x800a
80076ca0: addiu $v1, $v1, -0x60f4
80076ca4: addu $v0, $v1, $v0
80076ca8: sw $v0, 0x18($fp)
80076cac: j 0x80076d1c
80076cb0: nop
80076cb4: lui $v0, 0x800d
80076cb8: lw $v0, -0x2810($v0)
80076cbc: addiu $v1, $zero, 6
80076cc0: bne $v0, $v1, 0x80076d1c
80076cc4: nop
80076cc8: lui $v0, 0x800d
80076ccc: lw $v0, -0x25d0($v0)
80076cd0: nop
80076cd4: move $v1, $v0
80076cd8: sll $v0, $v1, 2
80076cdc: lui $v1, 0x800c
80076ce0: addiu $v1, $v1, -0x66e0
80076ce4: addu $v0, $v0, $v1
80076ce8: move $v1, $v0
80076cec: lw $v0, ($v1)
80076cf0: nop
80076cf4: move $a0, $v0
80076cf8: sll $v1, $a0, 1
80076cfc: addu $v1, $v1, $v0
80076d00: sll $a0, $v1, 4
80076d04: addu $a0, $a0, $v0
80076d08: sll $v0, $a0, 2
80076d0c: lui $v1, 0x800a
80076d10: addiu $v1, $v1, -0x60f4
80076d14: addu $v0, $v1, $v0
80076d18: sw $v0, 0x18($fp)
800b9910: xor $zero, $zero, $zero
800b9914: not $zero, $zero
800b9918: .byte 0x29, 0x00, 0x00, 0x00
800b991c: slt $zero, $zero, $zero
800cd760: tge $zero, $zero
800cd764: tgeu $zero, $zero
