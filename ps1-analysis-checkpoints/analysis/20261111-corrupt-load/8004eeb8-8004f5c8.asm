8004eeb8  addiu $sp, $sp, -0x20
8004eebc  sw $ra, 0x1c($sp)
8004eec0  sw $fp, 0x18($sp)
8004eec4  move $fp, $sp
8004eec8  addiu $v0, $zero, 2
8004eecc  sh $v0, 0x10($fp)
8004eed0  j 0x8004eee0
8004eed4  nop 
8004eed8  j 0x8004efac
8004eedc  nop 
8004eee0  lh $v0, 0x10($fp)
8004eee4  nop 
8004eee8  move $a0, $v0
8004eeec  jal 0x8004efd0
8004eef0  nop 
8004eef4  sh $v0, 0x10($fp)
8004eef8  lh $v0, 0x10($fp)
8004eefc  addiu $v1, $zero, 2
8004ef00  bne $v0, $v1, 0x8004ef18
8004ef04  nop 
8004ef08  j 0x8004efac
8004ef0c  nop 
8004ef10  j 0x8004efa4
8004ef14  nop 
8004ef18  lh $v0, 0x10($fp)
8004ef1c  nop 
8004ef20  beqz $v0, 0x8004ef3c
8004ef24  nop 
8004ef28  addiu $v1, $zero, 1
8004ef2c  beq $v0, $v1, 0x8004ef70
8004ef30  nop 
8004ef34  j 0x8004efa4
8004ef38  nop 
8004ef3c  move $a0, $zero
8004ef40  jal 0x800501fc
8004ef44  nop 
8004ef48  sw $v0, 0x14($fp)
8004ef4c  lw $v0, 0x14($fp)
8004ef50  nop 
8004ef54  bnez $v0, 0x8004ef68
8004ef58  nop 
8004ef5c  move $v0, $zero
8004ef60  j 0x8004efb8
8004ef64  nop 
8004ef68  j 0x8004efa4
8004ef6c  nop 
8004ef70  move $a0, $zero
8004ef74  jal 0x80051174
8004ef78  nop 
8004ef7c  sw $v0, 0x14($fp)
8004ef80  lw $v0, 0x14($fp)
8004ef84  nop 
8004ef88  bnez $v0, 0x8004ef9c
8004ef8c  nop 
8004ef90  addiu $v0, $zero, 1
8004ef94  j 0x8004efb8
8004ef98  nop 
8004ef9c  j 0x8004efa4
8004efa0  nop 
8004efa4  j 0x8004eed0
8004efa8  nop 
8004efac  addiu $v0, $zero, 2
8004efb0  j 0x8004efb8
8004efb4  nop 
8004efb8  move $sp, $fp
8004efbc  lw $ra, 0x1c($sp)
8004efc0  lw $fp, 0x18($sp)
8004efc4  addiu $sp, $sp, 0x20
8004efc8  jr $ra
8004efcc  nop 
8004efd0  addiu $sp, $sp, -0x48
8004efd4  sw $ra, 0x40($sp)
8004efd8  sw $fp, 0x3c($sp)
8004efdc  sw $s0, 0x38($sp)
8004efe0  move $fp, $sp
8004efe4  move $s0, $a0
8004efe8  sh $s0, 0x10($fp)
8004efec  addiu $a0, $zero, 0x1a
8004eff0  addiu $a1, $zero, 1
8004eff4  jal 0x80018940
8004eff8  nop 
8004effc  addiu $v0, $zero, 0x30
8004f000  sh $v0, 0x20($fp)
8004f004  addiu $v0, $zero, 0x30
8004f008  sh $v0, 0x22($fp)
8004f00c  addiu $v0, $zero, 0xe
8004f010  sh $v0, 0x24($fp)
8004f014  addiu $v0, $zero, 8
8004f018  sh $v0, 0x26($fp)
8004f01c  sb $zero, 0x28($fp)
8004f020  addiu $a0, $zero, 4
8004f024  addiu $a1, $zero, 1
8004f028  jal 0x80018940
8004f02c  nop 
8004f030  lhu $a0, 0x20($fp)
8004f034  nop 
8004f038  andi $v1, $a0, 0xffff
8004f03c  lui $a0, 0xffff
8004f040  and $v0, $v0, $a0
8004f044  or $v0, $v0, $v1
8004f048  lhu $v1, 0x22($fp)
8004f04c  nop 
8004f050  sll $a0, $v1, 0x10
8004f054  andi $v0, $v0, 0xffff
8004f058  or $v0, $v0, $a0
8004f05c  lhu $a1, 0x24($fp)
8004f060  nop 
8004f064  andi $a0, $a1, 0xffff
8004f068  lui $a1, 0xffff
8004f06c  and $v1, $v1, $a1
8004f070  or $v1, $v1, $a0
8004f074  lhu $a0, 0x26($fp)
8004f078  nop 
8004f07c  sll $a1, $a0, 0x10
8004f080  andi $v1, $v1, 0xffff
8004f084  or $v1, $v1, $a1
8004f088  lhu $a1, 0x28($fp)
8004f08c  nop 
8004f090  andi $a0, $a1, 0xffff
8004f094  lui $a1, 0xffff
8004f098  and $a2, $a2, $a1
8004f09c  or $a2, $a2, $a0
8004f0a0  move $a0, $v0
8004f0a4  move $a1, $v1
8004f0a8  jal 0x80017b18
8004f0ac  nop 
8004f0b0  jal 0x800157b4
8004f0b4  nop 
8004f0b8  addiu $a0, $zero, 0x30
8004f0bc  addiu $a1, $zero, 0x30
8004f0c0  move $a2, $zero
8004f0c4  jal 0x8004f5c8
8004f0c8  nop 
8004f0cc  lui $v0, 0x800d
8004f0d0  lhu $v0, -0x2768($v0)
8004f0d4  nop 
8004f0d8  sh $v0, 0x1a($fp)
8004f0dc  lhu $v0, 0x1a($fp)
8004f0e0  nop 
8004f0e4  andi $v1, $v0, 1
8004f0e8  sh $v1, 0x12($fp)
8004f0ec  lh $v0, 0x1a($fp)
8004f0f0  nop 
8004f0f4  sra $v1, $v0, 1
8004f0f8  move $v0, $v1
8004f0fc  andi $v1, $v0, 1
8004f100  sh $v1, 0x16($fp)
8004f104  lh $v0, 0x1a($fp)
8004f108  nop 
8004f10c  sra $v1, $v0, 8
8004f110  move $v0, $v1
8004f114  andi $v1, $v0, 3
8004f118  sh $v1, 0x14($fp)
8004f11c  lh $v0, 0x12($fp)
8004f120  lh $v1, 0x10($fp)
8004f124  move $a0, $v0
8004f128  move $a1, $v1
8004f12c  jal 0x8004fafc
8004f130  nop 
8004f134  lh $v0, 0x10($fp)
8004f138  lh $v1, 0x1a($fp)
8004f13c  move $a0, $v0
8004f140  move $a1, $v1
8004f144  jal 0x8004fc8c
8004f148  nop 
8004f14c  lhu $v0, 0x10($fp)
8004f150  nop 
8004f154  sh $v0, 0x18($fp)
8004f158  addiu $v0, $zero, 2
8004f15c  sh $v0, 0x30($fp)
8004f160  j 0x8004f170
8004f164  nop 
8004f168  j 0x8004f58c
8004f16c  nop 
8004f170  move $a0, $zero
8004f174  jal 0x80041374
8004f178  nop 
8004f17c  lui $v1, 0x800d
8004f180  lw $v1, -0x25f4($v1)
8004f184  nop 
8004f188  andi $v0, $v1, 0x1000
8004f18c  beqz $v0, 0x8004f1b8
8004f190  nop 
8004f194  lh $v0, 0x18($fp)
8004f198  nop 
8004f19c  blez $v0, 0x8004f1b8
8004f1a0  nop 
8004f1a4  lhu $v0, 0x18($fp)
8004f1a8  nop 
8004f1ac  addiu $v1, $v0, -1
8004f1b0  move $v0, $v1
8004f1b4  sh $v0, 0x18($fp)
8004f1b8  lui $v1, 0x800d
8004f1bc  lw $v1, -0x25f4($v1)
8004f1c0  nop 
8004f1c4  andi $v0, $v1, 0x4000
8004f1c8  beqz $v0, 0x8004f1f8
8004f1cc  nop 
8004f1d0  lh $v0, 0x18($fp)
8004f1d4  nop 
8004f1d8  slti $v1, $v0, 4
8004f1dc  beqz $v1, 0x8004f1f8
8004f1e0  nop 
8004f1e4  lhu $v0, 0x18($fp)
8004f1e8  nop 
8004f1ec  addiu $v1, $v0, 1
8004f1f0  move $v0, $v1
8004f1f4  sh $v0, 0x18($fp)
8004f1f8  lui $v1, 0x800d
8004f1fc  lw $v1, -0x25f4($v1)
8004f200  nop 
8004f204  andi $v0, $v1, 0x2000
8004f208  beqz $v0, 0x8004f2dc
8004f20c  nop 
8004f210  lh $v0, 0x18($fp)
8004f214  addiu $v1, $zero, 3
8004f218  beq $v0, $v1, 0x8004f280
8004f21c  nop 
8004f220  slti $v1, $v0, 4
8004f224  beqz $v1, 0x8004f240
8004f228  nop 
8004f22c  addiu $v1, $zero, 2
8004f230  beq $v0, $v1, 0x8004f254
8004f234  nop 
8004f238  j 0x8004f2dc
8004f23c  nop 
8004f240  addiu $v1, $zero, 4
8004f244  beq $v0, $v1, 0x8004f2b0
8004f248  nop 
8004f24c  j 0x8004f2dc
8004f250  nop 
8004f254  lh $v0, 0x12($fp)
8004f258  nop 
8004f25c  bnez $v0, 0x8004f278
8004f260  nop 
8004f264  lhu $v0, 0x12($fp)
8004f268  nop 
8004f26c  addiu $v1, $v0, 1
8004f270  move $v0, $v1
8004f274  sh $v0, 0x12($fp)
8004f278  j 0x8004f2dc
8004f27c  nop 
8004f280  lh $v0, 0x14($fp)
8004f284  nop 
8004f288  slti $v1, $v0, 2
8004f28c  beqz $v1, 0x8004f2a8
8004f290  nop 
8004f294  lhu $v0, 0x14($fp)
8004f298  nop 
8004f29c  addiu $v1, $v0, 1
8004f2a0  move $v0, $v1
8004f2a4  sh $v0, 0x14($fp)
8004f2a8  j 0x8004f2dc
8004f2ac  nop 
8004f2b0  lh $v0, 0x16($fp)
8004f2b4  nop 
8004f2b8  bnez $v0, 0x8004f2d4
8004f2bc  nop 
8004f2c0  lhu $v0, 0x16($fp)
8004f2c4  nop 
8004f2c8  addiu $v1, $v0, 1
8004f2cc  move $v0, $v1
8004f2d0  sh $v0, 0x16($fp)
8004f2d4  j 0x8004f2dc
8004f2d8  nop 
8004f2dc  lui $v1, 0x800d
8004f2e0  lw $v1, -0x25f4($v1)
8004f2e4  nop 
8004f2e8  andi $v0, $v1, 0x8000
8004f2ec  beqz $v0, 0x8004f3bc
8004f2f0  nop 
8004f2f4  lh $v0, 0x18($fp)
8004f2f8  addiu $v1, $zero, 3
8004f2fc  beq $v0, $v1, 0x8004f364
8004f300  nop 
8004f304  slti $v1, $v0, 4
8004f308  beqz $v1, 0x8004f324
8004f30c  nop 
8004f310  addiu $v1, $zero, 2
8004f314  beq $v0, $v1, 0x8004f338
8004f318  nop 
8004f31c  j 0x8004f3bc
8004f320  nop 
8004f324  addiu $v1, $zero, 4
8004f328  beq $v0, $v1, 0x8004f390
8004f32c  nop 
8004f330  j 0x8004f3bc
8004f334  nop 
8004f338  lh $v0, 0x12($fp)
8004f33c  addiu $v1, $zero, 1
8004f340  bne $v0, $v1, 0x8004f35c
8004f344  nop 
8004f348  lhu $v0, 0x12($fp)
8004f34c  nop 
8004f350  addiu $v1, $v0, -1
8004f354  move $v0, $v1
8004f358  sh $v0, 0x12($fp)
8004f35c  j 0x8004f3bc
8004f360  nop 
8004f364  lh $v0, 0x14($fp)
8004f368  nop 
8004f36c  blez $v0, 0x8004f388
8004f370  nop 
8004f374  lhu $v0, 0x14($fp)
8004f378  nop 
8004f37c  addiu $v1, $v0, -1
8004f380  move $v0, $v1
8004f384  sh $v0, 0x14($fp)
8004f388  j 0x8004f3bc
8004f38c  nop 
8004f390  lh $v0, 0x16($fp)
8004f394  addiu $v1, $zero, 1
8004f398  bne $v0, $v1, 0x8004f3b4
8004f39c  nop 
8004f3a0  lhu $v0, 0x16($fp)
8004f3a4  nop 
8004f3a8  addiu $v1, $v0, -1
8004f3ac  move $v0, $v1
8004f3b0  sh $v0, 0x16($fp)
8004f3b4  j 0x8004f3bc
8004f3b8  nop 
8004f3bc  lui $v1, 0x800d
8004f3c0  lw $v1, -0x25d8($v1)
8004f3c4  nop 
8004f3c8  andi $v0, $v1, 0x20
8004f3cc  beqz $v0, 0x8004f41c
8004f3d0  nop 
8004f3d4  jal 0x80065000
8004f3d8  nop 
8004f3dc  lh $v0, 0x18($fp)
8004f3e0  nop 
8004f3e4  beqz $v0, 0x8004f400
8004f3e8  nop 
8004f3ec  addiu $v1, $zero, 1
8004f3f0  beq $v0, $v1, 0x8004f40c
8004f3f4  nop 
8004f3f8  j 0x8004f41c
8004f3fc  nop 
8004f400  sh $zero, 0x30($fp)
8004f404  j 0x8004f41c
8004f408  nop 
8004f40c  addiu $v0, $zero, 1
8004f410  sh $v0, 0x30($fp)
8004f414  j 0x8004f41c
8004f418  nop 
8004f41c  sh $zero, 0x1a($fp)
8004f420  lhu $v0, 0x1a($fp)
8004f424  lhu $v1, 0x12($fp)
8004f428  nop 
8004f42c  or $v0, $v0, $v1
8004f430  sh $v0, 0x1a($fp)
8004f434  lhu $v0, 0x16($fp)
8004f438  nop 
8004f43c  sll $v1, $v0, 1
8004f440  lhu $v0, 0x1a($fp)
8004f444  nop 
8004f448  or $v0, $v0, $v1
8004f44c  sh $v0, 0x1a($fp)
8004f450  lhu $v0, 0x14($fp)
8004f454  nop 
8004f458  sll $v1, $v0, 8
8004f45c  lhu $v0, 0x1a($fp)
8004f460  nop 
8004f464  or $v0, $v0, $v1
8004f468  sh $v0, 0x1a($fp)
8004f46c  lh $v0, 0x18($fp)
8004f470  nop 
8004f474  sltiu $v1, $v0, 5
8004f478  beqz $v1, 0x8004f534
8004f47c  nop 
8004f480  sll $v1, $v0, 2
8004f484  lui $a0, 0x8001
8004f488  addiu $a0, $a0, 0xa3c
8004f48c  addu $v0, $v1, $a0
8004f490  move $v1, $v0
8004f494  lw $v0, ($v1)
8004f498  nop 
8004f49c  jr $v0
8004f4a0  nop 
8004f4a4  move $a0, $zero
8004f4a8  move $a1, $zero
8004f4ac  jal 0x8004fafc
8004f4b0  nop 
8004f4b4  j 0x8004f534
8004f4b8  nop 
8004f4bc  move $a0, $zero
8004f4c0  addiu $a1, $zero, 1
8004f4c4  jal 0x8004fafc
8004f4c8  nop 
8004f4cc  j 0x8004f534
8004f4d0  nop 
8004f4d4  lh $v0, 0x12($fp)
8004f4d8  nop 
8004f4dc  move $a0, $v0
8004f4e0  addiu $a1, $zero, 2
8004f4e4  jal 0x8004fafc
8004f4e8  nop 
8004f4ec  j 0x8004f534
8004f4f0  nop 
8004f4f4  lh $v0, 0x14($fp)
8004f4f8  nop 
8004f4fc  move $a0, $v0
8004f500  addiu $a1, $zero, 3
8004f504  jal 0x8004fafc
8004f508  nop 
8004f50c  j 0x8004f534
8004f510  nop 
8004f514  lh $v0, 0x16($fp)
8004f518  nop 
8004f51c  move $a0, $v0
8004f520  addiu $a1, $zero, 4
8004f524  jal 0x8004fafc
8004f528  nop 
8004f52c  j 0x8004f534
8004f530  nop 
8004f534  lh $v0, 0x18($fp)
8004f538  lh $v1, 0x1a($fp)
8004f53c  move $a0, $v0
8004f540  move $a1, $v1
8004f544  jal 0x8004fc8c
8004f548  nop 
8004f54c  lui $v1, 0x800d
8004f550  lw $v1, -0x25d8($v1)
8004f554  nop 
8004f558  andi $v0, $v1, 0x800
8004f55c  beqz $v0, 0x8004f56c
8004f560  nop 
8004f564  j 0x8004f58c
8004f568  nop 
8004f56c  lh $v0, 0x30($fp)
8004f570  addiu $v1, $zero, 2
8004f574  beq $v0, $v1, 0x8004f584
8004f578  nop 
8004f57c  j 0x8004f58c
8004f580  nop 
8004f584  j 0x8004f160
8004f588  nop 
8004f58c  lhu $v0, 0x1a($fp)
8004f590  lui $at, 0x800d
8004f594  sh $v0, -0x2768($at)
8004f598  lh $v1, 0x30($fp)
8004f59c  nop 
8004f5a0  move $v0, $v1
8004f5a4  j 0x8004f5ac
8004f5a8  nop 
8004f5ac  move $sp, $fp
8004f5b0  lw $ra, 0x40($sp)
8004f5b4  lw $fp, 0x3c($sp)
8004f5b8  lw $s0, 0x38($sp)
8004f5bc  addiu $sp, $sp, 0x48
8004f5c0  jr $ra
8004f5c4  nop 
