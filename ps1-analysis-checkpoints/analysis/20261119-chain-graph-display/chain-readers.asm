80048b80: addiu $sp, $sp, -0x30
80048b84: sw $ra, 0x2c($sp)
80048b88: sw $fp, 0x28($sp)
80048b8c: move $fp, $sp
80048b90: sh $zero, 0x20($fp)
80048b94: addiu $v0, $zero, 8
80048b98: sh $v0, 0x10($fp)
80048b9c: addiu $v0, $zero, 0x10
80048ba0: sh $v0, 0x12($fp)
80048ba4: addiu $v0, $zero, 0x13
80048ba8: sh $v0, 0x14($fp)
80048bac: addiu $v0, $zero, 0xd
80048bb0: sh $v0, 0x16($fp)
80048bb4: sb $zero, 0x18($fp)
80048bb8: addiu $a0, $zero, 4
80048bbc: addiu $a1, $zero, 1
80048bc0: jal 0x80018940
80048bc4: nop
80048bc8: lhu $a0, 0x10($fp)
80048bcc: nop
80048bd0: andi $v1, $a0, 0xffff
80048bd4: lui $a0, 0xffff
80048bd8: and $v0, $v0, $a0
80048bdc: or $v0, $v0, $v1
80048be0: lhu $v1, 0x12($fp)
80048be4: nop
80048be8: sll $a0, $v1, 0x10
80048bec: andi $v0, $v0, 0xffff
80048bf0: or $v0, $v0, $a0
80048bf4: lhu $a1, 0x14($fp)
80048bf8: nop
80048bfc: andi $a0, $a1, 0xffff
80048c00: lui $a1, 0xffff
80048c04: and $v1, $v1, $a1
80048c08: or $v1, $v1, $a0
80048c0c: lhu $a0, 0x16($fp)
80048c10: nop
80048c14: sll $a1, $a0, 0x10
80048c18: andi $v1, $v1, 0xffff
80048c1c: or $v1, $v1, $a1
80048c20: lhu $a1, 0x18($fp)
80048c24: nop
80048c28: andi $a0, $a1, 0xffff
80048c2c: lui $a1, 0xffff
80048c30: and $a2, $a2, $a1
80048c34: or $a2, $a2, $a0
80048c38: move $a0, $v0
80048c3c: move $a1, $v1
80048c40: jal 0x80017b18
80048c44: nop
80048c48: jal 0x800157b4
80048c4c: nop
80048c50: addiu $a0, $zero, 0xa
80048c54: addiu $a1, $zero, 1
80048c58: jal 0x80018940
80048c5c: nop
80048c60: j 0x80048c70
80048c64: nop
80048c68: j 0x80048ce0
80048c6c: nop
80048c70: jal 0x800157b4
80048c74: nop
80048c78: addiu $a0, $zero, 0x18
80048c7c: addiu $a1, $zero, 0x20
80048c80: addiu $a2, $zero, 0x180
80048c84: jal 0x8004e494
80048c88: nop
80048c8c: jal 0x8004965c
80048c90: nop
80048c94: jal 0x80048cf8
80048c98: nop
80048c9c: jal 0x800485a0
80048ca0: nop
80048ca4: move $a0, $zero
80048ca8: jal 0x80041374
80048cac: nop
80048cb0: lui $v1, 0x800d
80048cb4: lw $v1, -0x25d8($v1)
80048cb8: nop
80048cbc: andi $v0, $v1, 0x60
80048cc0: beqz $v0, 0x80048cd8
80048cc4: nop
80048cc8: jal 0x80065000
80048ccc: nop
80048cd0: j 0x80048ce0
80048cd4: nop
80048cd8: j 0x80048c60
80048cdc: nop
80048ce0: move $sp, $fp
80048ce4: lw $ra, 0x2c($sp)
80048ce8: lw $fp, 0x28($sp)
80048cec: addiu $sp, $sp, 0x30
80048cf0: jr $ra
80048cf4: nop
80048cf8: addiu $sp, $sp, -0x28
80048cfc: sw $fp, 0x20($sp)
80048d00: move $fp, $sp
80048d04: lui $v0, 0x8018
80048d08: ori $v0, $v0, 0x7e00
80048d0c: sw $v0, 0x1c($fp)
80048d10: sb $zero, 0x10($fp)
80048d14: sb $zero, 0x11($fp)
80048d18: addiu $v0, $zero, 0x30
80048d1c: sb $v0, 0x12($fp)
80048d20: sb $zero, 0x13($fp)
80048d24: sh $zero, ($fp)
80048d28: lh $v0, ($fp)
80048d2c: nop
80048d30: slti $v1, $v0, 0x70
80048d34: bnez $v1, 0x80048d44
80048d38: nop
80048d3c: j 0x8004902c
80048d40: nop
80048d44: sh $zero, 2($fp)
80048d48: lh $v0, 2($fp)
80048d4c: nop
80048d50: slti $v1, $v0, 0xf0
80048d54: bnez $v1, 0x80048d64
80048d58: nop
80048d5c: j 0x80048f98
80048d60: nop
80048d64: lh $v1, ($fp)
80048d68: lh $v0, 2($fp)
80048d6c: move $a1, $v1
80048d70: sll $a0, $a1, 4
80048d74: subu $a0, $a0, $v1
80048d78: sll $v1, $a0, 4
80048d7c: lw $a0, 0x1c($fp)
80048d80: nop
80048d84: addu $v1, $v1, $a0
80048d88: addu $v0, $v1, $v0
80048d8c: move $v1, $v0
80048d90: addiu $v0, $zero, 1
80048d94: sb $v0, ($v1)
80048d98: lbu $v0, 0x13($fp)
80048d9c: nop
80048da0: bnez $v0, 0x80048e00
80048da4: nop
80048da8: lh $v0, 2($fp)
80048dac: lbu $v1, 0x12($fp)
80048db0: nop
80048db4: bne $v0, $v1, 0x80048e00
80048db8: nop
80048dbc: lh $v1, ($fp)
80048dc0: lh $v0, 2($fp)
80048dc4: move $a1, $v1
80048dc8: sll $a0, $a1, 4
80048dcc: subu $a0, $a0, $v1
80048dd0: sll $v1, $a0, 4
80048dd4: lw $a0, 0x1c($fp)
80048dd8: nop
80048ddc: addu $v1, $v1, $a0
80048de0: addu $v0, $v1, $v0
80048de4: move $v1, $v0
80048de8: addiu $v0, $zero, 4
80048dec: sb $v0, ($v1)
80048df0: lbu $v0, 0x12($fp)
80048df4: nop
80048df8: addiu $v1, $v0, 0x30
80048dfc: sb $v1, 0x12($fp)
80048e00: lh $v0, ($fp)
80048e04: addiu $v1, $zero, 0x1c
80048e08: bne $v0, $v1, 0x80048e9c
80048e0c: nop
80048e10: lbu $v0, 0x10($fp)
80048e14: nop
80048e18: sltiu $v1, $v0, 2
80048e1c: beqz $v1, 0x80048e74
80048e20: nop
80048e24: lh $v1, ($fp)
80048e28: lh $v0, 2($fp)
80048e2c: move $a1, $v1
80048e30: sll $a0, $a1, 4
80048e34: subu $a0, $a0, $v1
80048e38: sll $v1, $a0, 4
80048e3c: lw $a0, 0x1c($fp)
80048e40: nop
80048e44: addu $v1, $v1, $a0
80048e48: addu $v0, $v1, $v0
80048e4c: move $v1, $v0
80048e50: addiu $v0, $zero, 4
80048e54: sb $v0, ($v1)
80048e58: lbu $v0, 0x10($fp)
80048e5c: nop
80048e60: addiu $v1, $v0, 1
80048e64: move $v0, $v1
80048e68: sb $v0, 0x10($fp)
80048e6c: j 0x80048e9c
80048e70: nop
80048e74: lbu $v0, 0x10($fp)
80048e78: nop
80048e7c: addiu $v1, $v0, 1
80048e80: move $v0, $v1
80048e84: sb $v0, 0x10($fp)
80048e88: lbu $v0, 0x10($fp)
80048e8c: addiu $v1, $zero, 4
80048e90: bne $v0, $v1, 0x80048e9c
80048e94: nop
80048e98: sb $zero, 0x10($fp)
80048e9c: lh $v0, ($fp)
80048ea0: addiu $v1, $zero, 0x54
80048ea4: bne $v0, $v1, 0x80048f38
80048ea8: nop
80048eac: lbu $v0, 0x10($fp)
80048eb0: nop
80048eb4: sltiu $v1, $v0, 2
80048eb8: beqz $v1, 0x80048f10
80048ebc: nop
80048ec0: lh $v1, ($fp)
80048ec4: lh $v0, 2($fp)
80048ec8: move $a1, $v1
80048ecc: sll $a0, $a1, 4
80048ed0: subu $a0, $a0, $v1
80048ed4: sll $v1, $a0, 4
80048ed8: lw $a0, 0x1c($fp)
80048edc: nop
80048ee0: addu $v1, $v1, $a0
80048ee4: addu $v0, $v1, $v0
80048ee8: move $v1, $v0
80048eec: addiu $v0, $zero, 4
80048ef0: sb $v0, ($v1)
80048ef4: lbu $v0, 0x10($fp)
80048ef8: nop
80048efc: addiu $v1, $v0, 1
80048f00: move $v0, $v1
80048f04: sb $v0, 0x10($fp)
80048f08: j 0x80048f38
80048f0c: nop
80048f10: lbu $v0, 0x10($fp)
80048f14: nop
80048f18: addiu $v1, $v0, 1
80048f1c: move $v0, $v1
80048f20: sb $v0, 0x10($fp)
80048f24: lbu $v0, 0x10($fp)
80048f28: addiu $v1, $zero, 4
80048f2c: bne $v0, $v1, 0x80048f38
80048f30: nop
80048f34: sb $zero, 0x10($fp)
80048f38: lh $v0, ($fp)
80048f3c: addiu $v1, $zero, 0x38
80048f40: bne $v0, $v1, 0x80048f7c
80048f44: nop
80048f48: lh $v1, ($fp)
80048f4c: lh $v0, 2($fp)
80048f50: move $a1, $v1
80048f54: sll $a0, $a1, 4
80048f58: subu $a0, $a0, $v1
80048f5c: sll $v1, $a0, 4
80048f60: lw $a0, 0x1c($fp)
80048f64: nop
80048f68: addu $v1, $v1, $a0
80048f6c: addu $v0, $v1, $v0
80048f70: move $v1, $v0
80048f74: addiu $v0, $zero, 4
80048f78: sb $v0, ($v1)
80048f7c: lhu $v0, 2($fp)
80048f80: nop
80048f84: addiu $v1, $v0, 1
80048f88: move $v0, $v1
80048f8c: sh $v0, 2($fp)
80048f90: j 0x80048d48
80048f94: nop
80048f98: addiu $v0, $zero, 0x30
80048f9c: sb $v0, 0x12($fp)
80048fa0: lbu $v0, 0x11($fp)
80048fa4: nop
80048fa8: sltiu $v1, $v0, 2
80048fac: beqz $v1, 0x80048fd4
80048fb0: nop
80048fb4: sb $zero, 0x13($fp)
80048fb8: lbu $v0, 0x11($fp)
80048fbc: nop
80048fc0: addiu $v1, $v0, 1
80048fc4: move $v0, $v1
80048fc8: sb $v0, 0x11($fp)
80048fcc: j 0x80049010
80048fd0: nop
80048fd4: lbu $v0, 0x11($fp)
80048fd8: addiu $v1, $zero, 4
80048fdc: bne $v0, $v1, 0x80048ff4
80048fe0: nop
80048fe4: sb $zero, 0x11($fp)
80048fe8: sb $zero, 0x13($fp)
80048fec: j 0x80049010
80048ff0: nop
80048ff4: lbu $v0, 0x11($fp)
80048ff8: nop
80048ffc: addiu $v1, $v0, 1
80049000: move $v0, $v1
80049004: sb $v0, 0x11($fp)
80049008: addiu $v0, $zero, 1
8004900c: sb $v0, 0x13($fp)
80049010: lhu $v0, ($fp)
80049014: nop
80049018: addiu $v1, $v0, 1
8004901c: move $v0, $v1
80049020: sh $v0, ($fp)
80049024: j 0x80048d28
80049028: nop
8004902c: sh $zero, 0xa($fp)
80049030: sh $zero, 4($fp)
80049034: lh $v0, 4($fp)
80049038: nop
8004903c: slti $v1, $v0, 0x3c
80049040: bnez $v1, 0x80049050
80049044: nop
80049048: j 0x800490dc
8004904c: nop
80049050: lh $v0, 4($fp)
80049054: lui $at, 0x800e
80049058: addu $at, $at, $v0
8004905c: lb $v1, 0x43d0($at)
80049060: nop
80049064: bgtz $v1, 0x80049074
80049068: nop
8004906c: j 0x800490dc
80049070: nop
80049074: lh $v0, 4($fp)
80049078: nop
8004907c: move $v1, $v0
80049080: sll $v0, $v1, 2
80049084: lui $v1, 0x800e
80049088: addiu $v1, $v1, 0x3c28
8004908c: addu $v0, $v0, $v1
80049090: move $v1, $v0
80049094: lw $v0, ($v1)
80049098: lui $v1, 0x8000
8004909c: bne $v0, $v1, 0x800490ac
800490a0: nop
800490a4: j 0x800490dc
800490a8: nop
800490ac: lhu $v0, 0xa($fp)
800490b0: nop
800490b4: addiu $v1, $v0, 1
800490b8: move $v0, $v1
800490bc: sh $v0, 0xa($fp)
800490c0: lhu $v0, 4($fp)
800490c4: nop
800490c8: addiu $v1, $v0, 1
800490cc: move $v0, $v1
800490d0: sh $v0, 4($fp)
800490d4: j 0x80049034
800490d8: nop
800490dc: lh $v0, 0xa($fp)
800490e0: nop
800490e4: bnez $v0, 0x800490f8
800490e8: nop
800490ec: move $v0, $zero
800490f0: j 0x80049648
800490f4: nop
800490f8: lhu $v0, 0xa($fp)
800490fc: nop
80049100: sh $v0, 8($fp)
80049104: lhu $v0, 0xa($fp)
80049108: nop
8004910c: addiu $v1, $v0, -1
80049110: move $v0, $v1
80049114: sh $v0, 0xa($fp)
80049118: sh $zero, 0xc($fp)
8004911c: sh $zero, 4($fp)
80049120: lh $v0, 4($fp)
80049124: lh $v1, 8($fp)
80049128: nop
8004912c: slt $v0, $v0, $v1
80049130: bnez $v0, 0x80049140
80049134: nop
80049138: j 0x8004963c
8004913c: nop
80049140: lh $v0, 0xa($fp)
80049144: nop
80049148: move $v1, $v0
8004914c: sll $v0, $v1, 2
80049150: lui $v1, 0x800e
80049154: addiu $v1, $v1, 0x3c28
80049158: addu $v0, $v0, $v1
8004915c: move $v1, $v0
80049160: lw $v0, ($v1)
80049164: nop
80049168: sw $v0, 0x14($fp)
8004916c: lw $v0, 0x14($fp)
80049170: nop
80049174: bgez $v0, 0x800493c8
80049178: nop
8004917c: lh $v0, 0xa($fp)
80049180: nop
80049184: move $v1, $v0
80049188: sll $v0, $v1, 2
8004918c: lui $v1, 0x800e
80049190: addiu $v1, $v1, 0x3c28
80049194: addu $v0, $v0, $v1
80049198: move $v1, $v0
8004919c: lw $v0, ($v1)
800491a0: nop
800491a4: bgez $v0, 0x800491b0
800491a8: move $v1, $v0
800491ac: negu $v1, $v1
800491b0: sw $v1, 0x14($fp)
800491b4: lw $v0, 0x14($fp)
800491b8: lui $a0, 0x68db
800491bc: ori $a0, $a0, 0x8bad
800491c0: mult $v0, $a0
800491c4: mfhi $v1
800491c8: sra $a0, $v1, 0xc
800491cc: sra $v1, $v0, 0x1f
800491d0: subu $v0, $a0, $v1
800491d4: sw $v0, 0x14($fp)
800491d8: lui $v0, 0x800e
800491dc: lw $v0, 0x4000($v0)
800491e0: nop
800491e4: sw $v0, 0x18($fp)
800491e8: lw $v0, 0x14($fp)
800491ec: nop
800491f0: move $a0, $v0
800491f4: sll $v1, $a0, 3
800491f8: subu $v1, $v1, $v0
800491fc: sll $v0, $v1, 3
80049200: lw $v1, 0x18($fp)
80049204: nop
80049208: div $zero, $v0, $v1
8004920c: bnez $v1, 0x80049218
80049210: nop
80049214: break 7
80049218: addiu $at, $zero, -1
8004921c: bne $v1, $at, 0x80049230
80049220: lui $at, 0x8000
80049224: bne $v0, $at, 0x80049230
80049228: nop
8004922c: break 6
80049230: mflo $v0
80049234: nop
80049238: sh $v0, 6($fp)
8004923c: lhu $v0, 6($fp)
80049240: nop
80049244: addiu $v1, $v0, 0x39
80049248: sh $v1, 6($fp)
8004924c: addiu $v0, $zero, 0x38
80049250: sh $v0, ($fp)
80049254: lh $v0, ($fp)
80049258: nop
8004925c: slti $v1, $v0, 0x70
80049260: bnez $v1, 0x80049270
80049264: nop
80049268: j 0x800493b0
8004926c: nop
80049270: sh $zero, 0xe($fp)
80049274: lhu $v0, 0xc($fp)
80049278: nop
8004927c: sh $v0, 2($fp)
80049280: lh $v0, 2($fp)
80049284: nop
80049288: slti $v1, $v0, 0xf0
8004928c: bnez $v1, 0x8004929c
80049290: nop
80049294: j 0x80049394
80049298: nop
8004929c: lh $v0, 0xe($fp)
800492a0: nop
800492a4: slti $v1, $v0, 4
800492a8: beqz $v1, 0x80049378
800492ac: nop
800492b0: lh $v0, ($fp)
800492b4: lh $v1, 6($fp)
800492b8: nop
800492bc: slt $v0, $v0, $v1
800492c0: beqz $v0, 0x80049378
800492c4: nop
800492c8: lh $v0, 0xe($fp)
800492cc: addiu $v1, $zero, 3
800492d0: bne $v0, $v1, 0x8004932c
800492d4: nop
800492d8: lh $v1, ($fp)
800492dc: lh $v0, 2($fp)
800492e0: move $a1, $v1
800492e4: sll $a0, $a1, 4
800492e8: subu $a0, $a0, $v1
800492ec: sll $v1, $a0, 4
800492f0: lw $a0, 0x1c($fp)
800492f4: nop
800492f8: addu $v1, $v1, $a0
800492fc: addu $v0, $v1, $v0
80049300: addiu $v1, $v0, 0xf0
80049304: move $v0, $v1
80049308: addiu $v1, $zero, 4
8004930c: sb $v1, ($v0)
80049310: lhu $v0, 0xe($fp)
80049314: nop
80049318: addiu $v1, $v0, 1
8004931c: move $v0, $v1
80049320: sh $v0, 0xe($fp)
80049324: j 0x80049378
80049328: nop
8004932c: lh $v1, ($fp)
80049330: lh $v0, 2($fp)
80049334: move $a1, $v1
80049338: sll $a0, $a1, 4
8004933c: subu $a0, $a0, $v1
80049340: sll $v1, $a0, 4
80049344: lw $a0, 0x1c($fp)
80049348: nop
8004934c: addu $v1, $v1, $a0
80049350: addu $v0, $v1, $v0
80049354: addiu $v1, $v0, 0xf0
80049358: move $v0, $v1
8004935c: addiu $v1, $zero, 2
80049360: sb $v1, ($v0)
80049364: lhu $v0, 0xe($fp)
80049368: nop
8004936c: addiu $v1, $v0, 1
80049370: move $v0, $v1
80049374: sh $v0, 0xe($fp)
80049378: lhu $v0, 2($fp)
8004937c: nop
80049380: addiu $v1, $v0, 1
80049384: move $v0, $v1
80049388: sh $v0, 2($fp)
8004938c: j 0x80049280
80049390: nop
80049394: lhu $v0, ($fp)
80049398: nop
8004939c: addiu $v1, $v0, 1
800493a0: move $v0, $v1
800493a4: sh $v0, ($fp)
800493a8: j 0x80049254
800493ac: nop
800493b0: lhu $v0, 0xc($fp)
800493b4: nop
800493b8: addiu $v1, $v0, 4
800493bc: sh $v1, 0xc($fp)
800493c0: j 0x8004960c
800493c4: nop
800493c8: lh $v0, 0xa($fp)
800493cc: nop
800493d0: move $v1, $v0
800493d4: sll $v0, $v1, 2
800493d8: lui $v1, 0x800e
800493dc: addiu $v1, $v1, 0x3c28
800493e0: addu $v0, $v0, $v1
800493e4: move $v1, $v0
800493e8: lw $v0, ($v1)
800493ec: nop
800493f0: bgez $v0, 0x800493fc
800493f4: move $v1, $v0
800493f8: negu $v1, $v1
800493fc: sw $v1, 0x14($fp)
80049400: lw $v0, 0x14($fp)
80049404: lui $a0, 0x68db
80049408: ori $a0, $a0, 0x8bad
8004940c: mult $v0, $a0
80049410: mfhi $v1
80049414: sra $a0, $v1, 0xc
80049418: sra $v1, $v0, 0x1f
8004941c: subu $v0, $a0, $v1
80049420: sw $v0, 0x14($fp)
80049424: lui $v0, 0x800e
80049428: lw $v0, 0x4000($v0)
8004942c: nop
80049430: sw $v0, 0x18($fp)
80049434: lw $v0, 0x14($fp)
80049438: nop
8004943c: move $a0, $v0
80049440: sll $v1, $a0, 3
80049444: subu $v1, $v1, $v0
80049448: sll $v0, $v1, 3
8004944c: lw $v1, 0x18($fp)
80049450: nop
80049454: div $zero, $v0, $v1
80049458: bnez $v1, 0x80049464
8004945c: nop
80049460: break 7
80049464: addiu $at, $zero, -1
80049468: bne $v1, $at, 0x8004947c
8004946c: lui $at, 0x8000
80049470: bne $v0, $at, 0x8004947c
80049474: nop
80049478: break 6
8004947c: mflo $v0
80049480: nop
80049484: sh $v0, 6($fp)
80049488: lhu $v0, 6($fp)
8004948c: addiu $v1, $zero, 0x38
80049490: subu $v0, $v1, $v0
80049494: sh $v0, 6($fp)
80049498: lhu $v0, 6($fp)
8004949c: nop
800494a0: sh $v0, ($fp)
800494a4: lh $v0, ($fp)
800494a8: nop
800494ac: slti $v1, $v0, 0x70
800494b0: bnez $v1, 0x800494c0
800494b4: nop
800494b8: j 0x800495fc
800494bc: nop
800494c0: sh $zero, 0xe($fp)
800494c4: lhu $v0, 0xc($fp)
800494c8: nop
800494cc: sh $v0, 2($fp)
800494d0: lh $v0, 2($fp)
800494d4: nop
800494d8: slti $v1, $v0, 0xf0
800494dc: bnez $v1, 0x800494ec
800494e0: nop
800494e4: j 0x800495e0
800494e8: nop
800494ec: lh $v0, 0xe($fp)
800494f0: nop
800494f4: slti $v1, $v0, 4
800494f8: beqz $v1, 0x800495c4
800494fc: nop
80049500: lh $v0, ($fp)
80049504: nop
80049508: slti $v1, $v0, 0x39
8004950c: beqz $v1, 0x800495c4
80049510: nop
80049514: lh $v0, 0xe($fp)
80049518: addiu $v1, $zero, 3
8004951c: bne $v0, $v1, 0x80049578
80049520: nop
80049524: lh $v1, ($fp)
80049528: lh $v0, 2($fp)
8004952c: move $a1, $v1
80049530: sll $a0, $a1, 4
80049534: subu $a0, $a0, $v1
80049538: sll $v1, $a0, 4
8004953c: lw $a0, 0x1c($fp)
80049540: nop
80049544: addu $v1, $v1, $a0
80049548: addu $v0, $v1, $v0
8004954c: addiu $v1, $v0, -0xf0
80049550: move $v0, $v1
80049554: addiu $v1, $zero, 4
80049558: sb $v1, ($v0)
8004955c: lhu $v0, 0xe($fp)
80049560: nop
80049564: addiu $v1, $v0, 1
80049568: move $v0, $v1
8004956c: sh $v0, 0xe($fp)
80049570: j 0x800495c4
80049574: nop
80049578: lh $v1, ($fp)
8004957c: lh $v0, 2($fp)
80049580: move $a1, $v1
80049584: sll $a0, $a1, 4
80049588: subu $a0, $a0, $v1
8004958c: sll $v1, $a0, 4
80049590: lw $a0, 0x1c($fp)
80049594: nop
80049598: addu $v1, $v1, $a0
8004959c: addu $v0, $v1, $v0
800495a0: addiu $v1, $v0, -0xf0
800495a4: move $v0, $v1
800495a8: addiu $v1, $zero, 3
800495ac: sb $v1, ($v0)
800495b0: lhu $v0, 0xe($fp)
800495b4: nop
800495b8: addiu $v1, $v0, 1
800495bc: move $v0, $v1
800495c0: sh $v0, 0xe($fp)
800495c4: lhu $v0, 2($fp)
800495c8: nop
800495cc: addiu $v1, $v0, 1
800495d0: move $v0, $v1
800495d4: sh $v0, 2($fp)
800495d8: j 0x800494d0
800495dc: nop
800495e0: lhu $v0, ($fp)
800495e4: nop
800495e8: addiu $v1, $v0, 1
800495ec: move $v0, $v1
800495f0: sh $v0, ($fp)
800495f4: j 0x800494a4
800495f8: nop
800495fc: lhu $v0, 0xc($fp)
80049600: nop
80049604: addiu $v1, $v0, 4
80049608: sh $v1, 0xc($fp)
8004960c: lhu $v0, 0xa($fp)
80049610: nop
80049614: addiu $v1, $v0, -1
80049618: move $v0, $v1
8004961c: sh $v0, 0xa($fp)
80049620: lhu $v0, 4($fp)
80049624: nop
80049628: addiu $v1, $v0, 1
8004962c: move $v0, $v1
80049630: sh $v0, 4($fp)
80049634: j 0x80049120
80049638: nop
8004963c: addiu $v0, $zero, 1
80049640: j 0x80049648
80049644: nop
80049648: move $sp, $fp
8004964c: lw $fp, 0x20($sp)
80049650: addiu $sp, $sp, 0x28
80049654: jr $ra
80049658: nop
8004965c: addiu $sp, $sp, -0x30
80049660: sw $ra, 0x2c($sp)
80049664: sw $fp, 0x28($sp)
80049668: move $fp, $sp
8004966c: addiu $v0, $zero, 1
80049670: sw $v0, 0x14($fp)
80049674: lui $v0, 0xf
80049678: ori $v0, $v0, 0x4240
8004967c: sw $v0, 0x18($fp)
80049680: lui $v0, 0xf
80049684: ori $v0, $v0, 0x4240
80049688: sw $v0, 0x1c($fp)
8004968c: sw $zero, 0x20($fp)
80049690: lw $v0, 0x20($fp)
80049694: nop
80049698: slti $v1, $v0, 0x3c
8004969c: bnez $v1, 0x800496ac
800496a0: nop
800496a4: j 0x800497ac
800496a8: nop
800496ac: lw $v0, 0x20($fp)
800496b0: lui $v1, 0x800e
800496b4: addiu $v1, $v1, 0x43d0
800496b8: addu $v0, $v0, $v1
800496bc: move $v1, $v0
800496c0: lb $v0, ($v1)
800496c4: nop
800496c8: bgtz $v0, 0x800496d8
800496cc: nop
800496d0: j 0x800497ac
800496d4: nop
800496d8: lw $v0, 0x20($fp)
800496dc: nop
800496e0: move $v1, $v0
800496e4: sll $v0, $v1, 2
800496e8: lui $v1, 0x800e
800496ec: addiu $v1, $v1, 0x3c28
800496f0: addu $v0, $v0, $v1
800496f4: move $v1, $v0
800496f8: lw $v0, ($v1)
800496fc: lui $v1, 0x8000
80049700: bne $v0, $v1, 0x80049710
80049704: nop
80049708: j 0x800497ac
8004970c: nop
80049710: lw $v0, 0x20($fp)
80049714: nop
80049718: move $v1, $v0
8004971c: sll $v0, $v1, 2
80049720: lui $v1, 0x800e
80049724: addiu $v1, $v1, 0x3c28
80049728: addu $v0, $v0, $v1
8004972c: move $v1, $v0
80049730: lw $a0, ($v1)
80049734: nop
80049738: bgez $a0, 0x80049744
8004973c: move $v0, $a0
80049740: negu $v0, $v0
80049744: lw $v1, 0x14($fp)
80049748: nop
8004974c: slt $v0, $v1, $v0
80049750: beqz $v0, 0x80049790
80049754: nop
80049758: lw $v0, 0x20($fp)
8004975c: nop
80049760: move $v1, $v0
80049764: sll $v0, $v1, 2
80049768: lui $v1, 0x800e
8004976c: addiu $v1, $v1, 0x3c28
80049770: addu $v0, $v0, $v1
80049774: move $v1, $v0
80049778: lw $v0, ($v1)
8004977c: nop
80049780: bgez $v0, 0x8004978c
80049784: move $v1, $v0
80049788: negu $v1, $v1
8004978c: sw $v1, 0x14($fp)
80049790: lw $v1, 0x20($fp)
80049794: nop
80049798: addiu $v0, $v1, 1
8004979c: move $v1, $v0
800497a0: sw $v1, 0x20($fp)
800497a4: j 0x80049690
800497a8: nop
800497ac: lw $v0, 0x18($fp)
800497b0: lw $v1, 0x14($fp)
800497b4: nop
800497b8: slt $v0, $v0, $v1
800497bc: bnez $v0, 0x800497cc
800497c0: nop
800497c4: j 0x800497e8
800497c8: nop
800497cc: lw $v0, 0x18($fp)
800497d0: lw $v1, 0x1c($fp)
800497d4: nop
800497d8: addu $v0, $v0, $v1
800497dc: sw $v0, 0x18($fp)
800497e0: j 0x800497ac
800497e4: nop
800497e8: lw $v0, 0x18($fp)
800497ec: lui $a0, 0x68db
800497f0: ori $a0, $a0, 0x8bad
800497f4: mult $v0, $a0
800497f8: mfhi $v1
800497fc: sra $a0, $v1, 0xc
80049800: sra $v1, $v0, 0x1f
80049804: subu $v0, $a0, $v1
80049808: lui $at, 0x800e
8004980c: sw $v0, 0x4000($at)
80049810: lui $at, 0x800e
80049814: sw $zero, 0x4008($at)
80049818: lw $v0, 0x18($fp)
8004981c: lui $a0, 0x68db
80049820: ori $a0, $a0, 0x8bad
80049824: mult $v0, $a0
80049828: mfhi $v1
8004982c: sra $a0, $v1, 0xc
80049830: sra $v1, $v0, 0x1f
80049834: subu $v0, $a0, $v1
80049838: negu $v1, $v0
8004983c: lui $at, 0x800e
80049840: sw $v1, 0x4004($at)
800498c8: addiu $sp, $sp, -0x58
800498cc: sw $ra, 0x54($sp)
800498d0: sw $fp, 0x50($sp)
800498d4: move $fp, $sp
800498d8: addiu $a0, $fp, 0x10
800498dc: move $a1, $zero
800498e0: jal 0x8001bd78
800498e4: nop
800498e8: sw $v0, 0x38($fp)
800498ec: sw $zero, 0x40($fp)
800498f0: lui $at, 0x800d
800498f4: sh $zero, -0x271a($at)
800498f8: sh $zero, 0x44($fp)
800498fc: lh $v0, 0x44($fp)
80049900: lw $v1, 0x38($fp)
80049904: nop
80049908: slt $v0, $v0, $v1
8004990c: bnez $v0, 0x8004991c
80049910: nop
80049914: j 0x80049a60
80049918: nop
8004991c: lh $v0, 0x44($fp)
80049920: nop
80049924: move $v1, $v0
80049928: sll $v0, $v1, 2
8004992c: addiu $v1, $fp, 0x10
80049930: addu $v0, $v0, $v1
80049934: move $v1, $v0
80049938: lw $v0, ($v1)
8004993c: nop
80049940: sw $v0, 0x3c($fp)
80049944: lw $v0, 0x3c($fp)
80049948: nop
8004994c: move $a0, $v0
80049950: sll $v1, $a0, 2
80049954: addu $v1, $v1, $v0
80049958: sll $v0, $v1, 7
8004995c: subu $v0, $v0, $v1
80049960: sll $v1, $v0, 3
80049964: lui $at, 0x8013
80049968: addu $at, $at, $v1
8004996c: lb $v0, -0x4d08($at)
80049970: nop
80049974: beqz $v0, 0x800499ec
80049978: nop
8004997c: lw $v0, 0x3c($fp)
80049980: nop
80049984: move $a0, $v0
80049988: sll $v1, $a0, 2
8004998c: addu $v1, $v1, $v0
80049990: sll $v0, $v1, 7
80049994: subu $v0, $v0, $v1
80049998: sll $v1, $v0, 3
8004999c: lui $at, 0x8013
800499a0: addu $at, $at, $v1
800499a4: lhu $v0, -0x4d04($at)
800499a8: nop
800499ac: andi $v1, $v0, 0x8000
800499b0: andi $v0, $v1, 0xffff
800499b4: bnez $v0, 0x800499ec
800499b8: nop
800499bc: lw $v0, 0x3c($fp)
800499c0: nop
800499c4: move $a0, $v0
800499c8: sll $v1, $a0, 2
800499cc: addu $v1, $v1, $v0
800499d0: sll $v0, $v1, 7
800499d4: subu $v0, $v0, $v1
800499d8: sll $v1, $v0, 3
800499dc: lui $v0, 0x8013
800499e0: addiu $v0, $v0, -0x4d08
800499e4: addu $v1, $v0, $v1
800499e8: sw $v1, 0x48($fp)
800499ec: lw $v0, 0x48($fp)
800499f0: lw $v1, 0x40($fp)
800499f4: lw $v0, 0xde0($v0)
800499f8: nop
800499fc: addu $v1, $v1, $v0
80049a00: sw $v1, 0x40($fp)
80049a04: lw $v1, 0x48($fp)
80049a08: nop
80049a0c: lw $v0, 0xc68($v1)
80049a10: lui $a0, 0x6666
80049a14: ori $a0, $a0, 0x6667
80049a18: mult $v0, $a0
80049a1c: mfhi $v1
80049a20: sra $a0, $v1, 3
80049a24: sra $v1, $v0, 0x1f
80049a28: subu $v0, $a0, $v1
80049a2c: lui $v1, 0x800d
80049a30: lhu $v1, -0x271a($v1)
80049a34: nop
80049a38: addu $v1, $v1, $v0
80049a3c: lui $at, 0x800d
80049a40: sh $v1, -0x271a($at)
80049a44: lhu $v0, 0x44($fp)
80049a48: nop
80049a4c: addiu $v1, $v0, 1
80049a50: move $v0, $v1
80049a54: sh $v0, 0x44($fp)
80049a58: j 0x800498fc
80049a5c: nop
80049a60: move $a0, $zero
80049a64: jal 0x80020498
80049a68: nop
80049a6c: lw $v1, 0x40($fp)
80049a70: nop
80049a74: move $a1, $v1
80049a78: sll $a0, $a1, 1
80049a7c: addu $a0, $a0, $v1
80049a80: sll $a1, $a0, 3
80049a84: addu $a1, $a1, $v1
80049a88: sll $v1, $a1, 2
80049a8c: div $zero, $v1, $v0
80049a90: bnez $v0, 0x80049a9c
80049a94: nop
80049a98: break 7
80049a9c: addiu $at, $zero, -1
80049aa0: bne $v0, $at, 0x80049ab4
80049aa4: lui $at, 0x8000
80049aa8: bne $v1, $at, 0x80049ab4
80049aac: nop
80049ab0: break 6
80049ab4: mflo $v0
80049ab8: lui $at, 0x800d
80049abc: sw $v0, -0x26c8($at)
80049ac0: addiu $a0, $zero, 0x18
80049ac4: addiu $a1, $zero, 0x30
80049ac8: addiu $a2, $zero, 0x1cd
80049acc: jal 0x8004e494
80049ad0: nop
80049ad4: lui $v0, 0x800d
80049ad8: lh $v0, -0x271a($v0)
80049adc: lw $v1, 0x38($fp)
80049ae0: nop
80049ae4: div $zero, $v0, $v1
80049ae8: bnez $v1, 0x80049af4
80049aec: nop
80049af0: break 7
80049af4: addiu $at, $zero, -1
80049af8: bne $v1, $at, 0x80049b0c
80049afc: lui $at, 0x8000
80049b00: bne $v0, $at, 0x80049b0c
80049b04: nop
80049b08: break 6
80049b0c: mflo $v0
80049b10: lui $at, 0x800d
80049b14: sh $v0, -0x271a($at)
80049b18: addiu $a0, $zero, 0xa8
80049b1c: addiu $a1, $zero, 0x30
80049b20: addiu $a2, $zero, 0x1ce
80049b24: jal 0x8004e494
80049b28: nop
80049b2c: move $sp, $fp
80049b30: lw $ra, 0x54($sp)
80049b34: lw $fp, 0x50($sp)
80049b38: addiu $sp, $sp, 0x58
80049b3c: jr $ra
80049b40: nop
