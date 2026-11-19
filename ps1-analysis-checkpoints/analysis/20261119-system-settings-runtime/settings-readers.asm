80029e44: lui $v0, 0x800d
80029e48: lb $v0, -0x27cb($v0)
80029e4c: nop
80029e50: beqz $v0, 0x80029fc8
80029e54: nop
80029e58: lw $v0, 0x18($fp)
80029e5c: nop
80029e60: lw $v1, 0xd5c($v0)
80029e64: lui $v0, 0x2d
80029e68: ori $v0, $v0, 0xc6bf
80029e6c: slt $v1, $v0, $v1
80029e70: beqz $v1, 0x80029fc8
80029e74: nop
8004eeb8: addiu $sp, $sp, -0x20
8004eebc: sw $ra, 0x1c($sp)
8004eec0: sw $fp, 0x18($sp)
8004eec4: move $fp, $sp
8004eec8: addiu $v0, $zero, 2
8004eecc: sh $v0, 0x10($fp)
8004eed0: j 0x8004eee0
8004eed4: nop
8004eed8: j 0x8004efac
8004eedc: nop
8004eee0: lh $v0, 0x10($fp)
8004eee4: nop
8004eee8: move $a0, $v0
8004eeec: jal 0x8004efd0
8004eef0: nop
8004eef4: sh $v0, 0x10($fp)
8004eef8: lh $v0, 0x10($fp)
8004eefc: addiu $v1, $zero, 2
8004ef00: bne $v0, $v1, 0x8004ef18
8004ef04: nop
8004ef08: j 0x8004efac
8004ef0c: nop
8004ef10: j 0x8004efa4
8004ef14: nop
8004ef18: lh $v0, 0x10($fp)
8004ef1c: nop
8004ef20: beqz $v0, 0x8004ef3c
8004ef24: nop
8004ef28: addiu $v1, $zero, 1
8004ef2c: beq $v0, $v1, 0x8004ef70
8004ef30: nop
8004ef34: j 0x8004efa4
8004ef38: nop
8004ef3c: move $a0, $zero
8004ef40: jal 0x800501fc
8004ef44: nop
8004ef48: sw $v0, 0x14($fp)
8004ef4c: lw $v0, 0x14($fp)
8004ef50: nop
8004ef54: bnez $v0, 0x8004ef68
8004ef58: nop
8004ef5c: move $v0, $zero
8004ef60: j 0x8004efb8
8004ef64: nop
8004ef68: j 0x8004efa4
8004ef6c: nop
8004ef70: move $a0, $zero
8004ef74: jal 0x80051174
8004ef78: nop
8004ef7c: sw $v0, 0x14($fp)
8004ef80: lw $v0, 0x14($fp)
8004ef84: nop
8004ef88: bnez $v0, 0x8004ef9c
8004ef8c: nop
8004ef90: addiu $v0, $zero, 1
8004ef94: j 0x8004efb8
8004ef98: nop
8004ef9c: j 0x8004efa4
8004efa0: nop
8004efa4: j 0x8004eed0
8004efa8: nop
8004efac: addiu $v0, $zero, 2
8004efb0: j 0x8004efb8
8004efb4: nop
8004efb8: move $sp, $fp
8004efbc: lw $ra, 0x1c($sp)
8004efc0: lw $fp, 0x18($sp)
8004efc4: addiu $sp, $sp, 0x20
8004efc8: jr $ra
8004efcc: nop
8004efd0: addiu $sp, $sp, -0x48
8004efd4: sw $ra, 0x40($sp)
8004efd8: sw $fp, 0x3c($sp)
8004efdc: sw $s0, 0x38($sp)
8004efe0: move $fp, $sp
8004efe4: move $s0, $a0
8004efe8: sh $s0, 0x10($fp)
8004efec: addiu $a0, $zero, 0x1a
8004eff0: addiu $a1, $zero, 1
8004eff4: jal 0x80018940
8004eff8: nop
8004effc: addiu $v0, $zero, 0x30
8004f000: sh $v0, 0x20($fp)
8004f004: addiu $v0, $zero, 0x30
8004f008: sh $v0, 0x22($fp)
8004f00c: addiu $v0, $zero, 0xe
8004f010: sh $v0, 0x24($fp)
8004f014: addiu $v0, $zero, 8
8004f018: sh $v0, 0x26($fp)
8004f01c: sb $zero, 0x28($fp)
8004f020: addiu $a0, $zero, 4
8004f024: addiu $a1, $zero, 1
8004f028: jal 0x80018940
8004f02c: nop
8004f030: lhu $a0, 0x20($fp)
8004f034: nop
8004f038: andi $v1, $a0, 0xffff
8004f03c: lui $a0, 0xffff
8004f040: and $v0, $v0, $a0
8004f044: or $v0, $v0, $v1
8004f048: lhu $v1, 0x22($fp)
8004f04c: nop
8004f050: sll $a0, $v1, 0x10
8004f054: andi $v0, $v0, 0xffff
8004f058: or $v0, $v0, $a0
8004f05c: lhu $a1, 0x24($fp)
8004f060: nop
8004f064: andi $a0, $a1, 0xffff
8004f068: lui $a1, 0xffff
8004f06c: and $v1, $v1, $a1
8004f070: or $v1, $v1, $a0
8004f074: lhu $a0, 0x26($fp)
8004f078: nop
8004f07c: sll $a1, $a0, 0x10
8004f080: andi $v1, $v1, 0xffff
8004f084: or $v1, $v1, $a1
8004f088: lhu $a1, 0x28($fp)
8004f08c: nop
8004f090: andi $a0, $a1, 0xffff
8004f094: lui $a1, 0xffff
8004f098: and $a2, $a2, $a1
8004f09c: or $a2, $a2, $a0
8004f0a0: move $a0, $v0
8004f0a4: move $a1, $v1
8004f0a8: jal 0x80017b18
8004f0ac: nop
8004f0b0: jal 0x800157b4
8004f0b4: nop
8004f0b8: addiu $a0, $zero, 0x30
8004f0bc: addiu $a1, $zero, 0x30
8004f0c0: move $a2, $zero
8004f0c4: jal 0x8004f5c8
8004f0c8: nop
8004f0cc: lui $v0, 0x800d
8004f0d0: lhu $v0, -0x2768($v0)
8004f0d4: nop
8004f0d8: sh $v0, 0x1a($fp)
8004f0dc: lhu $v0, 0x1a($fp)
8004f0e0: nop
8004f0e4: andi $v1, $v0, 1
8004f0e8: sh $v1, 0x12($fp)
8004f0ec: lh $v0, 0x1a($fp)
8004f0f0: nop
8004f0f4: sra $v1, $v0, 1
8004f0f8: move $v0, $v1
8004f0fc: andi $v1, $v0, 1
8004f100: sh $v1, 0x16($fp)
8004f104: lh $v0, 0x1a($fp)
8004f108: nop
8004f10c: sra $v1, $v0, 8
8004f110: move $v0, $v1
8004f114: andi $v1, $v0, 3
8004f118: sh $v1, 0x14($fp)
8004f11c: lh $v0, 0x12($fp)
8004f120: lh $v1, 0x10($fp)
8004f124: move $a0, $v0
8004f128: move $a1, $v1
8004f12c: jal 0x8004fafc
8004f130: nop
8004f134: lh $v0, 0x10($fp)
8004f138: lh $v1, 0x1a($fp)
8004f13c: move $a0, $v0
8004f140: move $a1, $v1
8004f144: jal 0x8004fc8c
8004f148: nop
8004f14c: lhu $v0, 0x10($fp)
8004f150: nop
8004f154: sh $v0, 0x18($fp)
8004f158: addiu $v0, $zero, 2
8004f15c: sh $v0, 0x30($fp)
8004f160: j 0x8004f170
8004f164: nop
8004f168: j 0x8004f58c
8004f16c: nop
8004f170: move $a0, $zero
8004f174: jal 0x80041374
8004f178: nop
8004f17c: lui $v1, 0x800d
8004f180: lw $v1, -0x25f4($v1)
8004f184: nop
8004f188: andi $v0, $v1, 0x1000
8004f18c: beqz $v0, 0x8004f1b8
8004f190: nop
8004f194: lh $v0, 0x18($fp)
8004f198: nop
8004f19c: blez $v0, 0x8004f1b8
8004f1a0: nop
8004f1a4: lhu $v0, 0x18($fp)
8004f1a8: nop
8004f1ac: addiu $v1, $v0, -1
8004f1b0: move $v0, $v1
8004f1b4: sh $v0, 0x18($fp)
8004f1b8: lui $v1, 0x800d
8004f1bc: lw $v1, -0x25f4($v1)
8004f1c0: nop
8004f1c4: andi $v0, $v1, 0x4000
8004f1c8: beqz $v0, 0x8004f1f8
8004f1cc: nop
8004f1d0: lh $v0, 0x18($fp)
8004f1d4: nop
8004f1d8: slti $v1, $v0, 4
8004f1dc: beqz $v1, 0x8004f1f8
8004f1e0: nop
8004f1e4: lhu $v0, 0x18($fp)
8004f1e8: nop
8004f1ec: addiu $v1, $v0, 1
8004f1f0: move $v0, $v1
8004f1f4: sh $v0, 0x18($fp)
8004f1f8: lui $v1, 0x800d
8004f1fc: lw $v1, -0x25f4($v1)
8004f200: nop
8004f204: andi $v0, $v1, 0x2000
8004f208: beqz $v0, 0x8004f2dc
8004f20c: nop
8004f210: lh $v0, 0x18($fp)
8004f214: addiu $v1, $zero, 3
8004f218: beq $v0, $v1, 0x8004f280
8004f21c: nop
8004f220: slti $v1, $v0, 4
8004f224: beqz $v1, 0x8004f240
8004f228: nop
8004f22c: addiu $v1, $zero, 2
8004f230: beq $v0, $v1, 0x8004f254
8004f234: nop
8004f238: j 0x8004f2dc
8004f23c: nop
8004f240: addiu $v1, $zero, 4
8004f244: beq $v0, $v1, 0x8004f2b0
8004f248: nop
8004f24c: j 0x8004f2dc
8004f250: nop
8004f254: lh $v0, 0x12($fp)
8004f258: nop
8004f25c: bnez $v0, 0x8004f278
8004f260: nop
8004f264: lhu $v0, 0x12($fp)
8004f268: nop
8004f26c: addiu $v1, $v0, 1
8004f270: move $v0, $v1
8004f274: sh $v0, 0x12($fp)
8004f278: j 0x8004f2dc
8004f27c: nop
8004f280: lh $v0, 0x14($fp)
8004f284: nop
8004f288: slti $v1, $v0, 2
8004f28c: beqz $v1, 0x8004f2a8
8004f290: nop
8004f294: lhu $v0, 0x14($fp)
8004f298: nop
8004f29c: addiu $v1, $v0, 1
8004f2a0: move $v0, $v1
8004f2a4: sh $v0, 0x14($fp)
8004f2a8: j 0x8004f2dc
8004f2ac: nop
8004f2b0: lh $v0, 0x16($fp)
8004f2b4: nop
8004f2b8: bnez $v0, 0x8004f2d4
8004f2bc: nop
8004f2c0: lhu $v0, 0x16($fp)
8004f2c4: nop
8004f2c8: addiu $v1, $v0, 1
8004f2cc: move $v0, $v1
8004f2d0: sh $v0, 0x16($fp)
8004f2d4: j 0x8004f2dc
8004f2d8: nop
8004f2dc: lui $v1, 0x800d
8004f2e0: lw $v1, -0x25f4($v1)
8004f2e4: nop
8004f2e8: andi $v0, $v1, 0x8000
8004f2ec: beqz $v0, 0x8004f3bc
8004f2f0: nop
8004f2f4: lh $v0, 0x18($fp)
8004f2f8: addiu $v1, $zero, 3
8004f2fc: beq $v0, $v1, 0x8004f364
8004f300: nop
8004f304: slti $v1, $v0, 4
8004f308: beqz $v1, 0x8004f324
8004f30c: nop
8004f310: addiu $v1, $zero, 2
8004f314: beq $v0, $v1, 0x8004f338
8004f318: nop
8004f31c: j 0x8004f3bc
8004f320: nop
8004f324: addiu $v1, $zero, 4
8004f328: beq $v0, $v1, 0x8004f390
8004f32c: nop
8004f330: j 0x8004f3bc
8004f334: nop
8004f338: lh $v0, 0x12($fp)
8004f33c: addiu $v1, $zero, 1
8004f340: bne $v0, $v1, 0x8004f35c
8004f344: nop
8004f348: lhu $v0, 0x12($fp)
8004f34c: nop
8004f350: addiu $v1, $v0, -1
8004f354: move $v0, $v1
8004f358: sh $v0, 0x12($fp)
8004f35c: j 0x8004f3bc
8004f360: nop
8004f364: lh $v0, 0x14($fp)
8004f368: nop
8004f36c: blez $v0, 0x8004f388
8004f370: nop
8004f374: lhu $v0, 0x14($fp)
8004f378: nop
8004f37c: addiu $v1, $v0, -1
8004f380: move $v0, $v1
8004f384: sh $v0, 0x14($fp)
8004f388: j 0x8004f3bc
8004f38c: nop
8004f390: lh $v0, 0x16($fp)
8004f394: addiu $v1, $zero, 1
8004f398: bne $v0, $v1, 0x8004f3b4
8004f39c: nop
8004f3a0: lhu $v0, 0x16($fp)
8004f3a4: nop
8004f3a8: addiu $v1, $v0, -1
8004f3ac: move $v0, $v1
8004f3b0: sh $v0, 0x16($fp)
8004f3b4: j 0x8004f3bc
8004f3b8: nop
8004f3bc: lui $v1, 0x800d
8004f3c0: lw $v1, -0x25d8($v1)
8004f3c4: nop
8004f3c8: andi $v0, $v1, 0x20
8004f3cc: beqz $v0, 0x8004f41c
8004f3d0: nop
8004f3d4: jal 0x80065000
8004f3d8: nop
8004f3dc: lh $v0, 0x18($fp)
8004f3e0: nop
8004f3e4: beqz $v0, 0x8004f400
8004f3e8: nop
8004f3ec: addiu $v1, $zero, 1
8004f3f0: beq $v0, $v1, 0x8004f40c
8004f3f4: nop
8004f3f8: j 0x8004f41c
8004f3fc: nop
8004f400: sh $zero, 0x30($fp)
8004f404: j 0x8004f41c
8004f408: nop
8004f40c: addiu $v0, $zero, 1
8004f410: sh $v0, 0x30($fp)
8004f414: j 0x8004f41c
8004f418: nop
8004f41c: sh $zero, 0x1a($fp)
8004f420: lhu $v0, 0x1a($fp)
8004f424: lhu $v1, 0x12($fp)
8004f428: nop
8004f42c: or $v0, $v0, $v1
8004f430: sh $v0, 0x1a($fp)
8004f434: lhu $v0, 0x16($fp)
8004f438: nop
8004f43c: sll $v1, $v0, 1
8004f440: lhu $v0, 0x1a($fp)
8004f444: nop
8004f448: or $v0, $v0, $v1
8004f44c: sh $v0, 0x1a($fp)
8004f450: lhu $v0, 0x14($fp)
8004f454: nop
8004f458: sll $v1, $v0, 8
8004f45c: lhu $v0, 0x1a($fp)
8004f460: nop
8004f464: or $v0, $v0, $v1
8004f468: sh $v0, 0x1a($fp)
8004f46c: lh $v0, 0x18($fp)
8004f470: nop
8004f474: sltiu $v1, $v0, 5
8004f478: beqz $v1, 0x8004f534
8004f47c: nop
8004f480: sll $v1, $v0, 2
8004f484: lui $a0, 0x8001
8004f488: addiu $a0, $a0, 0xa3c
8004f48c: addu $v0, $v1, $a0
8004f490: move $v1, $v0
8004f494: lw $v0, ($v1)
8004f498: nop
8004f49c: jr $v0
8004f4a0: nop
8004f4a4: move $a0, $zero
8004f4a8: move $a1, $zero
8004f4ac: jal 0x8004fafc
8004f4b0: nop
8004f4b4: j 0x8004f534
8004f4b8: nop
8004f4bc: move $a0, $zero
8004f4c0: addiu $a1, $zero, 1
8004f4c4: jal 0x8004fafc
8004f4c8: nop
8004f4cc: j 0x8004f534
8004f4d0: nop
8004f4d4: lh $v0, 0x12($fp)
8004f4d8: nop
8004f4dc: move $a0, $v0
8004f4e0: addiu $a1, $zero, 2
8004f4e4: jal 0x8004fafc
8004f4e8: nop
8004f4ec: j 0x8004f534
8004f4f0: nop
8004f4f4: lh $v0, 0x14($fp)
8004f4f8: nop
8004f4fc: move $a0, $v0
8004f500: addiu $a1, $zero, 3
8004f504: jal 0x8004fafc
8004f508: nop
8004f50c: j 0x8004f534
8004f510: nop
8004f514: lh $v0, 0x16($fp)
8004f518: nop
8004f51c: move $a0, $v0
8004f520: addiu $a1, $zero, 4
8004f524: jal 0x8004fafc
8004f528: nop
8004f52c: j 0x8004f534
8004f530: nop
8004f534: lh $v0, 0x18($fp)
8004f538: lh $v1, 0x1a($fp)
8004f53c: move $a0, $v0
8004f540: move $a1, $v1
8004f544: jal 0x8004fc8c
8004f548: nop
8004f54c: lui $v1, 0x800d
8004f550: lw $v1, -0x25d8($v1)
8004f554: nop
8004f558: andi $v0, $v1, 0x800
8004f55c: beqz $v0, 0x8004f56c
8004f560: nop
8004f564: j 0x8004f58c
8004f568: nop
8004f56c: lh $v0, 0x30($fp)
8004f570: addiu $v1, $zero, 2
8004f574: beq $v0, $v1, 0x8004f584
8004f578: nop
8004f57c: j 0x8004f58c
8004f580: nop
8004f584: j 0x8004f160
8004f588: nop
8004f58c: lhu $v0, 0x1a($fp)
8004f590: lui $at, 0x800d
8004f594: sh $v0, -0x2768($at)
8004f598: lh $v1, 0x30($fp)
8004f59c: nop
8004f5a0: move $v0, $v1
8004f5a4: j 0x8004f5ac
8004f5a8: nop
8004f5ac: move $sp, $fp
8004f5b0: lw $ra, 0x40($sp)
8004f5b4: lw $fp, 0x3c($sp)
8004f5b8: lw $s0, 0x38($sp)
8004f5bc: addiu $sp, $sp, 0x48
8004f5c0: jr $ra
8004f5c4: nop
800625c4: lui $v0, 0x800d
800625c8: lhu $v0, -0x2768($v0)
800625cc: nop
800625d0: andi $v1, $v0, 1
800625d4: sll $a0, $v1, 0x10
800625d8: sra $v0, $a0, 0x10
800625dc: beqz $v0, 0x800625f4
800625e0: nop
800625e4: lui $at, 0x800d
800625e8: sb $zero, -0x27cc($at)
800625ec: j 0x80062600
800625f0: nop
800625f4: addiu $v0, $zero, 1
800625f8: lui $at, 0x800d
800625fc: sb $v0, -0x27cc($at)
80062600: lui $v0, 0x800d
80062604: lhu $v0, -0x2768($v0)
80062608: nop
8006260c: andi $v1, $v0, 2
80062610: sll $a0, $v1, 0x10
80062614: sra $v0, $a0, 0x10
80062618: beqz $v0, 0x80062630
8006261c: nop
80062620: lui $at, 0x800d
80062624: sb $zero, -0x27cb($at)
80062628: j 0x8006263c
8006262c: nop
80062630: addiu $v0, $zero, 1
80062634: lui $at, 0x800d
80062638: sb $v0, -0x27cb($at)
8006263c: lui $v0, 0x800d
80062640: lh $v0, -0x2768($v0)
80062644: nop
80062648: sra $v1, $v0, 8
8006264c: move $v0, $v1
80062650: addiu $v1, $v0, 1
80062654: lui $at, 0x800d
80062658: sb $v1, -0x2757($at)
8006265c: lui $v0, 0x800d
80062660: lb $v0, -0x2757($v0)
80062664: nop
80062668: move $v1, $v0
8006266c: sll $v0, $v1, 2
80062670: lui $v1, 0x800a
80062674: addiu $v1, $v1, -0x679c
80062678: addu $v0, $v0, $v1
8006267c: move $v1, $v0
80062680: lw $a0, ($v1)
80062684: move $a1, $zero
80062688: jal 0x80065100
8006268c: nop
80062690: jal 0x80065974
80062694: nop
80064d58: addiu $sp, $sp, -8
80064d5c: sw $fp, ($sp)
80064d60: move $fp, $sp
80064d64: addiu $v0, $zero, 1
80064d68: lui $at, 0x800d
80064d6c: sb $v0, -0x2757($at)
80064d70: addiu $v0, $zero, 1
80064d74: lui $at, 0x800d
80064d78: sb $v0, -0x27cc($at)
80064d7c: lui $at, 0x800d
80064d80: sb $zero, -0x27ca($at)
80064d84: addiu $v0, $zero, 1
80064d88: lui $at, 0x800d
80064d8c: sb $v0, -0x27cb($at)
80064d90: move $sp, $fp
80064d94: lw $fp, ($sp)
80064d98: addiu $sp, $sp, 8
80064d9c: jr $ra
80064da0: nop
80064e4c: addiu $sp, $sp, -0x20
80064e50: sw $ra, 0x1c($sp)
80064e54: sw $fp, 0x18($sp)
80064e58: move $fp, $sp
80064e5c: sw $a0, 0x20($fp)
80064e60: lui $v0, 0x800d
80064e64: lw $v0, -0x2670($v0)
80064e68: addiu $v1, $zero, 6
80064e6c: bne $v0, $v1, 0x80064e7c
80064e70: nop
80064e74: j 0x80064fe8
80064e78: nop
80064e7c: lw $v0, 0x20($fp)
80064e80: addiu $v1, $zero, -1
80064e84: bne $v0, $v1, 0x80064ef4
80064e88: nop
80064e8c: sw $zero, 0x10($fp)
80064e90: lw $v0, 0x10($fp)
80064e94: nop
80064e98: slti $v1, $v0, 0x10
80064e9c: bnez $v1, 0x80064eac
80064ea0: nop
80064ea4: j 0x80064ee4
80064ea8: nop
80064eac: lui $v0, 0x800d
80064eb0: lh $v0, -0x25d2($v0)
80064eb4: lh $v1, 0x10($fp)
80064eb8: move $a0, $v0
80064ebc: move $a1, $v1
80064ec0: jal 0x8008ed1c
80064ec4: nop
80064ec8: lw $v1, 0x10($fp)
80064ecc: nop
80064ed0: addiu $v0, $v1, 1
80064ed4: move $v1, $v0
80064ed8: sw $v1, 0x10($fp)
80064edc: j 0x80064e90
80064ee0: nop
80064ee4: jal 0x80064550
80064ee8: nop
80064eec: j 0x80064fe8
80064ef0: nop
80064ef4: lw $v0, 0x20($fp)
80064ef8: nop
80064efc: slti $v1, $v0, 0x10
80064f00: beqz $v1, 0x80064f48
80064f04: nop
80064f08: lui $v0, 0x800d
80064f0c: lb $v0, -0x27cc($v0)
80064f10: addiu $v1, $zero, 1
80064f14: bne $v0, $v1, 0x80064f48
80064f18: nop
80064f1c: lui $v0, 0x800d
80064f20: lh $v0, -0x25d2($v0)
80064f24: lh $v1, 0x20($fp)
80064f28: move $a0, $v0
80064f2c: move $a1, $v1
80064f30: addiu $a2, $zero, 1
80064f34: addiu $a3, $zero, 1
80064f38: jal 0x8008ea7c
80064f3c: nop
80064f40: j 0x80064fe8
80064f44: nop
80064f48: lw $v0, 0x20($fp)
80064f4c: nop
80064f50: slti $v1, $v0, 0x1c
80064f54: beqz $v1, 0x80064fac
80064f58: nop
80064f5c: lui $v0, 0x800d
80064f60: lb $v0, -0x27cc($v0)
80064f64: addiu $v1, $zero, 1
80064f68: bne $v0, $v1, 0x80064fac
80064f6c: nop
80064f70: lui $v0, 0x800d
80064f74: lh $v0, -0x2780($v0)
80064f78: lhu $v1, 0x20($fp)
80064f7c: nop
80064f80: addiu $a0, $v1, -0x10
80064f84: sll $a1, $a0, 0x10
80064f88: sra $v1, $a1, 0x10
80064f8c: move $a0, $v0
80064f90: move $a1, $v1
80064f94: addiu $a2, $zero, 1
80064f98: addiu $a3, $zero, 1
80064f9c: jal 0x8008ea7c
80064fa0: nop
80064fa4: j 0x80064fe8
80064fa8: nop
80064fac: lw $v0, 0x20($fp)
80064fb0: nop
80064fb4: slti $v1, $v0, 0x1c
80064fb8: bnez $v1, 0x80064fe8
80064fbc: nop
80064fc0: jal 0x80064550
80064fc4: nop
80064fc8: jal 0x80018a5c
80064fcc: nop
80064fd0: lw $v1, 0x20($fp)
80064fd4: nop
80064fd8: addiu $v0, $v1, -0x1c
80064fdc: move $a0, $v0
80064fe0: jal 0x80064740
80064fe4: nop
80064fe8: move $sp, $fp
80064fec: lw $ra, 0x1c($sp)
80064ff0: lw $fp, 0x18($sp)
80064ff4: addiu $sp, $sp, 0x20
80064ff8: jr $ra
80064ffc: nop
8006b8c0: lw $v0, 0x10($fp)
8006b8c4: lui $v1, 0x800d
8006b8c8: lbu $v1, -0x2757($v1)
8006b8cc: nop
8006b8d0: sb $v1, 0x35($v0)
8006b8d4: lw $v0, 0x10($fp)
8006b8d8: lui $v1, 0x800d
8006b8dc: lbu $v1, -0x27cc($v1)
8006b8e0: nop
8006b8e4: sb $v1, 0x36($v0)
8006b8e8: lw $v0, 0x10($fp)
8006b8ec: lui $v1, 0x800d
8006b8f0: lbu $v1, -0x27ca($v1)
8006b8f4: nop
8006b8f8: sb $v1, 0x37($v0)
8006b8fc: lw $v0, 0x10($fp)
8006b900: lui $v1, 0x800d
8006b904: lbu $v1, -0x27cb($v1)
8006b908: nop
8006b90c: sb $v1, 0x38($v0)
8006bce4: lw $v0, 0x10($fp)
8006bce8: nop
8006bcec: lbu $v1, 0x35($v0)
8006bcf0: lui $at, 0x800d
8006bcf4: sb $v1, -0x2757($at)
8006bcf8: lw $v0, 0x10($fp)
8006bcfc: nop
8006bd00: lbu $v1, 0x36($v0)
8006bd04: lui $at, 0x800d
8006bd08: sb $v1, -0x27cc($at)
8006bd0c: lw $v0, 0x10($fp)
8006bd10: nop
8006bd14: lbu $v1, 0x37($v0)
8006bd18: lui $at, 0x800d
8006bd1c: sb $v1, -0x27ca($at)
8006bd20: lw $v0, 0x10($fp)
8006bd24: nop
8006bd28: lbu $v1, 0x38($v0)
8006bd2c: lui $at, 0x800d
8006bd30: sb $v1, -0x27cb($at)
80099864: .byte 0xff, 0xff, 0xff, 0xff
80099868: srl $zero, $zero, 0
8009986c: sra $zero, $zero, 0
80099870: sllv $zero, $zero, $zero
