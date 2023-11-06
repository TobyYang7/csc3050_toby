// `include "alu.v"

`timescale 1ns/1ps

module test_alu();
    reg [31:0] instruction, regA, regB;
    wire [31:0] result;
    wire [2:0] flags;  // Flags wire should be 3 bits to match the ALU module

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

        $monitor("Time: %3d. Instruction: %32b\n regA: %32b, regB: %32b\n result: %32b, flags: Z=%b N=%b O=%b\n",
        $time, instruction, regA, regB, result, flags[2], flags[1], flags[0]);

        // Test cases for each instruction

        // ADD (R-type)
        $display("Testing ADD...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100000}; // R-type format for ADD
        regA = 32'd10;
        regB = 32'd20;
        #20;

        // ADDI (I-type)
        $display("Testing ADDI...");
        instruction = {6'b001000, 5'd0, 5'd0, 16'd5}; // I-type format for ADDI
        regA = 32'd15;
        regB = 32'd0; // regB is not used for ADDI
        #20;

        // ADDU (R-type)
        $display("Testing ADDU...");
        instruction = {6'b000000, 5'd0, 5'd0, 5'd0, 5'd0, 6'b100001}; // R-type format for ADDU
        regA = 32'd1;
        regB = 32'hFFFFFFFE; // -2 in two's complement
        #20;

        // ADDIU (I-type)
        $display("Testing ADDIU...");
        instruction = {6'b001001, 5'd0, 5'd0, 16'hFFFF}; // I-type format for ADDIU
        regA = 32'h7FFFFFFF; // Largest positive 32-bit number
        #20;

        // todo: Continue with SUB, SUBU, AND, ANDI, NOR, OR, ORI, XOR, XORI, BEQ, BNE, SLT, SLTI, SLTIU, SLTU, LW, SW, SLL, SLLV, SRL, SRLV, SRA, SRAV

        // Complete the test
        $finish;
    end
endmodule
