	.file	"victim.c"
	.intel_syntax noprefix
	.text
	.globl	user_buf
	.bss
	.align 4096
	.type	user_buf, @object
	.size	user_buf, 266
user_buf:
	.zero	266
	.globl	kernel_buf
	.section	.kernel_buf,"aw"
	.align 4096
	.type	kernel_buf, @object
	.size	kernel_buf, 4
kernel_buf:
	.ascii	"\007\020\002\005"
	.text
	.globl	victim
	.type	victim, @function
victim:
.LFB0:
	.cfi_startproc
	push	rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	mov	rbp, rsp
	.cfi_def_cfa_register 6
	mov	DWORD PTR [rbp-36], edi
	mov	DWORD PTR [rbp-4], 0
	cmp	DWORD PTR [rbp-36], 195948557
	je	.L2
	mov	DWORD PTR [rbp-8], 0
	jmp	.L3
.L4:
	movabs	rdx, OFFSET FLAT:kernel_buf
	mov	eax, DWORD PTR [rbp-8]
	movzx	eax, BYTE PTR [rdx+rax]
	mov	BYTE PTR [rbp-17], al
	movzx	eax, BYTE PTR [rbp-17]
	movabs	rdx, OFFSET FLAT:user_buf
	cdqe
	movzx	eax, BYTE PTR [rdx+rax]
	movzx	eax, al
	add	DWORD PTR [rbp-4], eax
	add	DWORD PTR [rbp-8], 1
.L3:
	cmp	DWORD PTR [rbp-8], 3
	jbe	.L4
	jmp	.L5
.L2:
	mov	DWORD PTR [rbp-12], 1
	jmp	.L6
.L7:
	mov	eax, DWORD PTR [rbp-12]
	lea	edx, [rax+256]
	movabs	rax, OFFSET FLAT:user_buf
	mov	edx, edx
	movzx	eax, BYTE PTR [rax+rdx]
	movzx	eax, al
	add	DWORD PTR [rbp-4], eax
	add	DWORD PTR [rbp-12], 1
.L6:
	cmp	DWORD PTR [rbp-12], 3
	jbe	.L7
.L5:
	mov	DWORD PTR [rbp-16], 0
	jmp	.L8
.L9:
	movabs	rdx, OFFSET FLAT:user_buf
	mov	eax, DWORD PTR [rbp-16]
	movzx	eax, BYTE PTR [rdx+rax]
	movzx	eax, al
	add	DWORD PTR [rbp-4], eax
	add	DWORD PTR [rbp-16], 1
.L8:
	cmp	DWORD PTR [rbp-16], 255
	jbe	.L9
	mov	eax, DWORD PTR [rbp-4]
	pop	rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	victim, .-victim
	.ident	"GCC: (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0"
	.section	.note.GNU-stack,"",@progbits
