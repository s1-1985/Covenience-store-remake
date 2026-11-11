80062484  addiu $sp, $sp, -0x28
80062488  sw $ra, 0x24($sp)
8006248c  sw $fp, 0x20($sp)
80062490  move $fp, $sp
80062494  jal 0x8006b81c
80062498  nop 
8006249c  jal 0x8004eeb8
800624a0  nop 
800624a4  sw $v0, 0x10($fp)
800624a8  jal 0x80065000
800624ac  nop 
800624b0  lw $v0, 0x10($fp)
800624b4  addiu $v1, $zero, 1
800624b8  bne $v0, $v1, 0x800625c4
800624bc  nop 
800624c0  jal 0x8006bc40
800624c4  nop 
800624c8  jal 0x8005c61c
800624cc  nop 
800624d0  lui $at, 0x8014
800624d4  sw $zero, -0x6750($at)
800624d8  lui $v0, 0x8014
800624dc  lw $v0, -0x6750($v0)
800624e0  nop 
800624e4  slti $v1, $v0, 0x32
800624e8  bnez $v1, 0x800624f8
800624ec  nop 
800624f0  j 0x80062544
800624f4  nop 
800624f8  lui $v0, 0x8014
800624fc  lw $v0, -0x6750($v0)
80062500  nop 
80062504  move $a0, $v0
80062508  sll $v1, $a0, 2
8006250c  addu $v1, $v1, $v0
80062510  sll $v0, $v1, 5
80062514  lui $at, 0x8013
80062518  addu $at, $at, $v0
8006251c  sb $zero, 0x7970($at)
80062520  lui $v1, 0x8014
80062524  lw $v1, -0x6750($v1)
80062528  nop 
8006252c  addiu $v0, $v1, 1
80062530  move $v1, $v0
80062534  lui $at, 0x8014
80062538  sw $v1, -0x6750($at)
8006253c  j 0x800624d8
80062540  nop 
80062544  lui $at, 0x8014
80062548  sw $zero, -0x6748($at)
8006254c  lui $at, 0x8014
80062550  sw $zero, -0x674c($at)
80062554  lui $at, 0x8014
80062558  sw $zero, -0x6750($at)
8006255c  lui $at, 0x800d
80062560  sw $zero, -0x2600($at)
80062564  lui $at, 0x800d
80062568  sw $zero, -0x2748($at)
8006256c  addiu $v0, $zero, -1
80062570  lui $at, 0x800d
80062574  sw $v0, -0x264c($at)
80062578  lui $at, 0x800d
8006257c  sw $zero, -0x280c($at)
80062580  lui $at, 0x800d
80062584  sw $zero, -0x265c($at)
80062588  move $a0, $zero
8006258c  move $a1, $zero
80062590  jal 0x80062a4c
80062594  nop 
80062598  addiu $v0, $zero, 1
8006259c  lui $at, 0x8014
800625a0  sb $v0, -0x6744($at)
800625a4  jal 0x80023c20
800625a8  nop 
800625ac  jal 0x8002619c
800625b0  nop 
800625b4  jal 0x8006dbf0
800625b8  nop 
800625bc  jal 0x80066234
800625c0  nop 
800625c4  lui $v0, 0x800d
800625c8  lhu $v0, -0x2768($v0)
800625cc  nop 
800625d0  andi $v1, $v0, 1
800625d4  sll $a0, $v1, 0x10
800625d8  sra $v0, $a0, 0x10
800625dc  beqz $v0, 0x800625f4
800625e0  nop 
800625e4  lui $at, 0x800d
800625e8  sb $zero, -0x27cc($at)
800625ec  j 0x80062600
800625f0  nop 
800625f4  addiu $v0, $zero, 1
800625f8  lui $at, 0x800d
800625fc  sb $v0, -0x27cc($at)
80062600  lui $v0, 0x800d
80062604  lhu $v0, -0x2768($v0)
80062608  nop 
8006260c  andi $v1, $v0, 2
80062610  sll $a0, $v1, 0x10
80062614  sra $v0, $a0, 0x10
80062618  beqz $v0, 0x80062630
8006261c  nop 
80062620  lui $at, 0x800d
80062624  sb $zero, -0x27cb($at)
80062628  j 0x8006263c
8006262c  nop 
80062630  addiu $v0, $zero, 1
80062634  lui $at, 0x800d
80062638  sb $v0, -0x27cb($at)
8006263c  lui $v0, 0x800d
80062640  lh $v0, -0x2768($v0)
80062644  nop 
80062648  sra $v1, $v0, 8
8006264c  move $v0, $v1
80062650  addiu $v1, $v0, 1
80062654  lui $at, 0x800d
80062658  sb $v1, -0x2757($at)
8006265c  lui $v0, 0x800d
80062660  lb $v0, -0x2757($v0)
80062664  nop 
80062668  move $v1, $v0
8006266c  sll $v0, $v1, 2
80062670  lui $v1, 0x800a
80062674  addiu $v1, $v1, -0x679c
80062678  addu $v0, $v0, $v1
8006267c  move $v1, $v0
80062680  lw $a0, ($v1)
80062684  move $a1, $zero
80062688  jal 0x80065100
8006268c  nop 
80062690  jal 0x80065974
80062694  nop 
80062698  addiu $v0, $zero, -1
8006269c  j 0x800626a4
800626a0  nop 
800626a4  move $sp, $fp
800626a8  lw $ra, 0x24($sp)
800626ac  lw $fp, 0x20($sp)
800626b0  addiu $sp, $sp, 0x28
800626b4  jr $ra
800626b8  nop 
800626bc  addiu $sp, $sp, -0x48
800626c0  sw $ra, 0x44($sp)
800626c4  sw $fp, 0x40($sp)
800626c8  move $fp, $sp
800626cc  sw $zero, 0x18($fp)
800626d0  j 0x800626e0
800626d4  nop 
800626d8  j 0x80062940
800626dc  nop 
800626e0  jal 0x80065974
800626e4  nop 
800626e8  addiu $v0, $zero, 0x22
800626ec  sh $v0, 0x20($fp)
