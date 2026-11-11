80051174  addiu $sp, $sp, -0x48
80051178  sw $ra, 0x40($sp)
8005117c  sw $fp, 0x3c($sp)
80051180  sw $s0, 0x38($sp)
80051184  move $fp, $sp
80051188  move $s0, $a0
8005118c  sb $s0, 0x10($fp)
80051190  lui $v0, 0x8018
80051194  ori $v0, $v0, 0x7e00
80051198  sw $v0, 0x30($fp)
8005119c  addiu $v0, $zero, 0x20
800511a0  sh $v0, 0x18($fp)
800511a4  addiu $v0, $zero, 0x30
800511a8  sh $v0, 0x1a($fp)
800511ac  addiu $v0, $zero, 0x10
800511b0  sh $v0, 0x1c($fp)
800511b4  addiu $v0, $zero, 5
800511b8  sh $v0, 0x1e($fp)
800511bc  sb $zero, 0x20($fp)
800511c0  addiu $a0, $zero, 4
800511c4  addiu $a1, $zero, 1
800511c8  jal 0x80018940
800511cc  nop 
800511d0  lhu $a0, 0x18($fp)
800511d4  nop 
800511d8  andi $v1, $a0, 0xffff
800511dc  lui $a0, 0xffff
800511e0  and $v0, $v0, $a0
800511e4  or $v0, $v0, $v1
800511e8  lhu $v1, 0x1a($fp)
800511ec  nop 
800511f0  sll $a0, $v1, 0x10
800511f4  andi $v0, $v0, 0xffff
800511f8  or $v0, $v0, $a0
800511fc  lhu $a1, 0x1c($fp)
80051200  nop 
80051204  andi $a0, $a1, 0xffff
80051208  lui $a1, 0xffff
8005120c  and $v1, $v1, $a1
80051210  or $v1, $v1, $a0
80051214  lhu $a0, 0x1e($fp)
80051218  nop 
8005121c  sll $a1, $a0, 0x10
80051220  andi $v1, $v1, 0xffff
80051224  or $v1, $v1, $a1
80051228  lhu $a1, 0x20($fp)
8005122c  nop 
80051230  andi $a0, $a1, 0xffff
80051234  lui $a1, 0xffff
80051238  and $a2, $a2, $a1
8005123c  or $a2, $a2, $a0
80051240  move $a0, $v0
80051244  move $a1, $v1
80051248  jal 0x80017b18
8005124c  nop 
80051250  sb $zero, 0x2c($fp)
80051254  j 0x80051264
80051258  nop 
8005125c  j 0x800514fc
80051260  nop 
80051264  lb $v0, 0x2c($fp)
80051268  nop 
8005126c  bnez $v0, 0x8005129c
80051270  nop 
80051274  addiu $v0, $zero, 0x78
80051278  sh $v0, 0x18($fp)
8005127c  addiu $v0, $zero, 0x18
80051280  sh $v0, 0x1c($fp)
80051284  addiu $a0, $zero, 0x8e
80051288  addiu $a1, $zero, 0x6b
8005128c  jal 0x8004e938
80051290  nop 
80051294  j 0x800512bc
80051298  nop 
8005129c  addiu $v0, $zero, 0x98
800512a0  sh $v0, 0x18($fp)
800512a4  addiu $v0, $zero, 0x24
800512a8  sh $v0, 0x1c($fp)
800512ac  addiu $a0, $zero, 0xba
800512b0  addiu $a1, $zero, 0x6b
800512b4  jal 0x8004e938
800512b8  nop 
800512bc  addiu $v0, $zero, 0x60
800512c0  sh $v0, 0x1a($fp)
800512c4  addiu $v0, $zero, 0x10
800512c8  sh $v0, 0x1e($fp)
800512cc  sb $zero, 0x20($fp)
800512d0  addiu $a0, $zero, 0x10
800512d4  addiu $a1, $zero, 1
800512d8  jal 0x80018940
800512dc  nop 
800512e0  lhu $a0, 0x18($fp)
800512e4  nop 
800512e8  andi $v1, $a0, 0xffff
800512ec  lui $a0, 0xffff
800512f0  and $v0, $v0, $a0
800512f4  or $v0, $v0, $v1
800512f8  lhu $v1, 0x1a($fp)
800512fc  nop 
80051300  sll $a0, $v1, 0x10
80051304  andi $v0, $v0, 0xffff
80051308  or $v0, $v0, $a0
8005130c  lhu $a1, 0x1c($fp)
80051310  nop 
80051314  andi $a0, $a1, 0xffff
80051318  lui $a1, 0xffff
8005131c  and $v1, $v1, $a1
80051320  or $v1, $v1, $a0
80051324  lhu $a0, 0x1e($fp)
80051328  nop 
8005132c  sll $a1, $a0, 0x10
80051330  andi $v1, $v1, 0xffff
80051334  or $v1, $v1, $a1
80051338  lhu $a1, 0x20($fp)
8005133c  nop 
80051340  andi $a0, $a1, 0xffff
80051344  lui $a1, 0xffff
80051348  and $a2, $a2, $a1
8005134c  or $a2, $a2, $a0
80051350  move $a0, $v0
80051354  move $a1, $v1
80051358  move $a3, $zero
8005135c  jal 0x800182d0
80051360  nop 
80051364  lui $at, 0x800d
80051368  sh $v0, -0x25ec($at)
8005136c  jal 0x800157b4
80051370  nop 
80051374  addiu $a0, $zero, 2
80051378  addiu $a1, $zero, 1
8005137c  jal 0x80018940
80051380  nop 
80051384  addiu $a0, $zero, 0x20
80051388  addiu $a1, $zero, 0x30
8005138c  addiu $a2, $zero, 2
80051390  jal 0x8004f5c8
80051394  nop 
80051398  addiu $a0, $zero, 0x78
8005139c  addiu $a1, $zero, 0x60
800513a0  addiu $a2, $zero, 0x1c8
800513a4  jal 0x8004e494
800513a8  nop 
800513ac  move $a0, $zero
800513b0  jal 0x80041374
800513b4  nop 
800513b8  lui $v1, 0x800d
800513bc  lw $v1, -0x25f4($v1)
800513c0  nop 
800513c4  andi $v0, $v1, 0x2000
800513c8  beqz $v0, 0x800513e8
800513cc  nop 
800513d0  lb $v0, 0x2c($fp)
800513d4  nop 
800513d8  bnez $v0, 0x800513e8
800513dc  nop 
800513e0  addiu $v0, $zero, 1
800513e4  sb $v0, 0x2c($fp)
800513e8  lui $v1, 0x800d
800513ec  lw $v1, -0x25f4($v1)
800513f0  nop 
800513f4  andi $v0, $v1, 0x8000
800513f8  beqz $v0, 0x80051414
800513fc  nop 
80051400  lb $v0, 0x2c($fp)
80051404  addiu $v1, $zero, 1
80051408  bne $v0, $v1, 0x80051414
8005140c  nop 
80051410  sb $zero, 0x2c($fp)
80051414  lui $v1, 0x800d
80051418  lw $v1, -0x25d8($v1)
8005141c  nop 
80051420  andi $v0, $v1, 0x20
80051424  beqz $v0, 0x800514c4
80051428  nop 
8005142c  lb $v0, 0x2c($fp)
80051430  nop 
80051434  bnez $v0, 0x800514ac
80051438  nop 
8005143c  addiu $a0, $zero, -1
80051440  move $a1, $zero
80051444  jal 0x80065100
80051448  nop 
8005144c  jal 0x80065000
80051450  nop 
80051454  addiu $a0, $zero, 2
80051458  jal 0x80089ca4
8005145c  nop 
80051460  lb $v0, 0x10($fp)
80051464  nop 
80051468  move $a0, $v0
8005146c  jal 0x80051524
80051470  nop 
80051474  sw $v0, 0x28($fp)
80051478  addiu $a0, $zero, 2
8005147c  jal 0x80089ca4
80051480  nop 
80051484  lui $at, 0x800d
80051488  sw $zero, -0x25d8($at)
8005148c  lw $v0, 0x28($fp)
80051490  nop 
80051494  bnez $v0, 0x800514a4
80051498  nop 
8005149c  j 0x800514fc
800514a0  nop 
800514a4  j 0x800514c4
800514a8  nop 
800514ac  addiu $v0, $zero, -1
800514b0  sw $v0, 0x28($fp)
800514b4  jal 0x80065040
800514b8  nop 
800514bc  j 0x800514fc
800514c0  nop 
800514c4  lui $v1, 0x800d
800514c8  lw $v1, -0x25d8($v1)
800514cc  nop 
800514d0  andi $v0, $v1, 0x40
800514d4  beqz $v0, 0x800514f4
800514d8  nop 
800514dc  addiu $v0, $zero, -1
800514e0  sw $v0, 0x28($fp)
800514e4  jal 0x80065040
800514e8  nop 
800514ec  j 0x800514fc
800514f0  nop 
800514f4  j 0x80051254
800514f8  nop 
800514fc  lw $v0, 0x28($fp)
80051500  j 0x80051508
80051504  nop 
80051508  move $sp, $fp
8005150c  lw $ra, 0x40($sp)
80051510  lw $fp, 0x3c($sp)
80051514  lw $s0, 0x38($sp)
80051518  addiu $sp, $sp, 0x48
8005151c  jr $ra
80051520  nop 
80051524  addiu $sp, $sp, -0x30
80051528  sw $ra, 0x28($sp)
8005152c  sw $fp, 0x24($sp)
80051530  sw $s0, 0x20($sp)
80051534  move $fp, $sp
80051538  move $s0, $a0
8005153c  sb $s0, 0x10($fp)
80051540  addiu $a0, $zero, 2
80051544  jal 0x80089ca4
80051548  nop 
8005154c  addiu $a0, $zero, -1
80051550  jal 0x80064e4c
80051554  nop 
80051558  addiu $a0, $zero, 2
8005155c  jal 0x80089ca4
80051560  nop 
80051564  addiu $a0, $zero, 0x10
80051568  move $a1, $zero
8005156c  jal 0x80018940
80051570  nop 
80051574  jal 0x800157b4
80051578  nop 
8005157c  jal 0x8004ea68
80051580  nop 
80051584  jal 0x800157b4
80051588  nop 
8005158c  addiu $a0, $zero, 0x40
80051590  addiu $a1, $zero, 0x40
80051594  addiu $a2, $zero, 0x1e6
80051598  jal 0x8004e494
8005159c  nop 
800515a0  addiu $a0, $zero, 0x40
800515a4  addiu $a1, $zero, 0x60
800515a8  addiu $a2, $zero, 0x1e2
800515ac  jal 0x8004e494
800515b0  nop 
800515b4  jal 0x80018a5c
800515b8  nop 
800515bc  jal 0x80018a5c
800515c0  nop 
800515c4  addiu $a0, $zero, 1
800515c8  jal 0x8007b1f8
800515cc  nop 
800515d0  addiu $a0, $zero, 2
800515d4  jal 0x80089ca4
800515d8  nop 
800515dc  lui $v0, 0x800d
800515e0  lb $v0, -0x27e0($v0)
800515e4  nop 
800515e8  beqz $v0, 0x800515f8
800515ec  nop 
800515f0  j 0x800517f4
800515f4  nop 
800515f8  jal 0x800157b4
800515fc  nop 
80051600  addiu $a0, $zero, 0x40
80051604  addiu $a1, $zero, 0x40
80051608  addiu $a2, $zero, 0x1e4
8005160c  jal 0x8004e494
80051610  nop 
80051614  jal 0x80018a5c
80051618  nop 
8005161c  jal 0x80018a5c
80051620  nop 
80051624  addiu $a0, $zero, 2
80051628  jal 0x80089ca4
8005162c  nop 
80051630  move $a0, $zero
80051634  jal 0x8007ab2c
80051638  nop 
8005163c  addiu $a0, $zero, 2
80051640  jal 0x80089ca4
80051644  nop 
80051648  addiu $a0, $zero, 1
8005164c  jal 0x8007ab2c
80051650  nop 
80051654  addiu $a0, $zero, 2
80051658  jal 0x80089ca4
8005165c  nop 
80051660  lui $v0, 0x800d
80051664  lb $v0, -0x27e0($v0)
80051668  nop 
8005166c  bnez $v0, 0x8005177c
80051670  nop 
80051674  jal 0x800157b4
80051678  nop 
8005167c  jal 0x8005188c
80051680  nop 
80051684  sw $v0, 0x14($fp)
80051688  lw $v0, 0x14($fp)
8005168c  addiu $v1, $zero, -1
80051690  bne $v0, $v1, 0x80051708
80051694  nop 
80051698  addiu $a0, $zero, 0x40
8005169c  addiu $a1, $zero, 0x50
800516a0  addiu $a2, $zero, 0x1f2
800516a4  jal 0x8004e494
800516a8  nop 
800516ac  sw $zero, 0x18($fp)
800516b0  lw $v0, 0x18($fp)
800516b4  nop 
800516b8  slti $v1, $v0, 8
800516bc  bnez $v1, 0x800516cc
800516c0  nop 
800516c4  j 0x800516f0
800516c8  nop 
800516cc  jal 0x80018a5c
800516d0  nop 
800516d4  lw $v1, 0x18($fp)
800516d8  nop 
800516dc  addiu $v0, $v1, 1
800516e0  move $v1, $v0
800516e4  sw $v1, 0x18($fp)
800516e8  j 0x800516b0
800516ec  nop 
800516f0  addiu $v0, $zero, -1
800516f4  sw $v0, 0x14($fp)
800516f8  j 0x80051828
800516fc  nop 
80051700  j 0x8005176c
80051704  nop 
80051708  addiu $a0, $zero, 0x40
8005170c  addiu $a1, $zero, 0x40
80051710  addiu $a2, $zero, 0x1e9
80051714  jal 0x8004e494
80051718  nop 
8005171c  sw $zero, 0x18($fp)
80051720  lw $v0, 0x18($fp)
80051724  nop 
80051728  slti $v1, $v0, 8
8005172c  bnez $v1, 0x8005173c
80051730  nop 
80051734  j 0x80051760
80051738  nop 
8005173c  jal 0x80018a5c
80051740  nop 
80051744  lw $v1, 0x18($fp)
80051748  nop 
8005174c  addiu $v0, $v1, 1
80051750  move $v1, $v0
80051754  sw $v1, 0x18($fp)
80051758  j 0x80051720
8005175c  nop 
80051760  sw $zero, 0x14($fp)
80051764  j 0x80051828
80051768  nop 
8005176c  j 0x80051828
80051770  nop 
80051774  j 0x800517ec
80051778  nop 
8005177c  jal 0x800157b4
80051780  nop 
80051784  addiu $a0, $zero, 0x40
80051788  addiu $a1, $zero, 0x50
8005178c  addiu $a2, $zero, 0x1ec
80051790  jal 0x8004e494
80051794  nop 
80051798  sw $zero, 0x18($fp)
8005179c  lw $v0, 0x18($fp)
800517a0  nop 
800517a4  slti $v1, $v0, 8
800517a8  bnez $v1, 0x800517b8
800517ac  nop 
800517b0  j 0x800517dc
800517b4  nop 
800517b8  jal 0x80018a5c
800517bc  nop 
800517c0  lw $v1, 0x18($fp)
800517c4  nop 
800517c8  addiu $v0, $v1, 1
800517cc  move $v1, $v0
800517d0  sw $v1, 0x18($fp)
800517d4  j 0x8005179c
800517d8  nop 
800517dc  addiu $v0, $zero, -1
800517e0  sw $v0, 0x14($fp)
800517e4  j 0x80051828
800517e8  nop 
800517ec  j 0x80051828
800517f0  nop 
800517f4  jal 0x800157b4
800517f8  nop 
800517fc  lui $v0, 0x800d
80051800  lb $v0, -0x27e0($v0)
80051804  nop 
80051808  move $a0, $v0
8005180c  addiu $a1, $zero, 0x40
80051810  addiu $a2, $zero, 0x40
80051814  jal 0x80050fc8
80051818  nop 
8005181c  sw $v0, 0x14($fp)
80051820  j 0x80051828
80051824  nop 
80051828  j 0x80051838
8005182c  nop 
80051830  j 0x80051870
80051834  nop 
80051838  move $a0, $zero
8005183c  jal 0x80041374
80051840  nop 
80051844  lui $v1, 0x800d
80051848  lw $v1, -0x25d8($v1)
8005184c  nop 
80051850  andi $v0, $v1, 0x40
80051854  beqz $v0, 0x80051868
80051858  nop 
8005185c  lw $v0, 0x14($fp)
80051860  j 0x80051870
80051864  nop 
80051868  j 0x80051828
8005186c  nop 
80051870  move $sp, $fp
80051874  lw $ra, 0x28($sp)
80051878  lw $fp, 0x24($sp)
8005187c  lw $s0, 0x20($sp)
80051880  addiu $sp, $sp, 0x30
80051884  jr $ra
80051888  nop 
8005188c  addiu $sp, $sp, -0x28
80051890  sw $ra, 0x24($sp)
80051894  sw $fp, 0x20($sp)
80051898  move $fp, $sp
8005189c  lui $v0, 0x8018
800518a0  ori $v0, $v0, 0x7e00
800518a4  sw $v0, 0x1c($fp)
800518a8  lw $v0, 0x1c($fp)
800518ac  lui $at, 2
800518b0  addu $at, $v0, $at
800518b4  lw $v1, -0x6858($at)
800518b8  nop 
800518bc  sw $v1, 0x14($fp)
800518c0  jal 0x8006db4c
800518c4  nop 
800518c8  sw $v0, 0x18($fp)
800518cc  lw $v0, 0x14($fp)
800518d0  lw $v1, 0x18($fp)
800518d4  nop 
800518d8  bne $v0, $v1, 0x800518ec
800518dc  nop 
