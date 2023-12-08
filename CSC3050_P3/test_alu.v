// `include "alu.v"

`timescale 1ns/1ps

module test_alu();
    reg [31:0] instruction, regA, regB;
    wire [31:0] result;
    wire [2:0] flags;  // Flags wire should be 3 bits to match the ALU module
    reg [15:0] immediate;

    // Instantiate the ALU module
    alu test(
        .instruction(instruction),
        .regA(regA),
        .regB(regB),
        .result(result), 
        .flags(flags)
    );

    initial begin
        $dumpfile("test.vcd");
        $dumpvars(0, test_alu);

        $monitor("Time: %3d\n  Instr : %32b\n  regA  : %32b\n  regB  : %32b\n  result: %32b\nIn Decimals:\n  regA  : %d\n  regB  : %d\n  result: %d\nFlags: \n  zero    : %b\n  negative: %b\n  overflow: %b\n----------------------------------------------",
        $time, instruction, regA, regB, result, regA, regB, result, flags[2], flags[1], flags[0]);


        // Test cases for each instruction

        // ADD (R-type) overflow detection
        $display("Testing ADD...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100000}; // R-type format for ADD
        regA = 32'h7FFFFFFF; // Largest positive 32-bit number
        regB = 1;
        #20;

        // ADDI (I-type) overflow detection
        $display("Testing ADDI...");
        immediate = 1;
        $display("--imm--%d", immediate);
        instruction = {6'b001000, 5'd0, 5'd0, immediate}; // I-type format for ADDI
        regA = 32'h7FFFFFFF;
        // regB is not used for ADDI
        #20;

        // ADDU (R-type)
        $display("Testing ADDU...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100001}; // R-type format for ADDU
        regA = 2;
        regB = 32'h7FFFFFFF; // -2 in two's complement
        #20;

        // ADDIU (I-type)
        $display("Testing ADDIU...");
        immediate = 16'hFFFF;
        $display("--imm--%d", immediate);
        instruction = {6'b001001, 5'd0, 5'd0, immediate}; // I-type format for ADDIU
        regA = 32'h7FFFFFFF; // Largest positive 32-bit number
        #20;

        // SUB (R-type) overflow detection
        $display("Testing SUB...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100010}; // R-type format for SUB
        regA = -30;
        regB = -31;
        #20;

        // SUBU (R-type)
        $display("Testing SUBU...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100011}; // R-type format for SUBU
        regA = -30;
        regB = -31;
        #20;

        // AND (R-type)
        $display("Testing AND...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100100}; // R-type format for AND
        regA = 32'b1100;
        regB = 32'b1010;
        #20;

        // ANDI (I-type)
        $display("Testing ANDI...");
        immediate = 16'b0000000000001100;
        $display("--imm--%b", immediate);
        instruction = {6'b001100, 5'd0, 5'd0, immediate}; // I-type format for ANDI
        regA = 32'b1100;
        // regB is not used for ANDI
        #20;

        // NOR (R-type)
        $display("Testing NOR...");
        immediate = 6'b100111;
        $display("--imm--%b", immediate);
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, immediate}; // R-type format for NOR
        regA = 32'b1100;
        regB = 32'b1010;
        #20;

        // OR (R-type)
        $display("Testing OR...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100101}; // R-type format for OR
        regA = 32'b1100;
        regB = 32'b1010;
        #20;

        // ORI (I-type)
        $display("Testing ORI...");
        immediate = 16'b0000000000001101;
        $display("--imm--%b", immediate);
        instruction = {6'b001101, 5'd0, 5'd0, immediate}; // I-type format for ORI
        regA = 32'b1100;
        // regB is not used for ORI
        #20;

        // XOR (R-type)
        $display("Testing XOR...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100110}; // R-type format for XOR
        regA = 32'b1100;
        regB = 32'b1010;
        #20;

        // XORI (I-type)
        $display("Testing XORI...");
        immediate = 16'b0000000000000011;
        $display("--imm--%b", immediate);
        instruction = {6'b001110, 5'd0, 5'd0, immediate}; // I-type format for XORI
        regA = 32'b1100;
        // regB is not used for XORI
        #20;

        // BEQ (I-type) zero detection
        $display("Testing BEQ...");
        immediate = 0;
        $display("--imm--%d", immediate);
        instruction = {6'b000100, 5'd0, 5'd0, immediate}; // I-type format for BEQ
        regA = 32'd10;
        regB = 32'd10;
        #20;

        // BNE (I-type) zero detection
        $display("Testing BNE...");
        immediate = 0;
        $display("--imm--%d", immediate);
        instruction = {6'b000101, 5'd0, 5'd0, immediate}; // I-type format for BNE
        regA = 32'd10;
        regB = 32'd20;
        #20;

        // SLT (R-type) negative detection
        $display("Testing SLT...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b101010}; // R-type format for SLT
        regA = 32'd10;
        regB = 32'd20;
        #20;

        // SLTI (I-type) negative detection
        $display("Testing SLTI...");
        instruction = {6'b001010, 5'd0, 5'd0, 16'b0000000000000010}; // I-type format for SLTI
        regA = 32'd5;
        regB = 32'd0; // regB is not used for SLTI
        #20;

        // SLTIU (I-type) negative detection
        $display("Testing SLTIU...");
        instruction = {6'b001011, 5'd0, 5'd0, 16'b0000000000000010}; // I-type format for SLTIU
        regA = 32'd20;
        regB = 32'd0; // regB is not used for SLTIU
        #20;

        // SLTU (R-type) negative detection
        $display("Testing SLTU...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b101011}; // R-type format for SLTU
        regA = 32'd10;
        regB = 32'd20;
        #20;

        // LW (I-type)
        $display("Testing LW...");
        instruction = {6'b100011, 5'd0, 5'd0, 16'b0000000000000010}; // I-type format for LW
        regA = 32'd0; // base register
        regB = 32'd0; // offset
        #20;

        // SW (I-type)
        $display("Testing SW...");
        instruction = {6'b101011, 5'd0, 5'd0, 16'b0000000000000010}; // I-type format for SW
        regA = 32'd0; // base register
        regB = 32'd10; // offset
        #20;

        // SLL (R-type)
        $display("Testing SLL...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd10, 5'd0, 6'b000000}; // R-type format for SLL
        regA = 32'd5;
        regB = 32'd0; // regB is not used for SLL
        #20;

        // SLLV (R-type)
        $display("Testing SLLV...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd2, 5'd0, 6'b000100}; // R-type format for SLLV
        regA = 32'd8;
        regB = 32'd0; // regB is not used for SLLV
        #20;

        // SRL (R-type)
        $display("Testing SRL...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd10, 5'd0, 6'b000010}; // R-type format for SRL
        regA = 32'd1024;
        regB = 32'd0; // regB is not used for SRL
        #20;

        // SRLV (R-type)
        $display("Testing SRLV...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd2, 5'd0, 6'b000110}; // R-type format for SRLV
        regA = 32'd1024;
        regB = 32'd0; // regB is not used for SRLV
        #20;

        // SRA (R-type)
        $display("Testing SRA...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd10, 5'd0, 6'b000011}; // R-type format for SRA
        regA = 32'hF0000000; // negative number
        regB = 32'd0; // regB is not used for SRA
        #20;

        // SRAV (R-type)
        $display("Testing SRAV...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd2, 5'd0, 6'b000111}; // R-type format for SRAV
        regA = 32'hF0000000; // negative number
        regB = 32'd0; // regB is not used for SRAV
        #20;

        // Complete the test
        $finish;
    end
endmodule
