8006efcc: jal 0x80065974
8006efd0: nop
8006efd4: lw $v1, 0x88($fp)
8006efd8: nop
8006efdc: lhu $v0, 4($v1)
8006efe0: addiu $a0, $zero, 0x28
8006efe4: addiu $a1, $zero, 0x20
8006efe8: move $a2, $v0
8006efec: jal 0x8006fae0
8006eff0: nop
8006eff4: addiu $a0, $zero, 0x28
8006eff8: addiu $a1, $zero, 0x20
8006effc: jal 0x8006fff0
8006f000: nop
8006f004: lh $v0, 0x60($fp)
8006f008: addiu $a0, $zero, 0x92
8006f00c: addiu $a1, $zero, 0x30
8006f010: move $a2, $v0
8006f014: addiu $a3, $zero, 0x18
8006f018: jal 0x800703e4
8006f01c: nop
800703e4: addiu $sp, $sp, -0x50
800703e8: sw $ra, 0x48($sp)
800703ec: sw $fp, 0x44($sp)
800703f0: sw $s2, 0x40($sp)
800703f4: sw $s1, 0x3c($sp)
800703f8: sw $s0, 0x38($sp)
800703fc: move $fp, $sp
80070400: move $s0, $a0
80070404: move $s1, $a1
80070408: move $s2, $a2
8007040c: sw $a3, 0x5c($fp)
80070410: sh $s0, 0x10($fp)
80070414: sh $s1, 0x12($fp)
80070418: sh $s2, 0x14($fp)
8007041c: lh $v0, 0x14($fp)
80070420: nop
80070424: move $a0, $v0
80070428: sll $v1, $a0, 4
8007042c: subu $v1, $v1, $v0
80070430: sll $v0, $v1, 2
80070434: lui $at, 0x8014
80070438: addu $at, $at, $v0
8007043c: lbu $v1, 0x3ffc($at)
80070440: nop
80070444: sb $v1, 0x30($fp)
80070448: lh $v0, 0x10($fp)
8007044c: lh $v1, 0x12($fp)
80070450: lh $a0, 0x14($fp)
80070454: nop
80070458: move $a2, $a0
8007045c: sll $a1, $a2, 4
80070460: subu $a1, $a1, $a0
80070464: sll $a0, $a1, 2
80070468: lui $at, 0x8014
8007046c: addu $at, $at, $a0
80070470: lh $a2, 0x4000($at)
80070474: move $a0, $v0
80070478: move $a1, $v1
8007047c: addiu $a3, $zero, -0x80
80070480: jal 0x800675dc
80070484: nop
80070488: lhu $v0, 0x10($fp)
8007048c: nop
80070490: addiu $v1, $v0, 0x30
80070494: sll $a0, $v1, 0x10
80070498: sra $v0, $a0, 0x10
8007049c: lh $v1, 0x12($fp)
800704a0: lhu $a0, 0x14($fp)
800704a4: nop
800704a8: addiu $a1, $a0, 0x96
800704ac: sll $a0, $a1, 0x10
800704b0: sra $a2, $a0, 0x10
800704b4: move $a0, $v0
800704b8: move $a1, $v1
800704bc: jal 0x8004e494
800704c0: nop
800704c4: lh $v0, 0x14($fp)
800704c8: nop
800704cc: move $a0, $v0
800704d0: sll $v1, $a0, 4
800704d4: subu $v1, $v1, $v0
800704d8: sll $v0, $v1, 2
800704dc: lui $at, 0x8014
800704e0: addu $at, $at, $v0
800704e4: lb $v1, 0x3ffb($at)
800704e8: lui $at, 0x800d
800704ec: sw $v1, -0x26c8($at)
800704f0: lhu $v0, 0x10($fp)
800704f4: nop
800704f8: addiu $v1, $v0, 0x28
800704fc: sll $a0, $v1, 0x10
80070500: sra $v0, $a0, 0x10
80070504: lhu $v1, 0x12($fp)
80070508: nop
8007050c: addiu $a0, $v1, 0x10
80070510: sll $a1, $a0, 0x10
80070514: sra $v1, $a1, 0x10
80070518: lb $a0, 0x30($fp)
8007051c: nop
80070520: addiu $a1, $a0, 0x126
80070524: sll $a0, $a1, 0x10
80070528: sra $a2, $a0, 0x10
8007052c: move $a0, $v0
80070530: move $a1, $v1
80070534: jal 0x8004e494
80070538: nop
8007053c: lh $v0, 0x14($fp)
80070540: nop
80070544: move $a0, $v0
80070548: sll $v1, $a0, 4
8007054c: subu $v1, $v1, $v0
80070550: sll $v0, $v1, 2
80070554: lui $at, 0x8014
80070558: addu $at, $at, $v0
8007055c: lw $v1, 0x400c($at)
80070560: nop
80070564: bnez $v1, 0x800705b4
80070568: nop
8007056c: lhu $v0, 0x10($fp)
80070570: nop
80070574: addiu $v1, $v0, 0x30
80070578: sll $a0, $v1, 0x10
8007057c: sra $v0, $a0, 0x10
80070580: lhu $v1, 0x12($fp)
80070584: nop
80070588: addiu $a0, $v1, 0x20
8007058c: sll $a1, $a0, 0x10
80070590: sra $v1, $a1, 0x10
80070594: move $a0, $v0
80070598: move $a1, $v1
8007059c: lui $a2, 0x800c
800705a0: addiu $a2, $a2, -0x6984
800705a4: jal 0x80067338
800705a8: nop
800705ac: j 0x800705f4
800705b0: nop
800705b4: lhu $v0, 0x10($fp)
800705b8: nop
800705bc: addiu $v1, $v0, 0x30
800705c0: sll $a0, $v1, 0x10
800705c4: sra $v0, $a0, 0x10
800705c8: lhu $v1, 0x12($fp)
800705cc: nop
800705d0: addiu $a0, $v1, 0x20
800705d4: sll $a1, $a0, 0x10
800705d8: sra $v1, $a1, 0x10
800705dc: move $a0, $v0
800705e0: move $a1, $v1
800705e4: lui $a2, 0x800c
800705e8: addiu $a2, $a2, -0x6990
800705ec: jal 0x80067338
800705f0: nop
800705f4: lh $v0, 0x14($fp)
800705f8: nop
800705fc: move $a0, $v0
80070600: sll $v1, $a0, 4
80070604: subu $v1, $v1, $v0
80070608: sll $v0, $v1, 2
8007060c: lui $at, 0x8014
80070610: addu $at, $at, $v0
80070614: lw $v1, 0x4004($at)
80070618: lw $v0, 0x5c($fp)
8007061c: nop
80070620: mult $v1, $v0
80070624: mflo $v1
80070628: lui $at, 0x800e
8007062c: sw $v1, 0x4000($at)
80070630: lui $v0, 0x800e
80070634: lw $v0, 0x4000($v0)
80070638: nop
8007063c: slti $v1, $v0, 0x2710
80070640: bnez $v1, 0x80070660
80070644: nop
80070648: lhu $v0, 0x10($fp)
8007064c: nop
80070650: addiu $v1, $v0, 0x28
80070654: sh $v1, 0x16($fp)
80070658: j 0x80070670
8007065c: nop
80070660: lhu $v0, 0x10($fp)
80070664: nop
80070668: addiu $v1, $v0, 0x30
8007066c: sh $v1, 0x16($fp)
80070670: lh $v0, 0x16($fp)
80070674: lhu $v1, 0x12($fp)
80070678: nop
8007067c: addiu $a0, $v1, 0x30
80070680: sll $a1, $a0, 0x10
80070684: sra $v1, $a1, 0x10
80070688: move $a0, $v0
8007068c: move $a1, $v1
80070690: addiu $a2, $zero, 0x128
80070694: jal 0x8004e494
80070698: nop
8007069c: lh $v0, 0x14($fp)
800706a0: nop
800706a4: move $a0, $v0
800706a8: sll $v1, $a0, 4
800706ac: subu $v1, $v1, $v0
800706b0: sll $v0, $v1, 2
800706b4: lui $at, 0x8014
800706b8: addu $at, $at, $v0
800706bc: lb $v1, 0x4011($at)
800706c0: lui $at, 0x800d
800706c4: sw $v1, -0x26c8($at)
800706c8: lhu $v0, 0x10($fp)
800706cc: nop
800706d0: addiu $v1, $v0, -8
800706d4: sll $a0, $v1, 0x10
800706d8: sra $v0, $a0, 0x10
800706dc: lhu $v1, 0x12($fp)
800706e0: nop
800706e4: addiu $a0, $v1, 0x40
800706e8: sll $a1, $a0, 0x10
800706ec: sra $v1, $a1, 0x10
800706f0: move $a0, $v0
800706f4: move $a1, $v1
800706f8: addiu $a2, $zero, 0x171
800706fc: jal 0x8004e494
80070700: nop
80070704: addiu $v0, $zero, 0x10
80070708: sh $v0, 0x26($fp)
8007070c: lhu $v0, 0x10($fp)
80070710: nop
80070714: addiu $v1, $v0, 0x10
80070718: sh $v1, 0x20($fp)
8007071c: lhu $v0, 0x12($fp)
80070720: nop
80070724: addiu $v1, $v0, 0x40
80070728: sh $v1, 0x22($fp)
8007072c: lui $a0, 0x800d
80070730: lw $a0, -0x26c8($a0)
80070734: jal 0x80097c00
80070738: nop
8007073c: sw $v0, 0x34($fp)
80070740: lw $a0, 0x34($fp)
80070744: jal 0x80097924
80070748: nop
8007074c: move $a0, $v0
80070750: move $a1, $v1
80070754: lui $a2, 0xeb85
80070758: ori $a2, $a2, 0x1eb8
8007075c: lui $a3, 0x3fde
80070760: ori $a3, $a3, 0xb851
80070764: jal 0x80097cb8
80070768: nop
8007076c: move $a0, $v0
80070770: move $a1, $v1
80070774: jal 0x80098234
80070778: nop
8007077c: sw $v0, 0x34($fp)
80070780: lw $a0, 0x34($fp)
80070784: jal 0x80097b4c
80070788: nop
8007078c: sh $v0, 0x24($fp)
80070790: lui $v0, 0x800d
80070794: lbu $v0, -0x25ec($v0)
80070798: nop
8007079c: sb $v0, 0x28($fp)
800707a0: lhu $a0, 0x20($fp)
800707a4: nop
800707a8: andi $v1, $a0, 0xffff
800707ac: lui $a0, 0xffff
800707b0: and $v0, $v0, $a0
800707b4: or $v0, $v0, $v1
800707b8: lhu $v1, 0x22($fp)
800707bc: nop
800707c0: sll $a0, $v1, 0x10
800707c4: andi $v0, $v0, 0xffff
800707c8: or $v0, $v0, $a0
800707cc: lhu $a1, 0x24($fp)
800707d0: nop
800707d4: andi $a0, $a1, 0xffff
800707d8: lui $a1, 0xffff
800707dc: and $v1, $v1, $a1
800707e0: or $v1, $v1, $a0
800707e4: lhu $a0, 0x26($fp)
800707e8: nop
800707ec: sll $a1, $a0, 0x10
800707f0: andi $v1, $v1, 0xffff
800707f4: or $v1, $v1, $a1
800707f8: lhu $a1, 0x28($fp)
800707fc: nop
80070800: andi $a0, $a1, 0xffff
80070804: lui $a1, 0xffff
80070808: and $a2, $a2, $a1
8007080c: or $a2, $a2, $a0
80070810: move $a0, $v0
80070814: move $a1, $v1
80070818: addiu $a3, $zero, 3
8007081c: jal 0x800182d0
80070820: nop
80070824: lui $v1, 0x800d
80070828: lhu $v1, -0x25ec($v1)
8007082c: nop
80070830: addu $v1, $v1, $v0
80070834: lui $at, 0x800d
80070838: sh $v1, -0x25ec($at)
8007083c: lh $v0, 0x14($fp)
80070840: nop
80070844: move $a0, $v0
80070848: sll $v1, $a0, 4
8007084c: subu $v1, $v1, $v0
80070850: sll $v0, $v1, 2
80070854: lui $at, 0x8014
80070858: addu $at, $at, $v0
8007085c: lb $v1, 0x4010($at)
80070860: nop
80070864: move $a0, $v1
80070868: jal 0x80097c00
8007086c: nop
80070870: sw $v0, 0x34($fp)
80070874: lw $a0, 0x34($fp)
80070878: jal 0x80097924
8007087c: nop
80070880: move $a0, $v0
80070884: move $a1, $v1
80070888: lui $a2, 0xeb85
8007088c: ori $a2, $a2, 0x1eb8
80070890: lui $a3, 0x3fde
80070894: ori $a3, $a3, 0xb851
80070898: jal 0x80097cb8
8007089c: nop
800708a0: move $a0, $v0
800708a4: move $a1, $v1
800708a8: jal 0x80098234
800708ac: nop
800708b0: sw $v0, 0x34($fp)
800708b4: lw $a0, 0x34($fp)
800708b8: jal 0x80097b4c
800708bc: nop
800708c0: sh $v0, 0x24($fp)
800708c4: lui $v0, 0x800d
800708c8: lbu $v0, -0x25ec($v0)
800708cc: nop
800708d0: sb $v0, 0x28($fp)
800708d4: lhu $a0, 0x20($fp)
800708d8: nop
800708dc: andi $v1, $a0, 0xffff
800708e0: lui $a0, 0xffff
800708e4: and $v0, $v0, $a0
800708e8: or $v0, $v0, $v1
800708ec: lhu $v1, 0x22($fp)
800708f0: nop
800708f4: sll $a0, $v1, 0x10
800708f8: andi $v0, $v0, 0xffff
800708fc: or $v0, $v0, $a0
80070900: lhu $a1, 0x24($fp)
80070904: nop
80070908: andi $a0, $a1, 0xffff
8007090c: lui $a1, 0xffff
80070910: and $v1, $v1, $a1
80070914: or $v1, $v1, $a0
80070918: lhu $a0, 0x26($fp)
8007091c: nop
80070920: sll $a1, $a0, 0x10
80070924: andi $v1, $v1, 0xffff
80070928: or $v1, $v1, $a1
8007092c: lhu $a1, 0x28($fp)
80070930: nop
80070934: andi $a0, $a1, 0xffff
80070938: lui $a1, 0xffff
8007093c: and $a2, $a2, $a1
80070940: or $a2, $a2, $a0
80070944: move $a0, $v0
80070948: move $a1, $v1
8007094c: addiu $a3, $zero, 4
80070950: jal 0x800182d0
80070954: nop
80070958: lui $v1, 0x800d
8007095c: lhu $v1, -0x25ec($v1)
80070960: nop
80070964: addu $v1, $v1, $v0
80070968: lui $at, 0x800d
8007096c: sh $v1, -0x25ec($at)
80070970: lh $v0, 0x14($fp)
80070974: nop
80070978: move $a0, $v0
8007097c: sll $v1, $a0, 4
80070980: subu $v1, $v1, $v0
80070984: sll $v0, $v1, 2
80070988: lui $at, 0x8014
8007098c: addu $at, $at, $v0
80070990: lb $v1, 0x4015($at)
80070994: lui $at, 0x800d
80070998: sw $v1, -0x26c8($at)
8007099c: lhu $v0, 0x10($fp)
800709a0: nop
800709a4: addiu $v1, $v0, -8
800709a8: sll $a0, $v1, 0x10
800709ac: sra $v0, $a0, 0x10
800709b0: lhu $v1, 0x12($fp)
800709b4: nop
800709b8: addiu $a0, $v1, 0x50
800709bc: sll $a1, $a0, 0x10
800709c0: sra $v1, $a1, 0x10
800709c4: move $a0, $v0
800709c8: move $a1, $v1
800709cc: addiu $a2, $zero, 0x171
800709d0: jal 0x8004e494
800709d4: nop
800709d8: lui $a0, 0x800d
800709dc: lw $a0, -0x26c8($a0)
800709e0: jal 0x80097c00
800709e4: nop
800709e8: sw $v0, 0x34($fp)
800709ec: lw $a0, 0x34($fp)
800709f0: jal 0x80097924
800709f4: nop
800709f8: move $a0, $v0
800709fc: move $a1, $v1
80070a00: lui $a2, 0xeb85
80070a04: ori $a2, $a2, 0x1eb8
80070a08: lui $a3, 0x3fde
80070a0c: ori $a3, $a3, 0xb851
80070a10: jal 0x80097cb8
80070a14: nop
80070a18: move $a0, $v0
80070a1c: move $a1, $v1
80070a20: jal 0x80098234
80070a24: nop
80070a28: sw $v0, 0x34($fp)
80070a2c: lhu $v0, 0x10($fp)
80070a30: nop
80070a34: addiu $v1, $v0, 0x10
80070a38: sh $v1, 0x20($fp)
80070a3c: lhu $v0, 0x12($fp)
80070a40: nop
80070a44: addiu $v1, $v0, 0x50
80070a48: sh $v1, 0x22($fp)
80070a4c: lw $a0, 0x34($fp)
80070a50: jal 0x80097b4c
80070a54: nop
80070a58: sh $v0, 0x24($fp)
80070a5c: lui $v0, 0x800d
80070a60: lbu $v0, -0x25ec($v0)
80070a64: nop
80070a68: sb $v0, 0x28($fp)
80070a6c: lhu $a0, 0x20($fp)
80070a70: nop
80070a74: andi $v1, $a0, 0xffff
80070a78: lui $a0, 0xffff
80070a7c: and $v0, $v0, $a0
80070a80: or $v0, $v0, $v1
80070a84: lhu $v1, 0x22($fp)
80070a88: nop
80070a8c: sll $a0, $v1, 0x10
80070a90: andi $v0, $v0, 0xffff
80070a94: or $v0, $v0, $a0
80070a98: lhu $a1, 0x24($fp)
80070a9c: nop
80070aa0: andi $a0, $a1, 0xffff
80070aa4: lui $a1, 0xffff
80070aa8: and $v1, $v1, $a1
80070aac: or $v1, $v1, $a0
80070ab0: lhu $a0, 0x26($fp)
80070ab4: nop
80070ab8: sll $a1, $a0, 0x10
80070abc: andi $v1, $v1, 0xffff
80070ac0: or $v1, $v1, $a1
80070ac4: lhu $a1, 0x28($fp)
80070ac8: nop
80070acc: andi $a0, $a1, 0xffff
80070ad0: lui $a1, 0xffff
80070ad4: and $a2, $a2, $a1
80070ad8: or $a2, $a2, $a0
80070adc: move $a0, $v0
80070ae0: move $a1, $v1
80070ae4: addiu $a3, $zero, 3
80070ae8: jal 0x800182d0
80070aec: nop
80070af0: lui $v1, 0x800d
80070af4: lhu $v1, -0x25ec($v1)
80070af8: nop
80070afc: addu $v1, $v1, $v0
80070b00: lui $at, 0x800d
80070b04: sh $v1, -0x25ec($at)
80070b08: lh $v0, 0x14($fp)
80070b0c: nop
80070b10: move $a0, $v0
80070b14: sll $v1, $a0, 4
80070b18: subu $v1, $v1, $v0
80070b1c: sll $v0, $v1, 2
80070b20: lui $at, 0x8014
80070b24: addu $at, $at, $v0
80070b28: lb $v1, 0x4013($at)
80070b2c: lui $at, 0x800d
80070b30: sw $v1, -0x26c8($at)
80070b34: lhu $v0, 0x10($fp)
80070b38: nop
80070b3c: addiu $v1, $v0, -8
80070b40: sll $a0, $v1, 0x10
80070b44: sra $v0, $a0, 0x10
80070b48: lhu $v1, 0x12($fp)
80070b4c: nop
80070b50: addiu $a0, $v1, 0x60
80070b54: sll $a1, $a0, 0x10
80070b58: sra $v1, $a1, 0x10
80070b5c: move $a0, $v0
80070b60: move $a1, $v1
80070b64: addiu $a2, $zero, 0x171
80070b68: jal 0x8004e494
80070b6c: nop
80070b70: lui $a0, 0x800d
80070b74: lw $a0, -0x26c8($a0)
80070b78: jal 0x80097c00
80070b7c: nop
80070b80: sw $v0, 0x34($fp)
80070b84: lw $a0, 0x34($fp)
80070b88: jal 0x80097924
80070b8c: nop
80070b90: move $a0, $v0
80070b94: move $a1, $v1
80070b98: lui $a2, 0xeb85
80070b9c: ori $a2, $a2, 0x1eb8
80070ba0: lui $a3, 0x3fde
80070ba4: ori $a3, $a3, 0xb851
80070ba8: jal 0x80097cb8
80070bac: nop
80070bb0: move $a0, $v0
80070bb4: move $a1, $v1
80070bb8: jal 0x80098234
80070bbc: nop
80070bc0: sw $v0, 0x34($fp)
80070bc4: lhu $v0, 0x10($fp)
80070bc8: nop
80070bcc: addiu $v1, $v0, 0x10
80070bd0: sh $v1, 0x20($fp)
80070bd4: lhu $v0, 0x12($fp)
80070bd8: nop
80070bdc: addiu $v1, $v0, 0x60
80070be0: sh $v1, 0x22($fp)
80070be4: lw $a0, 0x34($fp)
80070be8: jal 0x80097b4c
80070bec: nop
80070bf0: sh $v0, 0x24($fp)
80070bf4: lui $v0, 0x800d
80070bf8: lbu $v0, -0x25ec($v0)
80070bfc: nop
80070c00: sb $v0, 0x28($fp)
80070c04: lhu $a0, 0x20($fp)
80070c08: nop
80070c0c: andi $v1, $a0, 0xffff
80070c10: lui $a0, 0xffff
80070c14: and $v0, $v0, $a0
80070c18: or $v0, $v0, $v1
80070c1c: lhu $v1, 0x22($fp)
80070c20: nop
80070c24: sll $a0, $v1, 0x10
80070c28: andi $v0, $v0, 0xffff
80070c2c: or $v0, $v0, $a0
80070c30: lhu $a1, 0x24($fp)
80070c34: nop
80070c38: andi $a0, $a1, 0xffff
80070c3c: lui $a1, 0xffff
80070c40: and $v1, $v1, $a1
80070c44: or $v1, $v1, $a0
80070c48: lhu $a0, 0x26($fp)
80070c4c: nop
80070c50: sll $a1, $a0, 0x10
80070c54: andi $v1, $v1, 0xffff
80070c58: or $v1, $v1, $a1
80070c5c: lhu $a1, 0x28($fp)
80070c60: nop
80070c64: andi $a0, $a1, 0xffff
80070c68: lui $a1, 0xffff
80070c6c: and $a2, $a2, $a1
80070c70: or $a2, $a2, $a0
80070c74: move $a0, $v0
80070c78: move $a1, $v1
80070c7c: addiu $a3, $zero, 3
80070c80: jal 0x800182d0
80070c84: nop
80070c88: lui $v1, 0x800d
80070c8c: lhu $v1, -0x25ec($v1)
80070c90: nop
80070c94: addu $v1, $v1, $v0
80070c98: lui $at, 0x800d
80070c9c: sh $v1, -0x25ec($at)
80070ca0: lh $v0, 0x14($fp)
80070ca4: nop
80070ca8: move $a0, $v0
80070cac: sll $v1, $a0, 4
80070cb0: subu $v1, $v1, $v0
80070cb4: sll $v0, $v1, 2
80070cb8: lui $at, 0x8014
80070cbc: addu $at, $at, $v0
80070cc0: lb $v1, 0x4014($at)
80070cc4: lui $at, 0x800d
80070cc8: sw $v1, -0x26c8($at)
80070ccc: lhu $v0, 0x10($fp)
80070cd0: nop
80070cd4: addiu $v1, $v0, -8
80070cd8: sll $a0, $v1, 0x10
80070cdc: sra $v0, $a0, 0x10
80070ce0: lhu $v1, 0x12($fp)
80070ce4: nop
80070ce8: addiu $a0, $v1, 0x70
80070cec: sll $a1, $a0, 0x10
80070cf0: sra $v1, $a1, 0x10
80070cf4: move $a0, $v0
80070cf8: move $a1, $v1
80070cfc: addiu $a2, $zero, 0x171
80070d00: jal 0x8004e494
80070d04: nop
80070d08: lui $a0, 0x800d
80070d0c: lw $a0, -0x26c8($a0)
80070d10: jal 0x80097c00
80070d14: nop
80070d18: sw $v0, 0x34($fp)
80070d1c: lw $a0, 0x34($fp)
80070d20: jal 0x80097924
80070d24: nop
80070d28: move $a0, $v0
80070d2c: move $a1, $v1
80070d30: lui $a2, 0xeb85
80070d34: ori $a2, $a2, 0x1eb8
80070d38: lui $a3, 0x3fde
80070d3c: ori $a3, $a3, 0xb851
80070d40: jal 0x80097cb8
80070d44: nop
80070d48: move $a0, $v0
80070d4c: move $a1, $v1
80070d50: jal 0x80098234
80070d54: nop
80070d58: sw $v0, 0x34($fp)
80070d5c: lhu $v0, 0x10($fp)
80070d60: nop
80070d64: addiu $v1, $v0, 0x10
80070d68: sh $v1, 0x20($fp)
80070d6c: lhu $v0, 0x12($fp)
80070d70: nop
80070d74: addiu $v1, $v0, 0x70
80070d78: sh $v1, 0x22($fp)
80070d7c: lw $a0, 0x34($fp)
80070d80: jal 0x80097b4c
80070d84: nop
80070d88: sh $v0, 0x24($fp)
80070d8c: lui $v0, 0x800d
80070d90: lbu $v0, -0x25ec($v0)
80070d94: nop
80070d98: sb $v0, 0x28($fp)
80070d9c: lhu $a0, 0x20($fp)
80070da0: nop
80070da4: andi $v1, $a0, 0xffff
80070da8: lui $a0, 0xffff
80070dac: and $v0, $v0, $a0
80070db0: or $v0, $v0, $v1
80070db4: lhu $v1, 0x22($fp)
80070db8: nop
80070dbc: sll $a0, $v1, 0x10
80070dc0: andi $v0, $v0, 0xffff
80070dc4: or $v0, $v0, $a0
80070dc8: lhu $a1, 0x24($fp)
80070dcc: nop
80070dd0: andi $a0, $a1, 0xffff
80070dd4: lui $a1, 0xffff
80070dd8: and $v1, $v1, $a1
80070ddc: or $v1, $v1, $a0
80070de0: lhu $a0, 0x26($fp)
80070de4: nop
80070de8: sll $a1, $a0, 0x10
80070dec: andi $v1, $v1, 0xffff
80070df0: or $v1, $v1, $a1
80070df4: lhu $a1, 0x28($fp)
80070df8: nop
80070dfc: andi $a0, $a1, 0xffff
80070e00: lui $a1, 0xffff
80070e04: and $a2, $a2, $a1
80070e08: or $a2, $a2, $a0
80070e0c: move $a0, $v0
80070e10: move $a1, $v1
80070e14: addiu $a3, $zero, 3
80070e18: jal 0x800182d0
80070e1c: nop
80070e20: lui $v1, 0x800d
80070e24: lhu $v1, -0x25ec($v1)
80070e28: nop
80070e2c: addu $v1, $v1, $v0
80070e30: lui $at, 0x800d
80070e34: sh $v1, -0x25ec($at)
80070e38: lhu $v0, 0x10($fp)
80070e3c: nop
80070e40: addiu $v1, $v0, -8
80070e44: sh $v1, 0x20($fp)
80070e48: lhu $v0, 0x12($fp)
80070e4c: nop
80070e50: addiu $v1, $v0, -1
80070e54: sh $v1, 0x22($fp)
80070e58: addiu $v0, $zero, 0x80
80070e5c: sh $v0, 0x24($fp)
80070e60: addiu $v0, $zero, 0x80
80070e64: sh $v0, 0x26($fp)
80070e68: lui $v0, 0x800d
80070e6c: lbu $v0, -0x25ec($v0)
80070e70: nop
80070e74: sb $v0, 0x28($fp)
80070e78: lhu $a0, 0x20($fp)
80070e7c: nop
80070e80: andi $v1, $a0, 0xffff
80070e84: lui $a0, 0xffff
80070e88: and $v0, $v0, $a0
80070e8c: or $v0, $v0, $v1
80070e90: lhu $v1, 0x22($fp)
80070e94: nop
80070e98: sll $a0, $v1, 0x10
80070e9c: andi $v0, $v0, 0xffff
80070ea0: or $v0, $v0, $a0
80070ea4: lhu $a1, 0x24($fp)
80070ea8: nop
80070eac: andi $a0, $a1, 0xffff
80070eb0: lui $a1, 0xffff
80070eb4: and $v1, $v1, $a1
80070eb8: or $v1, $v1, $a0
80070ebc: lhu $a0, 0x26($fp)
80070ec0: nop
80070ec4: sll $a1, $a0, 0x10
80070ec8: andi $v1, $v1, 0xffff
80070ecc: or $v1, $v1, $a1
80070ed0: lhu $a1, 0x28($fp)
80070ed4: nop
80070ed8: andi $a0, $a1, 0xffff
80070edc: lui $a1, 0xffff
80070ee0: and $a2, $a2, $a1
80070ee4: or $a2, $a2, $a0
80070ee8: move $a0, $v0
80070eec: move $a1, $v1
80070ef0: addiu $a3, $zero, 1
80070ef4: jal 0x800182d0
80070ef8: nop
80070efc: lui $v1, 0x800d
80070f00: lhu $v1, -0x25ec($v1)
80070f04: nop
80070f08: addu $v1, $v1, $v0
80070f0c: lui $at, 0x800d
80070f10: sh $v1, -0x25ec($at)
80070f14: addiu $a0, $zero, 0x1a
80070f18: addiu $a1, $zero, 1
80070f1c: jal 0x80018940
80070f20: nop
80070f24: move $sp, $fp
80070f28: lw $ra, 0x48($sp)
80070f2c: lw $fp, 0x44($sp)
80070f30: lw $s2, 0x40($sp)
80070f34: lw $s1, 0x3c($sp)
80070f38: lw $s0, 0x38($sp)
80070f3c: addiu $sp, $sp, 0x50
80070f40: jr $ra
80070f44: nop
80071b38: lh $v0, 0x1c($fp)
80071b3c: addiu $v1, $zero, -1
80071b40: beq $v0, $v1, 0x80071b84
80071b44: nop
80071b48: lh $v0, 0x1c($fp)
80071b4c: lw $v1, 0x28($fp)
80071b50: nop
80071b54: lw $a0, 0xc78($v1)
80071b58: lui $a1, 0x800d
80071b5c: addiu $a1, $a1, -0x28b0
80071b60: addu $v1, $a0, $a1
80071b64: move $a0, $v1
80071b68: lb $v1, ($a0)
80071b6c: addiu $a0, $zero, 0x92
80071b70: addiu $a1, $zero, 0x30
80071b74: move $a2, $v0
80071b78: move $a3, $v1
80071b7c: jal 0x800703e4
80071b80: nop
800b9670: .byte 0x6d, 0x01, 0x6e, 0x01
800b9674: .byte 0x3f, 0x00, 0x66, 0x00
800b9678: .byte 0xff, 0x40, 0x00, 0x00
800b967c: .byte 0x6d, 0x01, 0x6e, 0x01
800b9680: .byte 0x53, 0x00, 0x4a, 0x00
800b9684: .byte 0xff, 0x40, 0x00, 0x00
800b9688: .byte 0x25, 0x01, 0x21, 0x01
800b968c: .byte 0x6d, 0x00, 0x23, 0x01
800b9690: .byte 0x66, 0x00, 0x5d, 0x00
800b9694: syscall 0x1b001
800b9698: .byte 0xff, 0x40, 0x00, 0x00
800b969c: .byte 0xee, 0x00, 0x2f, 0x01
800b96a0: .byte 0x6b, 0x00, 0x6b, 0x01
800b96a4: .byte 0x3a, 0x01, 0x49, 0x00
800b96a8: syscall 0x17401
800b96ac: .byte 0x4b, 0x00, 0xff, 0x40
