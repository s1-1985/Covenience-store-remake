800109f4: .byte 0x80, 0x8d, 0x5b, 0x00
800109f8: .byte 0x80, 0x8d, 0x5b, 0x00
800109fc: .byte 0x00, 0x1b, 0xb7, 0x00
80010a00: .byte 0x00, 0x1b, 0xb7, 0x00
80010a04: .byte 0x80, 0xa8, 0x12, 0x01
80010a08: .byte 0x80, 0xa8, 0x12, 0x01
80010a0c: movf $zero, $zero, $fcc0
80010a10: sra $zero, $zero, 0
80010a14: lsa $zero, $zero, $zero, 1
80010a18: srl $zero, $zero, 0
80010a1c: sllv $zero, $zero, $zero
80010a20: srlv $zero, $zero, $zero
80043cf4: addiu $sp, $sp, -0xa0
80043cf8: sw $ra, 0x9c($sp)
80043cfc: sw $fp, 0x98($sp)
80043d00: move $fp, $sp
80043d04: sw $a0, 0xa0($fp)
80043d08: addiu $v0, $fp, 0x88
80043d0c: addiu $v1, $fp, 0x90
80043d10: addiu $a0, $zero, 6
80043d14: move $a1, $v0
80043d18: move $a2, $v1
80043d1c: jal 0x80013f7c
80043d20: nop
80043d24: lhu $a0, 0x88($fp)
80043d28: nop
80043d2c: andi $v1, $a0, 0xffff
80043d30: lui $a0, 0xffff
80043d34: and $v0, $v0, $a0
80043d38: or $v0, $v0, $v1
80043d3c: lhu $v1, 0x8a($fp)
80043d40: nop
80043d44: sll $a0, $v1, 0x10
80043d48: andi $v0, $v0, 0xffff
80043d4c: or $v0, $v0, $a0
80043d50: lhu $a1, 0x8c($fp)
80043d54: nop
80043d58: andi $a0, $a1, 0xffff
80043d5c: lui $a1, 0xffff
80043d60: and $v1, $v1, $a1
80043d64: or $v1, $v1, $a0
80043d68: lhu $a0, 0x8e($fp)
80043d6c: nop
80043d70: sll $a1, $a0, 0x10
80043d74: andi $v1, $v1, 0xffff
80043d78: or $v1, $v1, $a1
80043d7c: lhu $a1, 0x90($fp)
80043d80: nop
80043d84: andi $a0, $a1, 0xffff
80043d88: lui $a1, 0xffff
80043d8c: and $a3, $a3, $a1
80043d90: or $a3, $a3, $a0
80043d94: lhu $a0, 0x92($fp)
80043d98: nop
80043d9c: sll $a1, $a0, 0x10
80043da0: andi $a3, $a3, 0xffff
80043da4: or $a3, $a3, $a1
80043da8: addiu $a0, $sp, 0x10
80043dac: addiu $a1, $fp, 0x94
80043db0: lwl $t1, 3($a1)
80043db4: lwr $t1, ($a1)
80043db8: nop
80043dbc: swl $t1, 3($a0)
80043dc0: swr $t1, ($a0)
80043dc4: lui $a0, 0x8015
80043dc8: ori $a0, $a0, 0xea00
80043dcc: move $a1, $v0
80043dd0: move $a2, $v1
80043dd4: jal 0x80013eac
80043dd8: nop
80043ddc: addiu $v0, $zero, 0x30
80043de0: sh $v0, 0x38($fp)
80043de4: addiu $v0, $zero, 0x20
80043de8: sh $v0, 0x3a($fp)
80043dec: addiu $v0, $zero, 0xe
80043df0: sh $v0, 0x3c($fp)
80043df4: addiu $v0, $zero, 9
80043df8: sh $v0, 0x3e($fp)
80043dfc: sb $zero, 0x40($fp)
80043e00: addiu $a0, $zero, 4
80043e04: addiu $a1, $zero, 1
80043e08: jal 0x80018940
80043e0c: nop
80043e10: lhu $a0, 0x38($fp)
80043e14: nop
80043e18: andi $v1, $a0, 0xffff
80043e1c: lui $a0, 0xffff
80043e20: and $v0, $v0, $a0
80043e24: or $v0, $v0, $v1
80043e28: lhu $v1, 0x3a($fp)
80043e2c: nop
80043e30: sll $a0, $v1, 0x10
80043e34: andi $v0, $v0, 0xffff
80043e38: or $v0, $v0, $a0
80043e3c: lhu $a1, 0x3c($fp)
80043e40: nop
80043e44: andi $a0, $a1, 0xffff
80043e48: lui $a1, 0xffff
80043e4c: and $v1, $v1, $a1
80043e50: or $v1, $v1, $a0
80043e54: lhu $a0, 0x3e($fp)
80043e58: nop
80043e5c: sll $a1, $a0, 0x10
80043e60: andi $v1, $v1, 0xffff
80043e64: or $v1, $v1, $a1
80043e68: lhu $a1, 0x40($fp)
80043e6c: nop
80043e70: andi $a0, $a1, 0xffff
80043e74: lui $a1, 0xffff
80043e78: and $a2, $a2, $a1
80043e7c: or $a2, $a2, $a0
80043e80: move $a0, $v0
80043e84: move $a1, $v1
80043e88: jal 0x80017b18
80043e8c: nop
80043e90: sw $v0, 0x70($fp)
80043e94: jal 0x800419e0
80043e98: nop
80043e9c: sw $zero, 0x78($fp)
80043ea0: sw $zero, 0x74($fp)
80043ea4: lw $v0, 0x74($fp)
80043ea8: nop
80043eac: slti $v1, $v0, 3
80043eb0: bnez $v1, 0x80043ec0
80043eb4: nop
80043eb8: j 0x80044060
80043ebc: nop
80043ec0: sw $zero, 0x70($fp)
80043ec4: lw $v0, 0x70($fp)
80043ec8: nop
80043ecc: slti $v1, $v0, 2
80043ed0: bnez $v1, 0x80043ee0
80043ed4: nop
80043ed8: j 0x80044044
80043edc: nop
80043ee0: addiu $v0, $zero, 0x20
80043ee4: sh $v0, 0x50($fp)
80043ee8: addiu $v0, $zero, 0x20
80043eec: sh $v0, 0x52($fp)
80043ef0: lw $v0, 0x74($fp)
80043ef4: nop
80043ef8: move $a0, $v0
80043efc: sll $v1, $a0, 1
80043f00: addu $v1, $v1, $v0
80043f04: sll $v0, $v1, 4
80043f08: move $v1, $v0
80043f0c: addiu $v0, $v1, -0x40
80043f10: sh $v0, 0x4c($fp)
80043f14: lw $v0, 0x70($fp)
80043f18: nop
80043f1c: move $a0, $v0
80043f20: sll $v1, $a0, 2
80043f24: addu $v1, $v1, $v0
80043f28: sll $v0, $v1, 3
80043f2c: move $v1, $v0
80043f30: addiu $v0, $v1, -0x1c
80043f34: sh $v0, 0x4e($fp)
80043f38: addiu $v0, $zero, 0xd
80043f3c: sh $v0, 0x54($fp)
80043f40: lw $v1, 0x78($fp)
80043f44: nop
80043f48: andi $v0, $v1, 7
80043f4c: move $v1, $v0
80043f50: sll $v0, $v1, 5
80043f54: sb $v0, 0x56($fp)
80043f58: addiu $v0, $zero, 0x80
80043f5c: sb $v0, 0x57($fp)
80043f60: sh $zero, 0x58($fp)
80043f64: addiu $v0, $zero, 0x1ea
80043f68: sh $v0, 0x5a($fp)
80043f6c: lw $v0, 0x78($fp)
80043f70: lw $v1, 0xa0($fp)
80043f74: nop
80043f78: slt $v0, $v0, $v1
80043f7c: beqz $v0, 0x80043fa4
80043f80: nop
80043f84: addiu $v0, $zero, 0x80
80043f88: sb $v0, 0x5e($fp)
80043f8c: addiu $v0, $zero, 0x80
80043f90: sb $v0, 0x5d($fp)
80043f94: addiu $v0, $zero, 0x80
80043f98: sb $v0, 0x5c($fp)
80043f9c: j 0x80043fbc
80043fa0: nop
80043fa4: addiu $v0, $zero, 0x40
80043fa8: sb $v0, 0x5e($fp)
80043fac: addiu $v0, $zero, 0x40
80043fb0: sb $v0, 0x5d($fp)
80043fb4: addiu $v0, $zero, 0x40
80043fb8: sb $v0, 0x5c($fp)
80043fbc: addiu $v0, $zero, 1
80043fc0: sw $v0, 0x28($sp)
80043fc4: addiu $v0, $sp, 0x10
80043fc8: addiu $v1, $fp, 0x54
80043fcc: lw $t1, ($v1)
80043fd0: lw $t2, 4($v1)
80043fd4: lw $t3, 8($v1)
80043fd8: lw $t0, 0xc($v1)
80043fdc: sw $t1, ($v0)
80043fe0: sw $t2, 4($v0)
80043fe4: sw $t3, 8($v0)
80043fe8: sw $t0, 0xc($v0)
80043fec: lw $t1, 0x10($v1)
80043ff0: lw $t2, 0x14($v1)
80043ff4: sw $t1, 0x10($v0)
80043ff8: sw $t2, 0x14($v0)
80043ffc: lw $a1, 0x48($fp)
80044000: lw $a2, 0x4c($fp)
80044004: lw $a3, 0x50($fp)
80044008: lw $a0, 0x78($fp)
8004400c: jal 0x80041630
80044010: nop
80044014: lw $v1, 0x78($fp)
80044018: nop
8004401c: addiu $v0, $v1, 1
80044020: move $v1, $v0
80044024: sw $v1, 0x78($fp)
80044028: lw $v1, 0x70($fp)
8004402c: nop
80044030: addiu $v0, $v1, 1
80044034: move $v1, $v0
80044038: sw $v1, 0x70($fp)
8004403c: j 0x80043ec4
80044040: nop
80044044: lw $v1, 0x74($fp)
80044048: nop
8004404c: addiu $v0, $v1, 1
80044050: move $v1, $v0
80044054: sw $v1, 0x74($fp)
80044058: j 0x80043ea4
8004405c: nop
80044060: addiu $a0, $zero, 0x78
80044064: addiu $a1, $zero, 0x6c
80044068: jal 0x8004e938
8004406c: nop
80044070: jal 0x800157b4
80044074: nop
80044078: addiu $v0, $zero, 0x17
8004407c: sh $v0, 0x30($fp)
80044080: addiu $v0, $zero, 0x40
80044084: sh $v0, 0x32($fp)
80044088: addiu $v0, $zero, 0x30
8004408c: sh $v0, 0x34($fp)
80044090: lhu $a0, 0x30($fp)
80044094: nop
80044098: andi $v1, $a0, 0xffff
8004409c: lui $a0, 0xffff
800440a0: and $v0, $v0, $a0
800440a4: or $v0, $v0, $v1
800440a8: lhu $v1, 0x32($fp)
800440ac: nop
800440b0: sll $a0, $v1, 0x10
800440b4: andi $v0, $v0, 0xffff
800440b8: or $v0, $v0, $a0
800440bc: lhu $a1, 0x34($fp)
800440c0: nop
800440c4: andi $a0, $a1, 0xffff
800440c8: lui $a1, 0xffff
800440cc: and $v1, $v1, $a1
800440d0: or $v1, $v1, $a0
800440d4: lhu $a0, 0x36($fp)
800440d8: nop
800440dc: sll $a1, $a0, 0x10
800440e0: andi $v1, $v1, 0xffff
800440e4: or $v1, $v1, $a1
800440e8: move $a0, $v0
800440ec: move $a1, $v1
800440f0: jal 0x800155d0
800440f4: nop
800440f8: addiu $a0, $zero, 0xa
800440fc: addiu $a1, $zero, 1
80044100: jal 0x80018940
80044104: nop
80044108: jal 0x80018a5c
8004410c: nop
80044110: lw $a0, 0xa0($fp)
80044114: jal 0x80044154
80044118: nop
8004411c: sw $v0, 0x80($fp)
80044120: addiu $a0, $zero, 0x80e
80044124: move $a1, $zero
80044128: jal 0x80018940
8004412c: nop
80044130: lw $v0, 0x80($fp)
80044134: j 0x8004413c
80044138: nop
8004413c: move $sp, $fp
80044140: lw $ra, 0x9c($sp)
80044144: lw $fp, 0x98($sp)
80044148: addiu $sp, $sp, 0xa0
8004414c: jr $ra
80044150: nop
80044154: addiu $sp, $sp, -0x60
80044158: sw $ra, 0x5c($sp)
8004415c: sw $fp, 0x58($sp)
80044160: move $fp, $sp
80044164: sw $a0, 0x60($fp)
80044168: addiu $v0, $fp, 0x10
8004416c: addiu $v1, $fp, 0x10
80044170: lui $v0, 0x8001
80044174: addiu $v0, $v0, 0x9f4
80044178: lw $t0, ($v0)
8004417c: lw $t1, 4($v0)
80044180: lw $t2, 8($v0)
80044184: lw $a3, 0xc($v0)
80044188: sw $t0, ($v1)
8004418c: sw $t1, 4($v1)
80044190: sw $t2, 8($v1)
80044194: sw $a3, 0xc($v1)
80044198: lw $t0, 0x10($v0)
8004419c: lw $t1, 0x14($v0)
800441a0: sw $t0, 0x10($v1)
800441a4: sw $t1, 0x14($v1)
800441a8: addiu $v0, $fp, 0x28
800441ac: lui $v1, 0x8001
800441b0: addiu $v1, $v1, 0xa0c
800441b4: lw $t0, ($v1)
800441b8: lw $t1, 4($v1)
800441bc: lw $t2, 8($v1)
800441c0: lw $a3, 0xc($v1)
800441c4: sw $t0, ($v0)
800441c8: sw $t1, 4($v0)
800441cc: sw $t2, 8($v0)
800441d0: sw $a3, 0xc($v0)
800441d4: lw $t0, 0x10($v1)
800441d8: lw $t1, 0x14($v1)
800441dc: sw $t0, 0x10($v0)
800441e0: sw $t1, 0x14($v0)
800441e4: sw $zero, 0x4c($fp)
800441e8: sw $zero, 0x48($fp)
800441ec: sw $zero, 0x44($fp)
800441f0: sw $zero, 0x40($fp)
800441f4: lui $v0, 0x800e
800441f8: lhu $v0, -0x519a($v0)
800441fc: nop
80044200: addiu $v1, $v0, -2
80044204: lui $at, 0x800e
80044208: sh $v1, -0x519a($at)
8004420c: j 0x8004421c
80044210: nop
80044214: j 0x8004463c
80044218: nop
8004421c: lw $v0, 0x4c($fp)
80044220: nop
80044224: move $a0, $v0
80044228: sll $v1, $a0, 1
8004422c: addu $v1, $v1, $v0
80044230: sll $v0, $v1, 2
80044234: addiu $v1, $fp, 0x10
80044238: addu $v0, $v0, $v1
8004423c: addiu $v1, $v0, 0x18
80044240: move $v0, $v1
80044244: lw $v1, 0x48($fp)
80044248: nop
8004424c: move $a0, $v1
80044250: sll $v1, $a0, 2
80044254: addu $v0, $v1, $v0
80044258: move $v1, $v0
8004425c: lw $v0, ($v1)
80044260: nop
80044264: sw $v0, 0x40($fp)
80044268: lw $v1, 0x40($fp)
8004426c: nop
80044270: addiu $v0, $v1, -1
80044274: move $v1, $v0
80044278: sw $v1, 0x40($fp)
8004427c: jal 0x800157b4
80044280: nop
80044284: addiu $a0, $zero, 0x40
80044288: addiu $a1, $zero, 0x30
8004428c: addiu $a2, $zero, 0x17
80044290: jal 0x8004e494
80044294: nop
80044298: lw $v0, 0x40($fp)
8004429c: nop
800442a0: move $v1, $v0
800442a4: sll $v0, $v1, 2
800442a8: addiu $v1, $fp, 0x10
800442ac: addu $v0, $v0, $v1
800442b0: move $v1, $v0
800442b4: lw $v0, ($v1)
800442b8: lui $at, 0x800e
800442bc: sw $v0, 0x4000($at)
800442c0: lui $a0, 0x800e
800442c4: lw $a0, 0x4000($a0)
800442c8: jal 0x80065820
800442cc: nop
800442d0: addiu $v1, $zero, 0xb
800442d4: subu $v0, $v1, $v0
800442d8: move $v1, $v0
800442dc: sll $v0, $v1, 3
800442e0: sw $v0, 0x54($fp)
800442e4: lhu $v0, 0x54($fp)
800442e8: nop
800442ec: addiu $v1, $v0, 0xa0
800442f0: sll $a0, $v1, 0x10
800442f4: sra $v0, $a0, 0x10
800442f8: move $a0, $v0
800442fc: addiu $a1, $zero, 0x40
80044300: addiu $a2, $zero, 0x110
80044304: jal 0x8004e494
80044308: nop
8004430c: lw $v0, 0x40($fp)
80044310: lw $v1, 0x44($fp)
80044314: nop
80044318: beq $v0, $v1, 0x800443cc
8004431c: nop
80044320: lw $v0, 0x44($fp)
80044324: nop
80044328: move $a0, $v0
8004432c: sll $v1, $a0, 3
80044330: addu $v1, $v1, $v0
80044334: sll $v0, $v1, 2
80044338: lw $v1, 0x44($fp)
8004433c: nop
80044340: move $a1, $v1
80044344: sll $a0, $a1, 3
80044348: addu $a0, $a0, $v1
8004434c: sll $v1, $a0, 2
80044350: lui $at, 0x800e
80044354: addu $at, $at, $v1
80044358: lhu $a0, -0x519a($at)
8004435c: nop
80044360: addiu $v1, $a0, 2
80044364: lui $at, 0x800e
80044368: addu $at, $at, $v0
8004436c: sh $v1, -0x519a($at)
80044370: lw $v0, 0x40($fp)
80044374: nop
80044378: sw $v0, 0x44($fp)
8004437c: lw $v0, 0x44($fp)
80044380: nop
80044384: move $a0, $v0
80044388: sll $v1, $a0, 3
8004438c: addu $v1, $v1, $v0
80044390: sll $v0, $v1, 2
80044394: lw $v1, 0x44($fp)
80044398: nop
8004439c: move $a1, $v1
800443a0: sll $a0, $a1, 3
800443a4: addu $a0, $a0, $v1
800443a8: sll $v1, $a0, 2
800443ac: lui $at, 0x800e
800443b0: addu $at, $at, $v1
800443b4: lhu $a0, -0x519a($at)
800443b8: nop
800443bc: addiu $v1, $a0, -2
800443c0: lui $at, 0x800e
800443c4: addu $at, $at, $v0
800443c8: sh $v1, -0x519a($at)
800443cc: move $a0, $zero
800443d0: jal 0x80041374
800443d4: nop
8006e998: lui $v0, 0x800d
8006e99c: lb $v0, -0x266c($v0)
8006e9a0: nop
8006e9a4: slti $v1, $v0, 3
8006e9a8: beqz $v1, 0x8006e9c0
8006e9ac: nop
8006e9b0: addiu $v0, $zero, 2
8006e9b4: sw $v0, 0x18($fp)
8006e9b8: j 0x8006e9f0
8006e9bc: nop
8006e9c0: lui $v0, 0x800d
8006e9c4: lb $v0, -0x266c($v0)
8006e9c8: nop
8006e9cc: slti $v1, $v0, 5
8006e9d0: beqz $v1, 0x8006e9e8
8006e9d4: nop
8006e9d8: addiu $v0, $zero, 4
8006e9dc: sw $v0, 0x18($fp)
8006e9e0: j 0x8006e9f0
8006e9e4: nop
8006e9e8: addiu $v0, $zero, 6
8006e9ec: sw $v0, 0x18($fp)
8006e9f0: lw $a0, 0x18($fp)
8006e9f4: jal 0x80043cf4
8006e9f8: nop
