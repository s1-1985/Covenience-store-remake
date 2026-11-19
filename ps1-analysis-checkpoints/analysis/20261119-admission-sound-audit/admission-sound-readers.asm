80023a14: lui $v0, 0x800d
80023a18: lb $v0, -0x27cc($v0)
80023a1c: nop 
80023a20: beqz $v0, 0x80023bbc
80023a24: nop 
80023a28: lw $v0, 0x14($fp)
80023a2c: nop 
80023a30: move $v1, $v0
80023a34: sll $v0, $v1, 2
80023a38: lui $v1, 0x800d
80023a3c: addiu $v1, $v1, -0x19e4
80023a40: addu $v0, $v0, $v1
80023a44: move $v1, $v0
80023a48: lw $v0, ($v1)
80023a4c: lw $v1, 0x28($fp)
80023a50: nop 
80023a54: bne $v0, $v1, 0x80023bbc
80023a58: nop 
80023a5c: sw $zero, 0x1c($fp)
80023a60: lui $v0, 0x800d
80023a64: lhu $v0, -0x2870($v0)
80023a68: nop 
80023a6c: bnez $v0, 0x80023a7c
80023a70: nop 
80023a74: j 0x80023bbc
80023a78: nop 
80023a7c: lui $v0, 0x800d
80023a80: lhu $v0, -0x2870($v0)
80023a84: nop 
80023a88: andi $v1, $v0, 1
80023a8c: andi $v0, $v1, 0xffff
80023a90: bnez $v0, 0x80023aa0
80023a94: nop 
80023a98: j 0x80023b88
80023a9c: nop 
80023aa0: lw $v0, 0x1c($fp)
80023aa4: addiu $v1, $zero, 1
80023aa8: beq $v0, $v1, 0x80023b00
80023aac: nop 
80023ab0: slti $v1, $v0, 2
80023ab4: beqz $v1, 0x80023acc
80023ab8: nop 
80023abc: beqz $v0, 0x80023aec
80023ac0: nop 
80023ac4: j 0x80023b5c
80023ac8: nop 
80023acc: addiu $v1, $zero, 2
80023ad0: beq $v0, $v1, 0x80023b14
80023ad4: nop 
80023ad8: addiu $v1, $zero, 3
80023adc: beq $v0, $v1, 0x80023b38
80023ae0: nop 
80023ae4: j 0x80023b5c
80023ae8: nop 
80023aec: addiu $a0, $zero, 0x32
80023af0: jal 0x80064e4c
80023af4: nop 
80023af8: j 0x80023b88
80023afc: nop 
80023b00: addiu $a0, $zero, 0x31
80023b04: jal 0x80064e4c
80023b08: nop 
80023b0c: j 0x80023b88
80023b10: nop 
80023b14: lui $v1, 0x800d
80023b18: lw $v1, -0x19f4($v1)
80023b1c: nop 
80023b20: addiu $v0, $v1, 0x24
80023b24: move $a0, $v0
80023b28: jal 0x80064e4c
80023b2c: nop 
80023b30: j 0x80023b88
80023b34: nop 
80023b38: lui $v0, 0x800d
80023b3c: lh $v0, -0x2730($v0)
80023b40: nop 
80023b44: addiu $v1, $v0, 0x33
80023b48: move $a0, $v1
80023b4c: jal 0x80064e4c
80023b50: nop 
80023b54: j 0x80023b88
80023b58: nop 
80023b5c: lw $v0, 0x1c($fp)
80023b60: nop 
80023b64: move $v1, $v0
80023b68: sll $v0, $v1, 2
80023b6c: lui $v1, 0x800a
80023b70: addiu $v1, $v1, -0x6b84
80023b74: addu $v0, $v0, $v1
80023b78: move $v1, $v0
80023b7c: lw $a0, ($v1)
80023b80: jal 0x80064e4c
80023b84: nop 
80023b88: lui $v0, 0x800d
80023b8c: lhu $v0, -0x2870($v0)
80023b90: nop 
80023b94: srl $v1, $v0, 1
80023b98: lui $at, 0x800d
80023b9c: sh $v1, -0x2870($at)
80023ba0: lw $v1, 0x1c($fp)
80023ba4: nop 
80023ba8: addiu $v0, $v1, 1
80023bac: move $v1, $v0
80023bb0: sw $v1, 0x1c($fp)
80023bb4: j 0x80023a60
80023bb8: nop 
80031c28: lw $v0, 0x1c($fp)
80031c2c: nop 
80031c30: move $a0, $v0
80031c34: sll $v1, $a0, 1
80031c38: addu $v1, $v1, $v0
80031c3c: sll $v0, $v1, 3
80031c40: lui $at, 0x800a
80031c44: addu $at, $at, $v0
80031c48: lb $v1, 0x9dc($at)
80031c4c: addiu $v0, $zero, 3
80031c50: bne $v1, $v0, 0x80031e3c
80031c54: nop 
80031c58: lui $v0, 0x800d
80031c5c: lw $v0, -0x2714($v0)
80031c60: nop 
80031c64: move $a0, $v0
80031c68: sll $v1, $a0, 1
80031c6c: addu $v1, $v1, $v0
80031c70: sll $a0, $v1, 3
80031c74: subu $a0, $a0, $v0
80031c78: sll $v1, $a0, 5
80031c7c: addu $v1, $v1, $v0
80031c80: sll $v0, $v1, 2
80031c84: lui $at, 0x800d
80031c88: addu $at, $at, $v0
80031c8c: lw $v1, -0x1314($at)
80031c90: nop 
80031c94: lw $v0, 0x14($v1)
80031c98: lw $v1, 0x2c($fp)
80031c9c: nop 
80031ca0: addu $v0, $v0, $v1
80031ca4: lui $v1, 0x800d
80031ca8: lw $v1, -0x2714($v1)
80031cac: nop 
80031cb0: move $a1, $v1
80031cb4: sll $a0, $a1, 1
80031cb8: addu $a0, $a0, $v1
80031cbc: sll $a1, $a0, 3
80031cc0: subu $a1, $a1, $v1
80031cc4: sll $a0, $a1, 5
80031cc8: addu $a0, $a0, $v1
80031ccc: sll $v1, $a0, 2
80031cd0: lui $at, 0x800d
80031cd4: addu $at, $at, $v1
80031cd8: lw $a0, -0x1314($at)
80031cdc: nop 
80031ce0: lw $v1, 0x10($a0)
80031ce4: nop 
80031ce8: slt $v0, $v1, $v0
80031cec: beqz $v0, 0x80031e3c
80031cf0: nop 
80031cf4: lw $v0, 0x58($fp)
80031cf8: nop 
80031cfc: lb $v1, 0x12e3($v0)
80031d00: nop 
80031d04: slti $v0, $v1, 0x7f
80031d08: beqz $v0, 0x80031d34
80031d0c: nop 
80031d10: lw $v1, 0x58($fp)
80031d14: lw $v0, 0x58($fp)
80031d18: lw $v1, 0x58($fp)
80031d1c: nop 
80031d20: lbu $a0, 0x12e3($v1)
80031d24: nop 
80031d28: addiu $v1, $a0, 1
80031d2c: move $a0, $v1
80031d30: sb $a0, 0x12e3($v0)
80031d34: lw $v0, 0x58($fp)
80031d38: lw $v1, 0x1c($fp)
80031d3c: nop 
80031d40: move $a0, $v1
80031d44: sll $v1, $a0, 1
80031d48: addu $v0, $v1, $v0
80031d4c: addiu $v1, $v0, 0xde4
80031d50: move $v0, $v1
80031d54: lw $v1, 0x58($fp)
80031d58: lw $a0, 0x1c($fp)
80031d5c: nop 
80031d60: move $a1, $a0
80031d64: sll $a0, $a1, 1
80031d68: addu $v1, $a0, $v1
80031d6c: addiu $a0, $v1, 0xde4
80031d70: move $v1, $a0
80031d74: lhu $a0, ($v1)
80031d78: lhu $v1, 0x2c($fp)
80031d7c: nop 
80031d80: subu $a0, $a0, $v1
80031d84: sh $a0, ($v0)
80031d88: lui $v0, 0x800d
80031d8c: lhu $v0, -0x2870($v0)
80031d90: nop 
80031d94: ori $v1, $v0, 0x40
80031d98: lui $at, 0x800d
80031d9c: sh $v1, -0x2870($at)
80031da0: lui $v0, 0x800d
80031da4: lw $v0, -0x2714($v0)
80031da8: nop 
80031dac: move $a0, $v0
80031db0: sll $v1, $a0, 1
80031db4: addu $v1, $v1, $v0
80031db8: sll $a0, $v1, 3
80031dbc: subu $a0, $a0, $v0
80031dc0: sll $v1, $a0, 5
80031dc4: addu $v1, $v1, $v0
80031dc8: sll $a0, $v1, 2
80031dcc: lui $at, 0x800d
80031dd0: addu $at, $at, $a0
80031dd4: lw $v0, -0x1314($at)
80031dd8: lui $v1, 0x800d
80031ddc: lw $v1, -0x2714($v1)
80031de0: nop 
80031de4: move $a1, $v1
80031de8: sll $a0, $a1, 1
80031dec: addu $a0, $a0, $v1
80031df0: sll $a1, $a0, 3
80031df4: subu $a1, $a1, $v1
80031df8: sll $a0, $a1, 5
80031dfc: addu $a0, $a0, $v1
80031e00: sll $v1, $a0, 2
80031e04: lui $at, 0x800d
80031e08: addu $at, $at, $v1
80031e0c: lw $a0, -0x1314($at)
80031e10: lw $v0, 0x10($v0)
80031e14: lw $v1, 0x14($a0)
80031e18: nop 
80031e1c: subu $v0, $v0, $v1
80031e20: sw $v0, 0x2c($fp)
80031e24: lw $v0, 0x2c($fp)
80031e28: nop 
80031e2c: bgtz $v0, 0x80031e3c
80031e30: nop 
80031e34: j 0x80032804
80031e38: nop 
800329bc: lw $a0, 0x58($fp)
800329c0: jal 0x800331b4
800329c4: nop 
800329c8: lw $v1, 0x18($fp)
800329cc: nop 
800329d0: sb $v0, ($v1)
800329d4: sll $v1, $v0, 0x18
800329d8: sra $v0, $v1, 0x18
800329dc: addiu $v1, $zero, 1
800329e0: beq $v0, $v1, 0x80032ab4
800329e4: nop 
800329e8: lw $v0, 0x18($fp)
800329ec: lw $a0, 0x18($fp)
800329f0: nop 
800329f4: lh $v1, 2($a0)
800329f8: nop 
800329fc: move $a1, $v1
80032a00: sll $a0, $a1, 1
80032a04: addu $a0, $a0, $v1
80032a08: sll $v1, $a0, 3
80032a0c: lui $at, 0x800a
80032a10: addu $at, $at, $v1
80032a14: lbu $a0, 0x9d8($at)
80032a18: nop 
80032a1c: sb $a0, 1($v0)
80032a20: lw $v0, 0x18($fp)
80032a24: nop 
80032a28: sb $zero, 0x1d($v0)
80032a2c: lw $v0, 0x18($fp)
80032a30: lw $a0, 0x18($fp)
80032a34: nop 
80032a38: lh $v1, 2($a0)
80032a3c: nop 
80032a40: move $a1, $v1
80032a44: sll $a0, $a1, 1
80032a48: addu $a0, $a0, $v1
80032a4c: sll $v1, $a0, 3
80032a50: lui $at, 0x800a
80032a54: addu $at, $at, $v1
80032a58: lh $a0, 0x9d4($at)
80032a5c: lui $v1, 0x800d
80032a60: lw $v1, -0x26c4($v1)
80032a64: nop 
80032a68: addu $a0, $v1, $a0
80032a6c: sw $a0, 4($v0)
80032a70: lw $v0, 0x18($fp)
80032a74: lw $a0, 0x18($fp)
80032a78: nop 
80032a7c: lh $v1, 2($a0)
80032a80: nop 
80032a84: move $a1, $v1
80032a88: sll $a0, $a1, 1
80032a8c: addu $a0, $a0, $v1
80032a90: sll $v1, $a0, 3
80032a94: lui $at, 0x800a
80032a98: addu $at, $at, $v1
80032a9c: lhu $a0, 0x9d6($at)
80032aa0: nop 
80032aa4: sh $a0, 8($v0)
80032aa8: lw $v0, 0x18($fp)
80032aac: nop 
80032ab0: sh $zero, 0xa($v0)
80032ab4: j 0x80032c68
80032ab8: nop 
800331b4: addiu $sp, $sp, -0x18
800331b8: sw $ra, 0x14($sp)
800331bc: sw $fp, 0x10($sp)
800331c0: move $fp, $sp
800331c4: sw $a0, 0x18($fp)
800331c8: jal 0x8007e648
800331cc: nop 
800331d0: move $v1, $v0
800331d4: bgez $v1, 0x800331e0
800331d8: nop 
800331dc: addiu $v1, $v1, 3
800331e0: sra $v1, $v1, 2
800331e4: move $a0, $v1
800331e8: sll $v1, $a0, 2
800331ec: subu $v0, $v0, $v1
800331f0: addiu $v1, $zero, 1
800331f4: beq $v0, $v1, 0x800335a4
800331f8: nop 
800331fc: slti $v1, $v0, 2
80033200: beqz $v1, 0x80033218
80033204: nop 
80033208: beqz $v0, 0x80033238
8003320c: nop 
80033210: j 0x8003401c
80033214: nop 
80033218: addiu $v1, $zero, 2
8003321c: beq $v0, $v1, 0x80033924
80033220: nop 
80033224: addiu $v1, $zero, 3
80033228: beq $v0, $v1, 0x80033ca8
8003322c: nop 
80033230: j 0x8003401c
80033234: nop 
