module alu(
    input [31:0] instruction, 
    input [31:0] regA, 
    input [31:0] regB, 
    output reg [31:0] result, 
    output reg [2:0] flags
);

wire [5:0] opcode;
reg [5:0] funct;
reg [4:0] rs, rt, rd, shamt;
reg [15:0] immediate;
reg [31:0] rs_reg, rt_reg;
integer i; // sra, srav
assign opcode = instruction[31:26];

// result
reg [31:0] temp_reg;
reg zero, negative, overflow; // flags

// task update_flags;
//     input [31:0] result;
//     input zero_flag_in;
//     input negative_flag_in;
//     input overflow_flag_in;
//     output reg zero_flag_out;
//     output reg negative_flag_out;
//     output reg overflow_flag_out;
// begin
//     zero_flag_out = zero_flag_in ? 1'b1 : result == 32'b0;
//     negative_flag_out = negative_flag_in ? 1'b1 : result[31];
//     overflow_flag_out = overflow_flag_in; // Overflow flag typically set during arithmetic operations
// end
// endtask

task update_flags;
    input [5:0] opcode;      // The opcode of the current instruction
    input [5:0] funct;       // The function field for R-type instructions
    input [31:0] result;     // The result of the computation
    input [31:0] regA;       // Value of the source register
    input [31:0] regB;       // Value of the target register or immediate value
    output reg zero_flag;    // The zero flag output
    output reg negative_flag;// The negative flag output
    output reg overflow_flag;// The overflow flag output
