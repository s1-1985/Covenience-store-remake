80010bb8: nop
80010bbc: movf $zero, $zero, $fcc0
80010bc0: mfhi $zero
80010bc4: sync
80010bc8: mflo $zero
80010bcc: mflo $zero
80010bd0: mtlo $zero
80010bd4: .byte 0x17, 0x00, 0x00, 0x00
80010bd8: srav $zero, $zero, $zero
80010bdc: jr $zero
80010be0: jr $zero
80010be4: jr $zero
80010be8: jr $zero
80010bec: movz $zero, $zero, $zero
80010bf0: .byte 0x0e, 0x00, 0x00, 0x00
80010bf4: syscall
80010bf8: break
80010bfc: movn $zero, $zero, $zero
80010c00: .byte 0x28, 0x00, 0x18, 0x00
80010c04: .byte 0x10, 0x00, 0x09, 0x00
80010c08: nop
8006a5bc: lw $v0, 0x80($fp)
8006a5c0: nop
8006a5c4: move $a0, $v0
8006a5c8: sll $v1, $a0, 2
8006a5cc: addu $v1, $v1, $v0
8006a5d0: sll $v0, $v1, 1
8006a5d4: lw $v1, 0x84($fp)
8006a5d8: nop
8006a5dc: addu $v0, $v0, $v1
8006a5e0: lui $at, 0x800d
8006a5e4: sw $v0, -0x2798($at)
8006a5e8: lui $v0, 0x800d
8006a5ec: lw $v0, -0x2798($v0)
8006a5f0: nop
8006a5f4: move $a0, $v0
8006a5f8: sll $v1, $a0, 2
8006a5fc: addu $v1, $v1, $v0
8006a600: sll $v0, $v1, 2
8006a604: lui $v1, 0x800a
8006a608: addiu $v1, $v1, -0x328
8006a60c: addu $v0, $v1, $v0
8006a610: lui $at, 0x800d
8006a614: sw $v0, -0x2784($at)
8006a618: lui $v0, 0x800d
8006a61c: lw $v0, -0x2784($v0)
8006a620: nop
8006a624: sw $zero, 0xc($v0)
8006a628: sw $zero, 0x88($fp)
8006a62c: lui $v1, 0x800d
8006a630: lw $v1, -0x2784($v1)
8006a634: nop
8006a638: lh $v0, ($v1)
8006a63c: nop
8006a640: move $a0, $v0
8006a644: sll $v1, $a0, 3
8006a648: subu $v1, $v1, $v0
8006a64c: sll $v0, $v1, 3
8006a650: lw $v1, 0x88($fp)
8006a654: lui $at, 0x800a
8006a658: addu $at, $at, $v0
8006a65c: lw $v0, -0x28b0($at)
8006a660: nop
8006a664: slt $v1, $v1, $v0
8006a668: bnez $v1, 0x8006a678
8006a66c: nop
8006a670: j 0x8006a774
8006a674: nop
8006a678: sw $zero, 0x8c($fp)
8006a67c: lui $v1, 0x800d
8006a680: lw $v1, -0x2784($v1)
8006a684: nop
8006a688: lh $v0, ($v1)
8006a68c: nop
8006a690: move $a0, $v0
8006a694: sll $v1, $a0, 3
8006a698: subu $v1, $v1, $v0
8006a69c: sll $v0, $v1, 3
8006a6a0: lw $v1, 0x8c($fp)
8006a6a4: lui $at, 0x800a
8006a6a8: addu $at, $at, $v0
8006a6ac: lw $v0, -0x28ac($at)
8006a6b0: nop
8006a6b4: slt $v1, $v1, $v0
8006a6b8: bnez $v1, 0x8006a6c8
8006a6bc: nop
8006a6c0: j 0x8006a758
8006a6c4: nop
8006a6c8: lui $v0, 0x800d
8006a6cc: lw $v0, -0x2784($v0)
8006a6d0: lui $v1, 0x800d
8006a6d4: lw $v1, -0x2784($v1)
8006a6d8: lui $a1, 0x800d
8006a6dc: lw $a1, -0x2784($a1)
8006a6e0: nop
8006a6e4: lh $a0, ($a1)
8006a6e8: nop
8006a6ec: move $a2, $a0
8006a6f0: sll $a1, $a2, 3
8006a6f4: subu $a1, $a1, $a0
8006a6f8: sll $a2, $a1, 3
8006a6fc: lui $at, 0x800a
8006a700: addu $at, $at, $a2
8006a704: lb $a0, -0x289f($at)
8006a708: nop
8006a70c: move $a1, $a0
8006a710: sll $a2, $a1, 5
8006a714: subu $a2, $a2, $a0
8006a718: sll $a1, $a2, 6
8006a71c: subu $a1, $a1, $a2
8006a720: sll $a2, $a1, 3
8006a724: addu $a2, $a2, $a0
8006a728: sll $a0, $a2, 6
8006a72c: lw $v1, 0xc($v1)
8006a730: nop
8006a734: addu $a0, $v1, $a0
8006a738: sw $a0, 0xc($v0)
8006a73c: lw $v1, 0x8c($fp)
8006a740: nop
8006a744: addiu $v0, $v1, 1
8006a748: move $v1, $v0
8006a74c: sw $v1, 0x8c($fp)
8006a750: j 0x8006a67c
8006a754: nop
8006a758: lw $v1, 0x88($fp)
8006a75c: nop
8006a760: addiu $v0, $v1, 1
8006a764: move $v1, $v0
8006a768: sw $v1, 0x88($fp)
8006a76c: j 0x8006a62c
8006a770: nop
8006a774: lui $v0, 0x800d
8006a778: lw $v0, -0x2784($v0)
8006a77c: lui $a0, 0x800d
8006a780: lw $a0, -0x2784($a0)
8006a784: nop
8006a788: lw $v1, 0xc($a0)
8006a78c: lui $a1, 0x6666
8006a790: ori $a1, $a1, 0x6667
8006a794: mult $v1, $a1
8006a798: mfhi $a0
8006a79c: sra $a1, $a0, 2
8006a7a0: sra $a0, $v1, 0x1f
8006a7a4: subu $v1, $a1, $a0
8006a7a8: sw $v1, 0xc($v0)
8006a7ac: jal 0x80065974
8006a7b0: nop
8006a7b4: lhu $a0, 0x60($fp)
8006a7b8: nop
8006a7bc: andi $v1, $a0, 0xffff
8006a7c0: lui $a0, 0xffff
8006a7c4: and $v0, $v0, $a0
8006a7c8: or $v0, $v0, $v1
8006a7cc: lhu $v1, 0x62($fp)
8006a7d0: nop
8006a7d4: sll $a0, $v1, 0x10
8006a7d8: andi $v0, $v0, 0xffff
8006a7dc: or $v0, $v0, $a0
8006a7e0: lhu $a1, 0x64($fp)
8006a7e4: nop
8006a7e8: andi $a0, $a1, 0xffff
8006a7ec: lui $a1, 0xffff
8006a7f0: and $v1, $v1, $a1
8006a7f4: or $v1, $v1, $a0
8006a7f8: lhu $a0, 0x66($fp)
8006a7fc: nop
8006a800: sll $a1, $a0, 0x10
8006a804: andi $v1, $v1, 0xffff
8006a808: or $v1, $v1, $a1
8006a80c: lhu $a1, 0x68($fp)
8006a810: nop
8006a814: andi $a0, $a1, 0xffff
8006a818: lui $a1, 0xffff
8006a81c: and $a2, $a2, $a1
8006a820: or $a2, $a2, $a0
8006a824: move $a0, $v0
8006a828: move $a1, $v1
8006a82c: jal 0x80017b18
8006a830: nop
8006a834: addiu $a0, $zero, 0x48
8006a838: addiu $a1, $zero, 0x28
8006a83c: lui $a2, 0x800c
8006a840: addiu $a2, $a2, -0x6c54
8006a844: jal 0x80067338
8006a848: nop
8006a84c: addiu $a0, $zero, 0x94
8006a850: addiu $a1, $zero, 0x38
8006a854: lui $a2, 0x800c
8006a858: addiu $a2, $a2, -0x6be8
8006a85c: jal 0x80067338
8006a860: nop
8006a864: lui $v0, 0x800d
8006a868: lw $v0, -0x2784($v0)
8006a86c: nop
8006a870: lw $v1, 0xc($v0)
8006a874: lui $at, 0x800e
8006a878: sw $v1, 0x4000($at)
8006a87c: lui $a0, 0x800e
8006a880: lw $a0, 0x4000($a0)
8006a884: jal 0x80065820
8006a888: nop
8006a88c: addiu $v1, $zero, 0xb
8006a890: subu $v0, $v1, $v0
8006a894: move $v1, $v0
8006a898: sll $v0, $v1, 3
8006a89c: sw $v0, 0x90($fp)
8006a8a0: lw $v1, 0x90($fp)
8006a8a4: nop
8006a8a8: addiu $v0, $v1, 0xb8
8006a8ac: move $a0, $v0
8006a8b0: addiu $a1, $zero, 0x38
8006a8b4: addiu $a2, $zero, 0x110
8006a8b8: jal 0x8004e494
8006a8bc: nop
8006a8c0: lw $v0, 0x80($fp)
8006a8c4: addiu $v1, $zero, 1
8006a8c8: bne $v0, $v1, 0x8006a8e0
8006a8cc: nop
8006a8d0: addiu $v0, $zero, 4
8006a8d4: sw $v0, 0x8c($fp)
8006a8d8: j 0x8006a8e8
8006a8dc: nop
8006a8e0: addiu $v0, $zero, 5
8006a8e4: sw $v0, 0x8c($fp)
8006a8e8: sw $zero, 0x88($fp)
8006a8ec: lw $v0, 0x88($fp)
8006a8f0: nop
8006a8f4: slti $v1, $v0, 0xa
8006a8f8: beqz $v1, 0x8006a938
8006a8fc: nop
8006a900: lw $v0, 0x80($fp)
8006a904: nop
8006a908: move $a0, $v0
8006a90c: sll $v1, $a0, 2
8006a910: addu $v1, $v1, $v0
8006a914: sll $v0, $v1, 1
8006a918: lw $v1, 0x88($fp)
8006a91c: nop
8006a920: addu $v0, $v0, $v1
8006a924: slti $v1, $v0, 0x12
8006a928: bnez $v1, 0x8006a940
8006a92c: nop
8006a930: j 0x8006a938
8006a934: nop
8006a938: j 0x8006aa4c
8006a93c: nop
8006a940: lw $v0, 0x88($fp)
8006a944: lw $v1, 0x8c($fp)
8006a948: nop
8006a94c: div $zero, $v0, $v1
8006a950: bnez $v1, 0x8006a95c
8006a954: nop
8006a958: break 7
8006a95c: addiu $at, $zero, -1
8006a960: bne $v1, $at, 0x8006a974
8006a964: lui $at, 0x8000
8006a968: bne $v0, $at, 0x8006a974
8006a96c: nop
8006a970: break 6
8006a974: mfhi $v0
8006a978: nop
8006a97c: move $a0, $v0
8006a980: sll $v1, $a0, 2
8006a984: addu $v1, $v1, $v0
8006a988: sll $a0, $v1, 3
8006a98c: addiu $v0, $a0, 0x34
8006a990: lw $v1, 0x88($fp)
8006a994: lw $a0, 0x8c($fp)
8006a998: nop
8006a99c: div $zero, $v1, $a0
8006a9a0: bnez $a0, 0x8006a9ac
8006a9a4: nop
8006a9a8: break 7
8006a9ac: addiu $at, $zero, -1
8006a9b0: bne $a0, $at, 0x8006a9c4
8006a9b4: lui $at, 0x8000
8006a9b8: bne $v1, $at, 0x8006a9c4
8006a9bc: nop
8006a9c0: break 6
8006a9c4: mflo $v1
8006a9c8: nop
8006a9cc: move $a1, $v1
8006a9d0: sll $a0, $a1, 2
8006a9d4: addu $a0, $a0, $v1
8006a9d8: sll $a1, $a0, 3
8006a9dc: addiu $v1, $a1, 0x38
8006a9e0: lw $a0, 0x80($fp)
8006a9e4: nop
8006a9e8: move $a2, $a0
8006a9ec: sll $a1, $a2, 2
8006a9f0: addu $a1, $a1, $a0
8006a9f4: sll $a0, $a1, 1
8006a9f8: lw $a1, 0x88($fp)
8006a9fc: nop
8006aa00: addu $a0, $a0, $a1
8006aa04: move $a1, $a0
8006aa08: sll $a0, $a1, 2
8006aa0c: addiu $a1, $fp, 0x18
8006aa10: addu $a0, $a0, $a1
8006aa14: move $a2, $a0
8006aa18: move $a0, $v0
8006aa1c: move $a1, $v1
8006aa20: lw $a2, ($a2)
8006aa24: addiu $a3, $zero, -0x80
8006aa28: jal 0x8006b620
8006aa2c: nop
8006aa30: lw $v1, 0x88($fp)
8006aa34: nop
8006aa38: addiu $v0, $v1, 1
8006aa3c: move $v1, $v0
8006aa40: sw $v1, 0x88($fp)
8006aa44: j 0x8006a8ec
8006aa48: nop
8006aa4c: lw $v0, 0x84($fp)
8006aa50: lw $v1, 0x8c($fp)
8006aa54: nop
8006aa58: div $zero, $v0, $v1
8006aa5c: bnez $v1, 0x8006aa68
8006aa60: nop
8006aa64: break 7
8006aa68: addiu $at, $zero, -1
8006aa6c: bne $v1, $at, 0x8006aa80
8006aa70: lui $at, 0x8000
8006aa74: bne $v0, $at, 0x8006aa80
8006aa78: nop
8006aa7c: break 6
8006aa80: mfhi $v0
8006aa84: nop
8006aa88: move $a0, $v0
8006aa8c: sll $v1, $a0, 2
8006aa90: addu $v1, $v1, $v0
8006aa94: sll $v0, $v1, 3
8006aa98: move $v1, $v0
8006aa9c: addiu $v0, $v1, 0x58
8006aaa0: sll $v1, $v0, 0x10
8006aaa4: sra $v0, $v1, 0x10
8006aaa8: lw $v1, 0x84($fp)
8006aaac: lw $a0, 0x8c($fp)
8006aab0: nop
8006aab4: div $zero, $v1, $a0
8006aab8: bnez $a0, 0x8006aac4
8006aabc: nop
8006aac0: break 7
8006aac4: addiu $at, $zero, -1
8006aac8: bne $a0, $at, 0x8006aadc
8006aacc: lui $at, 0x8000
8006aad0: bne $v1, $at, 0x8006aadc
8006aad4: nop
8006aad8: break 6
8006aadc: mflo $v1
8006aae0: nop
8006aae4: move $a1, $v1
8006aae8: sll $a0, $a1, 2
8006aaec: addu $a0, $a0, $v1
8006aaf0: sll $v1, $a0, 3
8006aaf4: move $a0, $v1
8006aaf8: addiu $v1, $a0, 0x5c
8006aafc: sll $a0, $v1, 0x10
8006ab00: sra $v1, $a0, 0x10
8006ab04: move $a0, $v0
8006ab08: move $a1, $v1
8006ab0c: jal 0x8005fdd4
8006ab10: nop
8006ab14: lui $v0, 0x800d
8006ab18: lw $v0, -0x2798($v0)
8006ab1c: nop
8006ab20: move $v1, $v0
8006ab24: sll $v0, $v1, 2
8006ab28: lui $a0, 0x800c
8006ab2c: addiu $a0, $a0, -0x6b08
8006ab30: addu $v1, $v0, $a0
8006ab34: move $v0, $v1
8006ab38: addiu $a0, $zero, 0x38
8006ab3c: addiu $a1, $zero, 0x38
8006ab40: lw $a2, ($v0)
8006ab44: jal 0x8004e494
8006ab48: nop
8006ab4c: addiu $a0, $zero, 0x2e
8006ab50: addiu $a1, $zero, 1
8006ab54: jal 0x80018940
8006ab58: nop
8006ab5c: move $a0, $zero
8006ab60: jal 0x80041374
8006ab64: nop
8006ab68: lui $v1, 0x800d
8006ab6c: lw $v1, -0x25f4($v1)
8006ab70: nop
8006ab74: andi $v0, $v1, 0x1000
8006ab78: beqz $v0, 0x8006abac
8006ab7c: nop
8006ab80: lw $v0, 0x84($fp)
8006ab84: lw $v1, 0x8c($fp)
8006ab88: nop
8006ab8c: slt $v0, $v0, $v1
8006ab90: bnez $v0, 0x8006abac
8006ab94: nop
8006ab98: lw $v0, 0x84($fp)
8006ab9c: lw $v1, 0x8c($fp)
8006aba0: nop
8006aba4: subu $v0, $v0, $v1
8006aba8: sw $v0, 0x84($fp)
8006abac: lui $v1, 0x800d
8006abb0: lw $v1, -0x25f4($v1)
8006abb4: nop
8006abb8: andi $v0, $v1, 0x4000
8006abbc: beqz $v0, 0x8006abf0
8006abc0: nop
8006abc4: lw $v0, 0x84($fp)
8006abc8: lw $v1, 0x8c($fp)
8006abcc: nop
8006abd0: slt $v0, $v0, $v1
8006abd4: beqz $v0, 0x8006abf0
8006abd8: nop
8006abdc: lw $v0, 0x84($fp)
8006abe0: lw $v1, 0x8c($fp)
8006abe4: nop
8006abe8: addu $v0, $v0, $v1
8006abec: sw $v0, 0x84($fp)
8006abf0: lui $v1, 0x800d
8006abf4: lw $v1, -0x25f4($v1)
8006abf8: nop
8006abfc: andi $v0, $v1, 0x2000
8006ac00: beqz $v0, 0x8006acac
8006ac04: nop
8006ac08: lw $v1, 0x84($fp)
8006ac0c: nop
8006ac10: addiu $v0, $v1, 1
8006ac14: lw $v1, 0x8c($fp)
8006ac18: nop
8006ac1c: div $zero, $v0, $v1
8006ac20: bnez $v1, 0x8006ac2c
8006ac24: nop
8006ac28: break 7
8006ac2c: addiu $at, $zero, -1
8006ac30: bne $v1, $at, 0x8006ac44
8006ac34: lui $at, 0x8000
8006ac38: bne $v0, $at, 0x8006ac44
8006ac3c: nop
8006ac40: break 6
8006ac44: mfhi $v0
8006ac48: nop
8006ac4c: beqz $v0, 0x8006ac70
8006ac50: nop
8006ac54: lw $v1, 0x84($fp)
8006ac58: nop
8006ac5c: addiu $v0, $v1, 1
8006ac60: move $v1, $v0
8006ac64: sw $v1, 0x84($fp)
8006ac68: j 0x8006acac
8006ac6c: nop
8006ac70: lw $v0, 0x80($fp)
8006ac74: nop
8006ac78: bnez $v0, 0x8006acac
8006ac7c: nop
8006ac80: addiu $v0, $zero, 1
8006ac84: sw $v0, 0x80($fp)
8006ac88: lw $v0, 0x84($fp)
8006ac8c: addiu $v1, $zero, 4
8006ac90: bne $v0, $v1, 0x8006aca4
8006ac94: nop
8006ac98: sw $zero, 0x84($fp)
8006ac9c: j 0x8006acac
8006aca0: nop
8006aca4: addiu $v0, $zero, 4
8006aca8: sw $v0, 0x84($fp)
8006acac: lui $v1, 0x800d
8006acb0: lw $v1, -0x25f4($v1)
8006acb4: nop
8006acb8: andi $v0, $v1, 0x8000
8006acbc: beqz $v0, 0x8006ad60
8006acc0: nop
8006acc4: lw $v0, 0x84($fp)
8006acc8: lw $v1, 0x8c($fp)
8006accc: nop
8006acd0: div $zero, $v0, $v1
8006acd4: bnez $v1, 0x8006ace0
8006acd8: nop
8006acdc: break 7
8006ace0: addiu $at, $zero, -1
8006ace4: bne $v1, $at, 0x8006acf8
8006ace8: lui $at, 0x8000
8006acec: bne $v0, $at, 0x8006acf8
8006acf0: nop
8006acf4: break 6
8006acf8: mfhi $v0
8006acfc: nop
8006ad00: beqz $v0, 0x8006ad24
8006ad04: nop
8006ad08: lw $v1, 0x84($fp)
8006ad0c: nop
8006ad10: addiu $v0, $v1, -1
8006ad14: move $v1, $v0
8006ad18: sw $v1, 0x84($fp)
8006ad1c: j 0x8006ad60
8006ad20: nop
8006ad24: lw $v0, 0x80($fp)
8006ad28: addiu $v1, $zero, 1
8006ad2c: bne $v0, $v1, 0x8006ad60
8006ad30: nop
8006ad34: sw $zero, 0x80($fp)
8006ad38: lw $v0, 0x84($fp)
8006ad3c: nop
8006ad40: bnez $v0, 0x8006ad58
8006ad44: nop
8006ad48: addiu $v0, $zero, 4
8006ad4c: sw $v0, 0x84($fp)
8006ad50: j 0x8006ad60
8006ad54: nop
8006ad58: addiu $v0, $zero, 9
8006ad5c: sw $v0, 0x84($fp)
8006b620: addiu $sp, $sp, -0x70
8006b624: sw $ra, 0x68($sp)
8006b628: sw $fp, 0x64($sp)
8006b62c: sw $s0, 0x60($sp)
8006b630: move $fp, $sp
8006b634: sw $a0, 0x70($fp)
8006b638: sw $a1, 0x74($fp)
8006b63c: sw $a2, 0x78($fp)
8006b640: move $s0, $a3
8006b644: sb $s0, 0x30($fp)
8006b648: addiu $v0, $zero, 0xd
8006b64c: sh $v0, 0x44($fp)
8006b650: addiu $v0, $zero, 0x20
8006b654: sh $v0, 0x42($fp)
8006b658: addiu $v0, $zero, 0x20
8006b65c: sh $v0, 0x40($fp)
8006b660: lhu $v0, 0x70($fp)
8006b664: nop
8006b668: addiu $v1, $v0, -0x90
8006b66c: sh $v1, 0x3c($fp)
8006b670: lhu $v0, 0x74($fp)
8006b674: nop
8006b678: addiu $v1, $v0, -0x60
8006b67c: sh $v1, 0x3e($fp)
8006b680: lw $v0, 0x78($fp)
8006b684: nop
8006b688: move $v1, $v0
8006b68c: bgez $v1, 0x8006b698
8006b690: nop
8006b694: addiu $v1, $v1, 7
8006b698: sra $v1, $v1, 3
8006b69c: move $a0, $v1
8006b6a0: sll $v1, $a0, 3
8006b6a4: subu $v0, $v0, $v1
8006b6a8: move $v1, $v0
8006b6ac: sll $v0, $v1, 5
8006b6b0: sb $v0, 0x46($fp)
8006b6b4: lw $v1, 0x78($fp)
8006b6b8: nop
8006b6bc: move $v0, $v1
8006b6c0: bgez $v0, 0x8006b6cc
8006b6c4: nop
8006b6c8: addiu $v0, $v0, 7
8006b6cc: sra $v0, $v0, 3
8006b6d0: move $v1, $v0
8006b6d4: sll $v0, $v1, 5
8006b6d8: move $v1, $v0
8006b6dc: addiu $v0, $v1, -0x80
8006b6e0: sb $v0, 0x47($fp)
8006b6e4: sh $zero, 0x48($fp)
8006b6e8: addiu $v0, $zero, 0x1ea
8006b6ec: sh $v0, 0x4a($fp)
8006b6f0: lbu $v0, 0x30($fp)
8006b6f4: nop
8006b6f8: sb $v0, 0x4e($fp)
8006b6fc: sb $v0, 0x4d($fp)
8006b700: sb $v0, 0x4c($fp)
8006b704: lui $v0, 0x800d
8006b708: lh $v0, -0x25cc($v0)
8006b70c: addiu $v1, $zero, 1
8006b710: sw $v1, 0x28($sp)
8006b714: addiu $v1, $sp, 0x10
8006b718: addiu $a0, $fp, 0x44
8006b71c: lw $t1, ($a0)
8006b720: lw $t2, 4($a0)
8006b724: lw $t3, 8($a0)
8006b728: lw $t0, 0xc($a0)
8006b72c: sw $t1, ($v1)
8006b730: sw $t2, 4($v1)
8006b734: sw $t3, 8($v1)
8006b738: sw $t0, 0xc($v1)
8006b73c: lw $t1, 0x10($a0)
8006b740: lw $t2, 0x14($a0)
8006b744: sw $t1, 0x10($v1)
8006b748: sw $t2, 0x14($v1)
8006b74c: lw $a1, 0x38($fp)
8006b750: lw $a2, 0x3c($fp)
8006b754: lw $a3, 0x40($fp)
8006b758: move $a0, $v0
8006b75c: jal 0x80041630
8006b760: nop
8006b764: move $sp, $fp
8006b768: lw $ra, 0x68($sp)
8006b76c: lw $fp, 0x64($sp)
8006b770: lw $s0, 0x60($sp)
8006b774: addiu $sp, $sp, 0x70
8006b778: jr $ra
8006b77c: nop
800b94f8: .byte 0x67, 0x00, 0x00, 0x00
800b94fc: .byte 0x68, 0x00, 0x00, 0x00
800b9500: break 0, 2
800b9504: .byte 0x79, 0x00, 0x00, 0x00
800b9508: .byte 0x7c, 0x00, 0x00, 0x00
800b950c: .byte 0x7e, 0x00, 0x00, 0x00
800b9510: .byte 0x7d, 0x00, 0x00, 0x00
800b9514: .byte 0x7f, 0x00, 0x00, 0x00
800b9518: .byte 0x6d, 0x00, 0x00, 0x00
800b951c: .byte 0x6e, 0x00, 0x00, 0x00
800b9520: .byte 0x6f, 0x00, 0x00, 0x00
800b9524: tge $zero, $zero, 1
800b9528: tgeu $zero, $zero, 1
800b952c: tlt $zero, $zero, 1
800b9530: tne $zero, $zero, 1
800b9534: teq $zero, $zero, 1
800b9538: .byte 0x75, 0x00, 0x00, 0x00
800b953c: tltu $zero, $zero, 1
