80010bac: add $zero, $zero, $t8
80010bb0: .byte 0x10, 0x00, 0x0c, 0x00
80010bb4: nop
80067cf0: jal 0x80065974
80067cf4: nop
80067cf8: lhu $a0, 0x38($fp)
80067cfc: nop
80067d00: andi $v1, $a0, 0xffff
80067d04: lui $a0, 0xffff
80067d08: and $v0, $v0, $a0
80067d0c: or $v0, $v0, $v1
80067d10: lhu $v1, 0x3a($fp)
80067d14: nop
80067d18: sll $a0, $v1, 0x10
80067d1c: andi $v0, $v0, 0xffff
80067d20: or $v0, $v0, $a0
80067d24: lhu $a1, 0x3c($fp)
80067d28: nop
80067d2c: andi $a0, $a1, 0xffff
80067d30: lui $a1, 0xffff
80067d34: and $v1, $v1, $a1
80067d38: or $v1, $v1, $a0
80067d3c: lhu $a0, 0x3e($fp)
80067d40: nop
80067d44: sll $a1, $a0, 0x10
80067d48: andi $v1, $v1, 0xffff
80067d4c: or $v1, $v1, $a1
80067d50: lhu $a1, 0x40($fp)
80067d54: nop
80067d58: andi $a0, $a1, 0xffff
80067d5c: lui $a1, 0xffff
80067d60: and $a2, $a2, $a1
80067d64: or $a2, $a2, $a0
80067d68: move $a0, $v0
80067d6c: move $a1, $v1
80067d70: jal 0x80017b18
80067d74: nop
80067d78: addiu $a0, $zero, 0x30
80067d7c: addiu $a1, $zero, 0x28
80067d80: lui $a2, 0x800c
80067d84: addiu $a2, $a2, -0x6d10
80067d88: jal 0x80067338
80067d8c: nop
80067d90: lw $v0, 0x1c($fp)
80067d94: addiu $v1, $zero, 2
80067d98: bne $v0, $v1, 0x80067db8
80067d9c: nop
80067da0: addiu $v0, $zero, 3
80067da4: sw $v0, 0x18($fp)
80067da8: addiu $v0, $zero, 3
80067dac: sw $v0, 0x30($fp)
80067db0: j 0x80067dc8
80067db4: nop
80067db8: addiu $v0, $zero, 5
80067dbc: sw $v0, 0x18($fp)
80067dc0: addiu $v0, $zero, 5
80067dc4: sw $v0, 0x30($fp)
80067dc8: sw $zero, 0x14($fp)
80067dcc: lw $v0, 0x14($fp)
80067dd0: nop
80067dd4: slti $v1, $v0, 0xf
80067dd8: beqz $v1, 0x80067e14
80067ddc: nop
80067de0: lw $v0, 0x1c($fp)
80067de4: nop
80067de8: move $a0, $v0
80067dec: sll $v1, $a0, 4
80067df0: subu $v1, $v1, $v0
80067df4: lw $a0, 0x14($fp)
80067df8: nop
80067dfc: addu $v0, $v1, $a0
80067e00: slti $v1, $v0, 0x27
80067e04: bnez $v1, 0x80067e1c
80067e08: nop
80067e0c: j 0x80067e14
80067e10: nop
80067e14: j 0x80067fec
80067e18: nop
80067e1c: lw $v0, 0x50($fp)
80067e20: nop
80067e24: lb $v1, 0xc74($v0)
80067e28: nop
80067e2c: bnez $v1, 0x80067edc
80067e30: nop
80067e34: lw $v0, 0x1c($fp)
80067e38: nop
80067e3c: move $a0, $v0
80067e40: sll $v1, $a0, 4
80067e44: subu $v1, $v1, $v0
80067e48: lw $a0, 0x14($fp)
80067e4c: nop
80067e50: addu $v0, $v1, $a0
80067e54: move $v1, $v0
80067e58: sll $v0, $v1, 2
80067e5c: lui $v1, 0x800c
80067e60: addiu $v1, $v1, -0x66e0
80067e64: addu $v0, $v0, $v1
80067e68: move $v1, $v0
80067e6c: lw $v0, ($v1)
80067e70: addiu $v1, $zero, 0x1b
80067e74: beq $v0, $v1, 0x80067ecc
80067e78: nop
80067e7c: lw $v0, 0x1c($fp)
80067e80: nop
80067e84: move $a0, $v0
80067e88: sll $v1, $a0, 4
80067e8c: subu $v1, $v1, $v0
80067e90: lw $a0, 0x14($fp)
80067e94: nop
80067e98: addu $v0, $v1, $a0
80067e9c: move $v1, $v0
80067ea0: sll $v0, $v1, 2
80067ea4: lui $v1, 0x800c
80067ea8: addiu $v1, $v1, -0x66e0
80067eac: addu $v0, $v0, $v1
80067eb0: move $v1, $v0
80067eb4: lw $v0, ($v1)
80067eb8: addiu $v1, $zero, 0x1c
80067ebc: beq $v0, $v1, 0x80067ecc
80067ec0: nop
80067ec4: j 0x80067edc
80067ec8: nop
80067ecc: addiu $v0, $zero, 1
80067ed0: sw $v0, 0x24($fp)
80067ed4: j 0x80067ee0
80067ed8: nop
80067edc: sw $zero, 0x24($fp)
80067ee0: lw $v0, 0x14($fp)
80067ee4: lw $v1, 0x18($fp)
80067ee8: nop
80067eec: div $zero, $v0, $v1
80067ef0: bnez $v1, 0x80067efc
80067ef4: nop
80067ef8: break 7
80067efc: addiu $at, $zero, -1
80067f00: bne $v1, $at, 0x80067f14
80067f04: lui $at, 0x8000
80067f08: bne $v0, $at, 0x80067f14
80067f0c: nop
80067f10: break 6
80067f14: mfhi $v0
80067f18: nop
80067f1c: move $a0, $v0
80067f20: sll $v1, $a0, 2
80067f24: addu $v1, $v1, $v0
80067f28: sll $a0, $v1, 3
80067f2c: addiu $v0, $a0, 0x2c
80067f30: lw $v1, 0x14($fp)
80067f34: lw $a0, 0x18($fp)
80067f38: nop
80067f3c: div $zero, $v1, $a0
80067f40: bnez $a0, 0x80067f4c
80067f44: nop
80067f48: break 7
80067f4c: addiu $at, $zero, -1
80067f50: bne $a0, $at, 0x80067f64
80067f54: lui $at, 0x8000
80067f58: bne $v1, $at, 0x80067f64
80067f5c: nop
80067f60: break 6
80067f64: mflo $v1
80067f68: nop
80067f6c: move $a1, $v1
80067f70: sll $a0, $a1, 2
80067f74: addu $a0, $a0, $v1
80067f78: sll $a1, $a0, 3
80067f7c: addiu $v1, $a1, 0x48
80067f80: lw $a0, 0x1c($fp)
80067f84: nop
80067f88: move $a2, $a0
80067f8c: sll $a1, $a2, 4
80067f90: subu $a1, $a1, $a0
80067f94: lw $a2, 0x14($fp)
80067f98: nop
80067f9c: addu $a0, $a1, $a2
80067fa0: move $a1, $a0
80067fa4: sll $a0, $a1, 2
80067fa8: lui $a1, 0x800c
80067fac: addiu $a1, $a1, -0x66e0
80067fb0: addu $a0, $a0, $a1
80067fb4: move $a2, $a0
80067fb8: move $a0, $v0
80067fbc: move $a1, $v1
80067fc0: lw $a2, ($a2)
80067fc4: lw $a3, 0x24($fp)
80067fc8: jal 0x800687c4
80067fcc: nop
80067fd0: lw $v1, 0x14($fp)
80067fd4: nop
80067fd8: addiu $v0, $v1, 1
80067fdc: move $v1, $v0
80067fe0: sw $v1, 0x14($fp)
80067fe4: j 0x80067dcc
80067fe8: nop
80067fec: lw $v0, 0x20($fp)
80067ff0: lw $v1, 0x18($fp)
80067ff4: nop
80067ff8: div $zero, $v0, $v1
80067ffc: bnez $v1, 0x80068008
80068000: nop
80068004: break 7
80068008: addiu $at, $zero, -1
8006800c: bne $v1, $at, 0x80068020
80068010: lui $at, 0x8000
80068014: bne $v0, $at, 0x80068020
80068018: nop
8006801c: break 6
80068020: mfhi $v0
80068024: nop
80068028: move $a0, $v0
8006802c: sll $v1, $a0, 2
80068030: addu $v1, $v1, $v0
80068034: sll $v0, $v1, 3
80068038: move $v1, $v0
8006803c: addiu $v0, $v1, 0x50
80068040: sll $v1, $v0, 0x10
80068044: sra $v0, $v1, 0x10
80068048: lw $v1, 0x20($fp)
8006804c: lw $a0, 0x18($fp)
80068050: nop
80068054: div $zero, $v1, $a0
80068058: bnez $a0, 0x80068064
8006805c: nop
80068060: break 7
80068064: addiu $at, $zero, -1
80068068: bne $a0, $at, 0x8006807c
8006806c: lui $at, 0x8000
80068070: bne $v1, $at, 0x8006807c
80068074: nop
80068078: break 6
8006807c: mflo $v1
80068080: nop
80068084: move $a1, $v1
80068088: sll $a0, $a1, 2
8006808c: addu $a0, $a0, $v1
80068090: sll $v1, $a0, 3
80068094: move $a0, $v1
80068098: addiu $v1, $a0, 0x6c
8006809c: sll $a0, $v1, 0x10
800680a0: sra $v1, $a0, 0x10
800680a4: move $a0, $v0
800680a8: move $a1, $v1
800680ac: jal 0x8005fdd4
800680b0: nop
800680b4: lw $v0, 0x1c($fp)
800680b8: nop
800680bc: move $a0, $v0
800680c0: sll $v1, $a0, 4
800680c4: subu $v1, $v1, $v0
800680c8: lw $a0, 0x20($fp)
800680cc: nop
800680d0: addu $v0, $v1, $a0
800680d4: move $v1, $v0
800680d8: sll $v0, $v1, 2
800680dc: lui $v1, 0x800c
800680e0: addiu $v1, $v1, -0x66e0
800680e4: addu $v0, $v0, $v1
800680e8: move $v1, $v0
800680ec: lw $v0, ($v1)
800680f0: nop
800680f4: sw $v0, 0x28($fp)
800680f8: lw $v1, 0x28($fp)
800680fc: nop
80068100: addiu $v0, $v1, 0x183
80068104: addiu $a0, $zero, 0x30
80068108: addiu $a1, $zero, 0x38
8006810c: move $a2, $v0
80068110: jal 0x8004e494
80068114: nop
80068118: addiu $a0, $zero, 0x9a
8006811c: addiu $a1, $zero, 0x48
80068120: lui $a2, 0x800c
80068124: addiu $a2, $a2, -0x6b7c
80068128: jal 0x80067338
8006812c: nop
80068130: lw $v0, 0x28($fp)
80068134: nop
80068138: move $a0, $v0
8006813c: sll $v1, $a0, 1
80068140: addu $v1, $v1, $v0
80068144: sll $a0, $v1, 4
80068148: addu $a0, $a0, $v0
8006814c: sll $v1, $a0, 2
80068150: lui $at, 0x800a
80068154: addu $at, $at, $v1
80068158: lw $v0, -0x60ec($at)
8006815c: nop
80068160: move $a0, $v0
80068164: sll $v1, $a0, 1
80068168: addu $v1, $v1, $v0
8006816c: sll $v0, $v1, 3
80068170: lui $at, 0x800e
80068174: sw $v0, 0x4000($at)
80068178: lui $a0, 0x800e
8006817c: lw $a0, 0x4000($a0)
80068180: jal 0x80065820
80068184: nop
80068188: addiu $v1, $zero, 8
8006818c: subu $v0, $v1, $v0
80068190: move $v1, $v0
80068194: sll $v0, $v1, 3
80068198: sw $v0, 0x2c($fp)
8006819c: lw $v1, 0x2c($fp)
800681a0: nop
800681a4: addiu $v0, $v1, 0xb6
800681a8: move $a0, $v0
800681ac: addiu $a1, $zero, 0x48
800681b0: addiu $a2, $zero, 0x128
800681b4: jal 0x8004e494
800681b8: nop
800681bc: addiu $a0, $zero, 0xc8
800681c0: addiu $a1, $zero, 0x28
800681c4: lui $a2, 0x800c
800681c8: addiu $a2, $a2, -0x6c64
800681cc: jal 0x80067338
800681d0: nop
800681d4: lw $v0, 0x28($fp)
800681d8: nop
800681dc: move $a0, $v0
800681e0: sll $v1, $a0, 1
800681e4: addu $v1, $v1, $v0
800681e8: sll $a0, $v1, 4
800681ec: addu $a0, $a0, $v0
800681f0: sll $v0, $a0, 2
800681f4: lui $at, 0x800a
800681f8: addu $at, $at, $v0
800681fc: lw $v1, -0x60e8($at)
80068200: lui $at, 0x800d
80068204: sw $v1, -0x26c8($at)
80068208: addiu $a0, $zero, 0xf0
8006820c: addiu $a1, $zero, 0x28
80068210: addiu $a2, $zero, 0x171
80068214: jal 0x8004e494
80068218: nop
8006821c: addiu $a0, $zero, 0xc8
80068220: addiu $a1, $zero, 0x38
80068224: lui $a2, 0x800c
80068228: addiu $a2, $a2, -0x6c5c
8006822c: jal 0x80067338
80068230: nop
80068234: lw $v0, 0x28($fp)
80068238: nop
8006823c: move $a0, $v0
80068240: sll $v1, $a0, 1
80068244: addu $v1, $v1, $v0
80068248: sll $a0, $v1, 4
8006824c: addu $a0, $a0, $v0
80068250: sll $v0, $a0, 2
80068254: lui $at, 0x800a
80068258: addu $at, $at, $v0
8006825c: lw $v1, -0x60e4($at)
80068260: lui $at, 0x800d
80068264: sw $v1, -0x26c8($at)
80068268: addiu $a0, $zero, 0xf0
8006826c: addiu $a1, $zero, 0x38
80068270: addiu $a2, $zero, 0x171
80068274: jal 0x8004e494
80068278: nop
8006827c: addiu $a0, $zero, 0x30
80068280: addiu $a1, $zero, 0x48
80068284: lui $a2, 0x800c
80068288: addiu $a2, $a2, -0x6b74
8006828c: jal 0x80067338
80068290: nop
80068294: lw $v0, 0x28($fp)
80068298: nop
8006829c: move $a0, $v0
800682a0: sll $v1, $a0, 1
800682a4: addu $v1, $v1, $v0
800682a8: sll $a0, $v1, 4
800682ac: addu $a0, $a0, $v0
800682b0: sll $v0, $a0, 2
800682b4: lui $at, 0x800a
800682b8: addu $at, $at, $v0
800682bc: lw $v1, -0x60f0($at)
800682c0: lui $at, 0x800e
800682c4: sw $v1, 0x4004($at)
800682c8: lui $a0, 0x800e
800682cc: lw $a0, 0x4004($a0)
800682d0: jal 0x80065820
800682d4: nop
800682d8: addiu $v1, $zero, 6
800682dc: subu $v0, $v1, $v0
800682e0: move $v1, $v0
800682e4: sll $v0, $v1, 3
800682e8: sw $v0, 0x2c($fp)
800682ec: lw $v1, 0x2c($fp)
800682f0: nop
800682f4: addiu $v0, $v1, 0x4a
800682f8: move $a0, $v0
800682fc: addiu $a1, $zero, 0x48
80068300: addiu $a2, $zero, 0x1c
80068304: jal 0x8004e494
80068308: nop
8006830c: lw $v0, 0x10($fp)
80068310: nop
80068314: bnez $v0, 0x80068324
80068318: nop
8006831c: jal 0x80065690
80068320: nop
80068324: addiu $v0, $zero, 1
80068328: sw $v0, 0x10($fp)
8006832c: move $a0, $zero
80068330: jal 0x80041374
80068334: nop
800687c4: addiu $sp, $sp, -0x68
800687c8: sw $ra, 0x64($sp)
800687cc: sw $fp, 0x60($sp)
800687d0: move $fp, $sp
800687d4: sw $a0, 0x68($fp)
800687d8: sw $a1, 0x6c($fp)
800687dc: sw $a2, 0x70($fp)
800687e0: sw $a3, 0x74($fp)
800687e4: lw $v0, 0x70($fp)
800687e8: nop
800687ec: move $a0, $v0
800687f0: sll $v1, $a0, 1
800687f4: addu $v1, $v1, $v0
800687f8: sll $a0, $v1, 4
800687fc: addu $a0, $a0, $v0
80068800: sll $v0, $a0, 2
80068804: lui $at, 0x800a
80068808: addu $at, $at, $v0
8006880c: lw $v1, -0x60a4($at)
80068810: nop
80068814: sw $v1, 0x30($fp)
80068818: addiu $v0, $zero, 0x20
8006881c: sh $v0, 0x42($fp)
80068820: addiu $v0, $zero, 0x20
80068824: sh $v0, 0x40($fp)
80068828: addiu $v0, $zero, 0x19
8006882c: sh $v0, 0x44($fp)
80068830: lhu $v0, 0x68($fp)
80068834: nop
80068838: addiu $v1, $v0, -0x90
8006883c: sh $v1, 0x3c($fp)
80068840: lhu $v0, 0x6c($fp)
80068844: nop
80068848: addiu $v1, $v0, -0x60
8006884c: sh $v1, 0x3e($fp)
80068850: lw $v0, 0x30($fp)
80068854: nop
80068858: move $v1, $v0
8006885c: bgez $v1, 0x80068868
80068860: nop
80068864: addiu $v1, $v1, 7
80068868: sra $v1, $v1, 3
8006886c: move $a0, $v1
80068870: sll $v1, $a0, 3
80068874: subu $v0, $v0, $v1
80068878: move $v1, $v0
8006887c: sll $v0, $v1, 5
80068880: sb $v0, 0x46($fp)
80068884: lw $v1, 0x30($fp)
80068888: nop
8006888c: move $v0, $v1
80068890: bgez $v0, 0x8006889c
80068894: nop
80068898: addiu $v0, $v0, 7
8006889c: sra $v0, $v0, 3
800688a0: move $v1, $v0
800688a4: sll $v0, $v1, 5
800688a8: sb $v0, 0x47($fp)
800688ac: sh $zero, 0x48($fp)
800688b0: addiu $v0, $zero, 0x1eb
800688b4: sh $v0, 0x4a($fp)
800688b8: lw $v0, 0x74($fp)
800688bc: nop
800688c0: bnez $v0, 0x800688e8
800688c4: nop
800688c8: addiu $v0, $zero, 0x80
800688cc: sb $v0, 0x4e($fp)
800688d0: addiu $v0, $zero, 0x80
800688d4: sb $v0, 0x4d($fp)
800688d8: addiu $v0, $zero, 0x80
800688dc: sb $v0, 0x4c($fp)
800688e0: j 0x80068900
800688e4: nop
800688e8: addiu $v0, $zero, 0x40
800688ec: sb $v0, 0x4e($fp)
800688f0: addiu $v0, $zero, 0x40
800688f4: sb $v0, 0x4d($fp)
800688f8: addiu $v0, $zero, 0x40
800688fc: sb $v0, 0x4c($fp)
80068900: lui $v0, 0x800d
80068904: lh $v0, -0x25cc($v0)
80068908: addiu $v1, $zero, 1
8006890c: sw $v1, 0x28($sp)
80068910: addiu $v1, $sp, 0x10
80068914: addiu $a0, $fp, 0x44
80068918: lw $t1, ($a0)
8006891c: lw $t2, 4($a0)
80068920: lw $t3, 8($a0)
80068924: lw $t0, 0xc($a0)
80068928: sw $t1, ($v1)
8006892c: sw $t2, 4($v1)
80068930: sw $t3, 8($v1)
80068934: sw $t0, 0xc($v1)
80068938: lw $t1, 0x10($a0)
8006893c: lw $t2, 0x14($a0)
80068940: sw $t1, 0x10($v1)
80068944: sw $t2, 0x14($v1)
80068948: lw $a1, 0x38($fp)
8006894c: lw $a2, 0x3c($fp)
80068950: lw $a3, 0x40($fp)
80068954: move $a0, $v0
80068958: jal 0x80041630
8006895c: nop
80068960: move $sp, $fp
80068964: lw $ra, 0x64($sp)
80068968: lw $fp, 0x60($sp)
8006896c: addiu $sp, $sp, 0x68
80068970: jr $ra
80068974: nop
800b9920: negu $zero, $zero
800b9924: and $zero, $zero, $zero
800b9928: .byte 0x16, 0x00, 0x00, 0x00
800b992c: .byte 0x17, 0x00, 0x00, 0x00
800b9930: mult $zero, $zero
800b9934: nop
800b9938: movf $zero, $zero, $fcc0
800b993c: srl $zero, $zero, 0
800b9940: sra $zero, $zero, 0
800b9944: sllv $zero, $zero, $zero
800b9948: lsa $zero, $zero, $zero, 1
800b994c: srlv $zero, $zero, $zero
800b9950: srav $zero, $zero, $zero
800b9954: jr $zero
800b9958: jr $zero
800b995c: movz $zero, $zero, $zero
800b9960: movn $zero, $zero, $zero
800b9964: syscall
800b9968: break
800b996c: .byte 0x0e, 0x00, 0x00, 0x00
800b9970: sync
800b9974: mfhi $zero
800b9978: mthi $zero
800b997c: multu $zero, $zero
800b9980: div $zero, $zero, $zero
800b9984: divu $zero, $zero, $zero
800b9988: .byte 0x1c, 0x00, 0x00, 0x00
800b998c: .byte 0x1d, 0x00, 0x00, 0x00
800b9990: .byte 0x1e, 0x00, 0x00, 0x00
800b9994: .byte 0x1f, 0x00, 0x00, 0x00
800b9998: add $zero, $zero, $zero
800b999c: sltu $zero, $zero, $zero
800b99a0: .byte 0x2c, 0x00, 0x00, 0x00
800b99a4: .byte 0x2d, 0x00, 0x00, 0x00
800b99a8: .byte 0x2e, 0x00, 0x00, 0x00
800b99ac: .byte 0x2f, 0x00, 0x00, 0x00
800b99b0: tlt $zero, $zero
800b99b4: tltu $zero, $zero
800b99b8: teq $zero, $zero