begin
    // Reset flags
    zero_flag = 0;
    negative_flag = 0;
    overflow_flag = 0;

    // Check for overflow flag conditions
    if ((opcode == 6'b000000 && funct == 6'b100000) || // add
        (opcode == 6'b001000) || // addi
        (opcode == 6'b000000 && funct == 6'b100010)) begin // sub
        // Overflow occurs if the signs of the inputs are the same and the sign of the result is different
        overflow_flag = ((regA[31] == regB[31]) && (result[31] != regA[31]));
    end

    // Check for zero flag conditions
    if (opcode == 6'b000100 || // beq
        opcode == 6'b000101) begin // bne
        zero_flag = (result == 0);
    end

    // Check for negative flag conditions
    if ((opcode == 6'b000000 && (funct == 6'b101010 || funct == 6'b101011)) || // slt, sltu
        (opcode == 6'b001010 || opcode == 6'b001011)) begin // slti, sltiu
        negative_flag = result[31];
    end
end
endtask

// parse instruction
always @(*) begin
    // Extracting fields from the instruction
    funct = instruction[5:0];
    rs = instruction[25:21];
    rt = instruction[20:16];
    rd = instruction[15:11];
    shamt = instruction[10:6];
    immediate = instruction[15:0];

    // Sign-extend immediate for I-type instructions
    if (opcode == 6'b001000 || opcode == 6'b001100 || opcode == 6'b001101) begin
        immediate = {{16{instruction[15]}}, immediate};
    end
end

// execute different instructions
always @(*) begin
    // todo: implement the instructions: add, addi, addu, addiu, sub, subu, and, andi, nor, or, ori, xor, xori, beq, bne, slt, slti, sltiu, sltu, lw, sw sll, sllv, srl, srlv, sra, srav
    // initialize flags
    zero = 0;
    negative = 0;
    overflow = 0;

    // add
    if (opcode == 6'b000000 && funct == 6'b100000) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform addition
        temp_reg = rs_reg + rt_reg;
        $display("--add--%d = %d + %d", temp_reg, rs_reg, rt_reg);
    end

    // addi
    if (opcode == 6'b001000) begin
        // fetch registers
        rs_reg = regA;

        // perform addition
        temp_reg = rs_reg + immediate;
        $display("--addi--%d = %d + %d", temp_reg, rs_reg, immediate);
    end

    //addu
    if (opcode == 6'b000000 && funct == 6'b100001) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform addition
        temp_reg = rs_reg + rt_reg;
        $display("--addu--%d = %d + %d", temp_reg, rs_reg, rt_reg);
    end

    //addiu
    if (opcode == 6'b001001) begin
        // fetch registers
        rs_reg = regA;

        // perform addition
        temp_reg = rs_reg + immediate;
        $display("--addiu--%d = %d + %d", temp_reg, rs_reg, immediate);
    end

    //sub
    if (opcode == 6'b000000 && funct == 6'b100010) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform subtraction
        temp_reg = rs_reg - rt_reg;
        $display("--sub--%d = %d - %d", temp_reg, rs_reg, rt_reg);
    end

    //subu
    if (opcode == 6'b000000 && funct == 6'b100011) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform subtraction
        temp_reg = rs_reg - rt_reg;
        $display("--subu--%d = %d - %d", temp_reg, rs_reg, rt_reg);
    end

    //and
    if (opcode == 6'b000000 && funct == 6'b100100) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform and
        temp_reg = rs_reg & rt_reg;
        $display("--and--%d = %d & %d", temp_reg, rs_reg, rt_reg);
    end

    //andi
    if (opcode == 6'b001100) begin
        // fetch registers
        rs_reg = regA;

        // perform and
        temp_reg = rs_reg & immediate;
        $display("--andi--%d = %d & %d", temp_reg, rs_reg, immediate);
    end

    //nor
    if (opcode == 6'b000000 && funct == 6'b100111) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform nor
        temp_reg = ~(rs_reg | rt_reg);
        $display("--nor--%d = ~(%d | %d)", temp_reg, rs_reg, rt_reg);
    end

    //or
    if (opcode == 6'b000000 && funct == 6'b100101) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform or
        temp_reg = rs_reg | rt_reg;
        $display("--or--%d = %d | %d", temp_reg, rs_reg, rt_reg);
    end

    //ori
    if (opcode == 6'b001101) begin
        // fetch registers
        rs_reg = regA;

        // perform or
        temp_reg = rs_reg | immediate;
        $display("--ori--%d = %d | %d", temp_reg, rs_reg, immediate);
    end

    //xor
    if (opcode == 6'b000000 && funct == 6'b100110) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform xor
        temp_reg = rs_reg ^ rt_reg;
        $display("--xor--%d = %d ^ %d", temp_reg, rs_reg, rt_reg);
    end

    //xori
    if (opcode == 6'b001110) begin
        // fetch registers
        rs_reg = regA;

        // perform xor
        temp_reg = rs_reg ^ immediate;
        $display("--xori--%d = %d ^ %d", temp_reg, rs_reg, immediate);
    end

    //beq
    if (opcode == 6'b000100) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform beq
        if (rs_reg == rt_reg) begin
            temp_reg = immediate;
            $display("--beq--%d = %d", temp_reg, immediate);
        end
    end

    //bne
    if (opcode == 6'b000101) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform bne
        if (rs_reg != rt_reg) begin
            temp_reg = immediate;
            $display("--bne--%d = %d", temp_reg, immediate);
        end
    end

    //slt
    if (opcode == 6'b000000 && funct == 6'b101010) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform slt
        temp_reg = (rs_reg < rt_reg) ? 1 : 0;
        $display("--slt--%d = %d < %d", temp_reg, rs_reg, rt_reg);
    end

    //slti
    if (opcode == 6'b001010) begin
        // fetch registers
        rs_reg = regA;

        // perform slt
        temp_reg = (rs_reg < immediate) ? 1 : 0;
        $display("--slti--%d = %d < %d", temp_reg, rs_reg, immediate);
    end

    //sltiu
    if (opcode == 6'b001011) begin
        // fetch registers
        rs_reg = regA;

        // perform slt
        temp_reg = (rs_reg < immediate) ? 1 : 0;
        $display("--sltiu--%d = %d < %d", temp_reg, rs_reg, immediate);
    end

    //sltu
    if (opcode == 6'b000000 && funct == 6'b101011) begin
        // fetch registers
        rs_reg = regA;
        rt_reg = regB;

        // perform slt
        temp_reg = (rs_reg < rt_reg) ? 1 : 0;
        $display("--sltu--%d = %d < %d", temp_reg, rs_reg, rt_reg);
    end



    // update_flags(temp_reg, zero, negative, overflow, zero, negative, overflow);
    update_flags(opcode, funct, temp_reg, regA, regB, zero, negative, overflow);
end

// return result
always @(*) begin
    result = temp_reg;
    flags = {zero, negative, overflow};
end

endmodule
