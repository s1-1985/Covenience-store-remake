8005fdd4: addiu $sp, $sp, -0x28
8005fdd8: sw $ra, 0x24($sp)
8005fddc: sw $fp, 0x20($sp)
8005fde0: sw $s1, 0x1c($sp)
8005fde4: sw $s0, 0x18($sp)
8005fde8: move $fp, $sp
8005fdec: move $s0, $a0
8005fdf0: move $s1, $a1
8005fdf4: sh $s0, 0x10($fp)
8005fdf8: sh $s1, 0x12($fp)
8005fdfc: lhu $v0, 0x10($fp)
8005fe00: nop
8005fe04: addiu $v1, $v0, 3
8005fe08: sll $a0, $v1, 0x10
8005fe0c: sra $v0, $a0, 0x10
8005fe10: lhu $v1, 0x12($fp)
8005fe14: nop
8005fe18: addiu $a0, $v1, 3
8005fe1c: sll $a1, $a0, 0x10
8005fe20: sra $v1, $a1, 0x10
8005fe24: move $a0, $v0
8005fe28: move $a1, $v1
8005fe2c: jal 0x8004e938
8005fe30: nop
8005fe34: move $sp, $fp
8005fe38: lw $ra, 0x24($sp)
8005fe3c: lw $fp, 0x20($sp)
8005fe40: lw $s1, 0x1c($sp)
8005fe44: lw $s0, 0x18($sp)
8005fe48: addiu $sp, $sp, 0x28
8005fe4c: jr $ra
8005fe50: nop
80069d30: jal 0x80065974
80069d34: nop
80069d38: addiu $v0, $zero, 0x28
80069d3c: sh $v0, 0x38($fp)
80069d40: addiu $v0, $zero, 0x18
80069d44: sh $v0, 0x3a($fp)
80069d48: addiu $v0, $zero, 0x10
80069d4c: sh $v0, 0x3c($fp)
80069d50: addiu $v0, $zero, 9
80069d54: sh $v0, 0x3e($fp)
80069d58: sb $zero, 0x40($fp)
80069d5c: lhu $a0, 0x38($fp)
80069d60: nop
80069d64: andi $v1, $a0, 0xffff
80069d68: lui $a0, 0xffff
80069d6c: and $v0, $v0, $a0
80069d70: or $v0, $v0, $v1
80069d74: lhu $v1, 0x3a($fp)
80069d78: nop
80069d7c: sll $a0, $v1, 0x10
80069d80: andi $v0, $v0, 0xffff
80069d84: or $v0, $v0, $a0
80069d88: lhu $a1, 0x3c($fp)
80069d8c: nop
80069d90: andi $a0, $a1, 0xffff
80069d94: lui $a1, 0xffff
80069d98: and $v1, $v1, $a1
80069d9c: or $v1, $v1, $a0
80069da0: lhu $a0, 0x3e($fp)
80069da4: nop
80069da8: sll $a1, $a0, 0x10
80069dac: andi $v1, $v1, 0xffff
80069db0: or $v1, $v1, $a1
80069db4: lhu $a1, 0x40($fp)
80069db8: nop
80069dbc: andi $a0, $a1, 0xffff
80069dc0: lui $a1, 0xffff
80069dc4: and $a2, $a2, $a1
80069dc8: or $a2, $a2, $a0
80069dcc: move $a0, $v0
80069dd0: move $a1, $v1
80069dd4: jal 0x80017b18
80069dd8: nop
80069ddc: addiu $a0, $zero, 0x38
80069de0: addiu $a1, $zero, 0x28
80069de4: lui $a2, 0x800c
80069de8: addiu $a2, $a2, -0x6ca0
80069dec: jal 0x80067338
80069df0: nop
80069df4: sw $zero, 0x18($fp)
80069df8: sw $zero, 0x24($fp)
80069dfc: lw $v0, 0x18($fp)
80069e00: nop
80069e04: slti $v1, $v0, 5
80069e08: bnez $v1, 0x80069e18
80069e0c: nop
80069e10: j 0x80069f38
80069e14: nop
80069e18: lw $v0, 0x18($fp)
80069e1c: lui $a0, 0x6666
80069e20: ori $a0, $a0, 0x6667
80069e24: mult $v0, $a0
80069e28: mfhi $v1
80069e2c: sra $a0, $v1, 1
80069e30: sra $a1, $v0, 0x1f
80069e34: subu $v1, $a0, $a1
80069e38: move $a1, $v1
80069e3c: sll $a0, $a1, 2
80069e40: addu $a0, $a0, $v1
80069e44: subu $v0, $v0, $a0
80069e48: move $a0, $v0
80069e4c: sll $v1, $a0, 2
80069e50: addu $v1, $v1, $v0
80069e54: sll $a0, $v1, 3
80069e58: addiu $v0, $a0, 0x44
80069e5c: lw $v1, 0x18($fp)
80069e60: lui $a1, 0x6666
80069e64: ori $a1, $a1, 0x6667
80069e68: mult $v1, $a1
80069e6c: mfhi $a0
80069e70: sra $a1, $a0, 1
80069e74: sra $a0, $v1, 0x1f
80069e78: subu $v1, $a1, $a0
80069e7c: move $a1, $v1
80069e80: sll $a0, $a1, 2
80069e84: addu $a0, $a0, $v1
80069e88: sll $a1, $a0, 3
80069e8c: addiu $v1, $a1, 0x58
80069e90: addiu $a0, $fp, 0x30
80069e94: lw $a1, 0x18($fp)
80069e98: nop
80069e9c: addu $a0, $a0, $a1
80069ea0: move $a1, $a0
80069ea4: lb $a3, ($a1)
80069ea8: move $a0, $v0
80069eac: move $a1, $v1
80069eb0: lw $a2, 0x18($fp)
80069eb4: jal 0x8006a304
80069eb8: nop
80069ebc: addiu $v0, $fp, 0x30
80069ec0: lw $v1, 0x18($fp)
80069ec4: nop
80069ec8: addu $v0, $v0, $v1
80069ecc: move $v1, $v0
80069ed0: lb $v0, ($v1)
80069ed4: addiu $v1, $zero, 1
80069ed8: bne $v0, $v1, 0x80069f1c
80069edc: nop
80069ee0: lw $v0, 0x18($fp)
80069ee4: nop
80069ee8: move $a0, $v0
80069eec: sll $v1, $a0, 1
80069ef0: addu $v1, $v1, $v0
80069ef4: sll $a0, $v1, 2
80069ef8: subu $a0, $a0, $v0
80069efc: sll $v0, $a0, 2
80069f00: lw $v1, 0x24($fp)
80069f04: lui $at, 0x800a
80069f08: addu $at, $at, $v0
80069f0c: lw $v0, -0x1a8($at)
80069f10: nop
80069f14: addu $v1, $v1, $v0
80069f18: sw $v1, 0x24($fp)
80069f1c: lw $v1, 0x18($fp)
80069f20: nop
80069f24: addiu $v0, $v1, 1
80069f28: move $v1, $v0
80069f2c: sw $v1, 0x18($fp)
80069f30: j 0x80069dfc
80069f34: nop
80069f38: lw $v0, 0x20($fp)
80069f3c: nop
80069f40: move $a0, $v0
80069f44: sll $v1, $a0, 2
80069f48: addu $v1, $v1, $v0
80069f4c: sll $v0, $v1, 2
80069f50: lui $v1, 0x800c
80069f54: addiu $v1, $v1, -0x6be0
80069f58: addu $v0, $v0, $v1
80069f5c: addiu $a0, $zero, 0x48
80069f60: addiu $a1, $zero, 0x38
80069f64: move $a2, $v0
80069f68: jal 0x80067338
80069f6c: nop
80069f70: addiu $a0, $zero, 0xf0
80069f74: addiu $a1, $zero, 0x38
80069f78: lui $a2, 0x800c
80069f7c: addiu $a2, $a2, -0x6c6c
80069f80: jal 0x80067338
80069f84: nop
80069f88: lw $v0, 0x20($fp)
80069f8c: nop
80069f90: move $a0, $v0
80069f94: sll $v1, $a0, 1
80069f98: addu $v1, $v1, $v0
80069f9c: sll $a0, $v1, 2
80069fa0: subu $a0, $a0, $v0
80069fa4: sll $v0, $a0, 2
80069fa8: lui $at, 0x800a
80069fac: addu $at, $at, $v0
80069fb0: lw $v1, -0x1a8($at)
80069fb4: lui $at, 0x800e
80069fb8: sw $v1, 0x4000($at)
80069fbc: lui $a0, 0x800e
80069fc0: lw $a0, 0x4000($a0)
80069fc4: jal 0x80065820
80069fc8: nop
80069fcc: addiu $v1, $zero, 0xb
80069fd0: subu $v0, $v1, $v0
80069fd4: move $v1, $v0
80069fd8: sll $v0, $v1, 3
80069fdc: sw $v0, 0x28($fp)
80069fe0: lw $v1, 0x28($fp)
80069fe4: nop
80069fe8: addiu $v0, $v1, 0x98
80069fec: move $a0, $v0
80069ff0: addiu $a1, $zero, 0x38
80069ff4: addiu $a2, $zero, 0x110
80069ff8: jal 0x8004e494
80069ffc: nop
8006a000: addiu $a0, $zero, 0x48
8006a004: addiu $a1, $zero, 0x48
8006a008: lui $a2, 0x800c
8006a00c: addiu $a2, $a2, -0x6c78
8006a010: jal 0x80067338
8006a014: nop
8006a018: addiu $a0, $zero, 0xf0
8006a01c: addiu $a1, $zero, 0x48
8006a020: lui $a2, 0x800c
8006a024: addiu $a2, $a2, -0x6c6c
8006a028: jal 0x80067338
8006a02c: nop
8006a030: lw $v0, 0x24($fp)
8006a034: lui $at, 0x800e
8006a038: sw $v0, 0x4000($at)
8006a03c: lui $a0, 0x800e
8006a040: lw $a0, 0x4000($a0)
8006a044: jal 0x80065820
8006a048: nop
8006a04c: addiu $v1, $zero, 0xb
8006a050: subu $v0, $v1, $v0
8006a054: move $v1, $v0
8006a058: sll $v0, $v1, 3
8006a05c: sw $v0, 0x28($fp)
8006a060: lw $v1, 0x28($fp)
8006a064: nop
8006a068: addiu $v0, $v1, 0x98
8006a06c: move $a0, $v0
8006a070: addiu $a1, $zero, 0x48
8006a074: addiu $a2, $zero, 0x110
8006a078: jal 0x8004e494
8006a07c: nop
8006a080: addiu $a0, $zero, 0x7c
8006a084: addiu $a1, $zero, 0x84
8006a088: addiu $a2, $zero, 0x16
8006a08c: jal 0x8004e494
8006a090: nop
8006a094: lw $v0, 0x20($fp)
8006a098: lui $a0, 0x6666
8006a09c: ori $a0, $a0, 0x6667
8006a0a0: mult $v0, $a0
8006a0a4: mfhi $v1
8006a0a8: sra $a0, $v1, 1
8006a0ac: sra $a1, $v0, 0x1f
8006a0b0: subu $v1, $a0, $a1
8006a0b4: move $a1, $v1
8006a0b8: sll $a0, $a1, 2
8006a0bc: addu $a0, $a0, $v1
8006a0c0: subu $v0, $v0, $a0
8006a0c4: move $a0, $v0
8006a0c8: sll $v1, $a0, 2
8006a0cc: addu $v1, $v1, $v0
8006a0d0: sll $v0, $v1, 3
8006a0d4: move $v1, $v0
8006a0d8: addiu $v0, $v1, 0x5c
8006a0dc: sll $v1, $v0, 0x10
8006a0e0: sra $v0, $v1, 0x10
8006a0e4: move $a0, $v0
8006a0e8: addiu $a1, $zero, 0x72
8006a0ec: jal 0x8005fdd4
8006a0f0: nop
8006a0f4: addiu $a0, $zero, 0x2e
8006a0f8: addiu $a1, $zero, 1
8006a0fc: jal 0x80018940
8006a100: nop
8006a104: move $a0, $zero
8006a108: jal 0x80041374
8006a10c: nop
8006a110: lui $v1, 0x800d
8006a114: lw $v1, -0x25d8($v1)
8006a118: nop
8006a11c: andi $v0, $v1, 0x800
8006a120: beqz $v0, 0x8006a1a8
8006a124: nop
8006a128: sw $zero, 0x18($fp)
8006a12c: lw $v0, 0x18($fp)
8006a130: nop
8006a134: slti $v1, $v0, 5
8006a138: bnez $v1, 0x8006a148
8006a13c: nop
8006a140: j 0x8006a198
8006a144: nop
8006a148: lw $v0, 0x18($fp)
8006a14c: lui $a0, 0x800e
8006a150: addiu $a0, $a0, 0x3688
8006a154: addu $v1, $v0, $a0
8006a158: move $v0, $v1
8006a15c: addiu $v1, $fp, 0x30
8006a160: lw $a0, 0x18($fp)
8006a164: nop
8006a168: addu $v1, $v1, $a0
8006a16c: move $a0, $v1
8006a170: lbu $v1, ($a0)
8006a174: nop
8006a178: sb $v1, ($v0)
8006a17c: lw $v1, 0x18($fp)
8006a180: nop
8006a184: addiu $v0, $v1, 1
8006a188: move $v1, $v0
8006a18c: sw $v1, 0x18($fp)
8006a190: j 0x8006a12c
8006a194: nop
8006a198: jal 0x80065000
8006a19c: nop
8006a1a0: j 0x8006a2dc
8006a1a4: nop
8006a1a8: lui $v1, 0x800d
8006a1ac: lw $v1, -0x25d8($v1)
8006a1b0: nop
8006a1b4: andi $v0, $v1, 0x20
8006a1b8: beqz $v0, 0x8006a230
8006a1bc: nop
8006a1c0: addiu $v0, $fp, 0x30
8006a1c4: lw $v1, 0x20($fp)
8006a1c8: nop
8006a1cc: addu $v0, $v0, $v1
8006a1d0: move $v1, $v0
8006a1d4: lb $v0, ($v1)
8006a1d8: nop
8006a1dc: bnez $v0, 0x8006a210
8006a1e0: nop
8006a1e4: addiu $v0, $fp, 0x30
8006a1e8: lw $v1, 0x20($fp)
8006a1ec: nop
8006a1f0: addu $v0, $v0, $v1
8006a1f4: move $v1, $v0
8006a1f8: addiu $v0, $zero, 1
8006a1fc: sb $v0, ($v1)
8006a200: jal 0x80065000
8006a204: nop
8006a208: j 0x8006a230
8006a20c: nop
8006a210: addiu $v0, $fp, 0x30
8006a214: lw $v1, 0x20($fp)
8006a218: nop
8006a21c: addu $v0, $v0, $v1
8006a220: move $v1, $v0
8006a224: sb $zero, ($v1)
8006a228: jal 0x80065040
8006a22c: nop
8006a230: lui $v1, 0x800d
8006a234: lw $v1, -0x25d8($v1)
8006a238: nop
8006a23c: andi $v0, $v1, 0x40
8006a240: beqz $v0, 0x8006a258
8006a244: nop
8006a248: jal 0x80065040
8006a24c: nop
8006a250: j 0x8006a2dc
8006a254: nop
8006a258: lui $v1, 0x800d
8006a25c: lw $v1, -0x25f4($v1)
8006a260: nop
8006a264: andi $v0, $v1, 0x2000
8006a268: beqz $v0, 0x8006a298
8006a26c: nop
8006a270: lw $v0, 0x20($fp)
8006a274: nop
8006a278: slti $v1, $v0, 4
8006a27c: beqz $v1, 0x8006a298
8006a280: nop
8006a284: lw $v1, 0x20($fp)
8006a288: nop
8006a28c: addiu $v0, $v1, 1
8006a290: move $v1, $v0
8006a294: sw $v1, 0x20($fp)
8006a298: lui $v1, 0x800d
8006a29c: lw $v1, -0x25f4($v1)
8006a2a0: nop
8006a2a4: andi $v0, $v1, 0x8000
8006a2a8: beqz $v0, 0x8006a2d4
8006a2ac: nop
8006a2b0: lw $v0, 0x20($fp)
8006a2b4: nop
8006a2b8: blez $v0, 0x8006a2d4
8006a2bc: nop
8006a2c0: lw $v1, 0x20($fp)
8006a2c4: nop
8006a2c8: addiu $v0, $v1, -1
8006a2cc: move $v1, $v0
8006a2d0: sw $v1, 0x20($fp)
8006a2d4: j 0x80069d20
8006a2d8: nop
8006a2dc: jal 0x80065974
8006a2e0: nop
8006a2e4: j 0x8006a2ec
8006a2e8: nop
8006a2ec: move $sp, $fp
8006a2f0: lw $ra, 0x5c($sp)
8006a2f4: lw $fp, 0x58($sp)
8006a2f8: addiu $sp, $sp, 0x60
8006a2fc: jr $ra
8006a300: nop
8006a304: addiu $sp, $sp, -0x68
8006a308: sw $ra, 0x64($sp)
8006a30c: sw $fp, 0x60($sp)
8006a310: move $fp, $sp
8006a314: sw $a0, 0x68($fp)
8006a318: sw $a1, 0x6c($fp)
8006a31c: sw $a2, 0x70($fp)
8006a320: sw $a3, 0x74($fp)
8006a324: addiu $v0, $zero, 0x1d
8006a328: sh $v0, 0x44($fp)
8006a32c: addiu $v0, $zero, 0x20
8006a330: sh $v0, 0x42($fp)
8006a334: addiu $v0, $zero, 0x20
8006a338: sh $v0, 0x40($fp)
8006a33c: lhu $v0, 0x68($fp)
8006a340: nop
8006a344: addiu $v1, $v0, -0xa0
8006a348: sh $v1, 0x3c($fp)
8006a34c: lhu $v0, 0x6c($fp)
8006a350: nop
8006a354: addiu $v1, $v0, -0x70
8006a358: sh $v1, 0x3e($fp)
8006a35c: addiu $v0, $zero, 0xe0
8006a360: sb $v0, 0x46($fp)
8006a364: lw $v0, 0x70($fp)
8006a368: nop
8006a36c: move $v1, $v0
8006a370: sll $v0, $v1, 5
8006a374: move $v1, $v0
8006a378: addiu $v0, $v1, 0x60
8006a37c: sb $v0, 0x47($fp)
8006a380: sh $zero, 0x48($fp)
8006a384: addiu $v0, $zero, 0x1ef
8006a388: sh $v0, 0x4a($fp)
8006a38c: lw $v0, 0x74($fp)
8006a390: addiu $v1, $zero, 1
8006a394: bne $v0, $v1, 0x8006a3bc
8006a398: nop
8006a39c: addiu $v0, $zero, 0x80
8006a3a0: sb $v0, 0x4e($fp)
8006a3a4: addiu $v0, $zero, 0x80
8006a3a8: sb $v0, 0x4d($fp)
8006a3ac: addiu $v0, $zero, 0x80
8006a3b0: sb $v0, 0x4c($fp)
8006a3b4: j 0x8006a3d4
8006a3b8: nop
8006a3bc: addiu $v0, $zero, 0x40
8006a3c0: sb $v0, 0x4e($fp)
8006a3c4: addiu $v0, $zero, 0x40
8006a3c8: sb $v0, 0x4d($fp)
8006a3cc: addiu $v0, $zero, 0x40
8006a3d0: sb $v0, 0x4c($fp)
8006a3d4: lui $v0, 0x800d
8006a3d8: lh $v0, -0x25cc($v0)
8006a3dc: addiu $v1, $zero, 1
8006a3e0: sw $v1, 0x28($sp)
8006a3e4: addiu $v1, $sp, 0x10
8006a3e8: addiu $a0, $fp, 0x44
8006a3ec: lw $t1, ($a0)
8006a3f0: lw $t2, 4($a0)
8006a3f4: lw $t3, 8($a0)
8006a3f8: lw $t0, 0xc($a0)
8006a3fc: sw $t1, ($v1)
8006a400: sw $t2, 4($v1)
8006a404: sw $t3, 8($v1)
8006a408: sw $t0, 0xc($v1)
8006a40c: lw $t1, 0x10($a0)
8006a410: lw $t2, 0x14($a0)
8006a414: sw $t1, 0x10($v1)
8006a418: sw $t2, 0x14($v1)
8006a41c: lw $a1, 0x38($fp)
8006a420: lw $a2, 0x3c($fp)
8006a424: lw $a3, 0x40($fp)
8006a428: move $a0, $v0
8006a42c: jal 0x80041630
8006a430: nop
8006a434: move $sp, $fp
8006a438: lw $ra, 0x64($sp)
8006a43c: lw $fp, 0x60($sp)
8006a440: addiu $sp, $sp, 0x68
8006a444: jr $ra
8006a448: nop
800b9360: .byte 0x9d, 0x01, 0x9e, 0x01
800b9364: .byte 0x61, 0x01, 0x8e, 0x02
800b9368: .byte 0x6b, 0x00, 0xe8, 0x00
800b936c: .byte 0xe9, 0x00, 0x4a, 0x00
800b9370: .byte 0x51, 0x00, 0x56, 0x01
800b9374: .byte 0x49, 0x00, 0x40, 0x00
800b9378: .byte 0x38, 0x00, 0x8d, 0x02
800b937c: .byte 0x92, 0x02, 0xe8, 0x00
800b9380: .byte 0xe9, 0x00, 0x1a, 0x01
800b9384: .byte 0x39, 0x00, 0xff, 0x40
800b9388: .byte 0x80, 0x01, 0xf5, 0x00
800b938c: .byte 0x95, 0x01, 0x9c, 0x01
800b9390: .byte 0xff, 0x40, 0x00, 0x00
800b9394: .byte 0x29, 0x00, 0xe6, 0x00
800b9398: .byte 0xff, 0x40, 0x00, 0x00
800b939c: syscall 0x95806
800b93a0: .byte 0xff, 0x00, 0xff, 0x40
800b93a4: .byte 0x9b, 0x02, 0xe5, 0x00
800b93a8: .byte 0x8a, 0x02, 0xff, 0x40
800b93ac: .byte 0xec, 0x00, 0xed, 0x00
800b93b0: .byte 0x4b, 0x00, 0x67, 0x00
800b93b4: .byte 0xa7, 0x01, 0xf1, 0x00
800b93b8: .byte 0x6b, 0x00, 0xe8, 0x00
800b93bc: .byte 0xe9, 0x00, 0x4a, 0x00
800b93c0: .byte 0x51, 0x00, 0x56, 0x01
800b93c4: .byte 0x49, 0x00, 0x40, 0x00
800b93c8: .byte 0xff, 0x40, 0x00, 0x00
800b93cc: .byte 0x25, 0x01, 0x21, 0x01
800b93d0: .byte 0x6d, 0x00, 0x89, 0x01
800b93d4: .byte 0x23, 0x01, 0x4a, 0x00
800b93d8: .byte 0x51, 0x00, 0x40, 0x00
800b93dc: .byte 0x5d, 0x00, 0x4b, 0x00
800b93e0: .byte 0xff, 0x40, 0x00, 0x00
800b93e4: .byte 0xec, 0x00, 0xed, 0x00
800b93e8: .byte 0x4b, 0x00, 0x67, 0x00
800b93ec: .byte 0x43, 0x01, 0x82, 0x01
800b93f0: .byte 0x6b, 0x00, 0x13, 0x01
800b93f4: .byte 0x60, 0x00, 0x51, 0x00
800b93f8: .byte 0x56, 0x01, 0x49, 0x00
800b93fc: .byte 0x40, 0x00, 0xff, 0x40
800b9400: .byte 0xec, 0x00, 0xed, 0x00
800b9404: .byte 0x1a, 0x01, 0x2b, 0x02
800b9408: .byte 0xff, 0x40, 0x00, 0x00
800b940c: .byte 0xec, 0x00, 0xed, 0x00
800b9410: .byte 0x89, 0x01, 0x1a, 0x01
800b9414: .byte 0x2b, 0x02, 0xff, 0x40
800b9418: .byte 0x15, 0x02, 0x16, 0x02
800b941c: .byte 0x22, 0x01, 0xff, 0x40
800b9420: .byte 0xc7, 0x00, 0x90, 0x00
800b9424: .byte 0xb8, 0x00, 0x96, 0x00
800b9428: .byte 0xa2, 0x00, 0xb0, 0x00
800b942c: .byte 0x2e, 0x00, 0xb7, 0x00
800b9430: .byte 0xff, 0x40, 0x00, 0x00
800b9434: .byte 0x8e, 0x01, 0x9f, 0x01
800b9438: .byte 0xa0, 0x01, 0x0e, 0x01
800b943c: .byte 0xff, 0x40, 0x00, 0x00
800b9440: nop
800b9444: nop
800b9448: .byte 0xa1, 0x01, 0xa2, 0x01
800b944c: .byte 0xa3, 0x01, 0xff, 0x40
800b9450: nop
800b9454: nop
800b9458: nop
800b945c: .byte 0xb5, 0x00, 0xc3, 0x00
800b9460: .byte 0x93, 0x00, 0xff, 0x40
800b9464: nop
800b9468: nop
800b946c: nop
800b9470: .byte 0x1d, 0x00, 0x1f, 0x00
800b9474: .byte 0xff, 0x40, 0x00, 0x00
800b9478: nop
800b947c: nop
800b9480: nop
