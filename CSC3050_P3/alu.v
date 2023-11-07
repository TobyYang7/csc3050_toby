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
reg [31:0] extended_immediate;
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
        (opcode == 6'b000000 && funct == 6'b100010)) begin // sub
        // Overflow occurs if the signs of the inputs are the same and the sign of the result is different
        overflow_flag = ((regA[31] == regB[31]) && (result[31] != regA[31]));
    end else if (opcode == 6'b001000) begin // addi
        // For addi, sign extend the immediate and check for overflow
        // Assuming 'immediate' is 16 bits and needs to be sign-extended to 32 bits
        extended_immediate = {{16{immediate[15]}}, immediate};
        overflow_flag = ((regA[31] == extended_immediate[31]) && (result[31] != regA[31]));
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

    //Zero-extend immediate for I-type instructions
    if (opcode == 6'b001001 || opcode == 6'b001011 || opcode == 6'b001110) begin
        immediate = {{16{1'b0}}, immediate};
    end
end

// Fetch registers with sign consideration based on the instruction type
always @(*) begin
    // Defaults for rs and rt
    rs_reg = regA;
    rt_reg = regB;

    case (opcode)
        6'b000000: begin // R-type instructions
            case (funct)
                // Signed operations
                6'b100000, // add
                6'b100010, // sub
                6'b101010: // slt
                    begin
                        rs_reg = $signed(regA);
                        rt_reg = $signed(regB);
                    end
                // Unsigned operations
                6'b100001, // addu
                6'b100011, // subu
                6'b101011: // sltu
                    begin
                        rs_reg = $unsigned(regA);
                        rt_reg = $unsigned(regB);
                    end
                // Shift operations and logical operations don't require signed/unsigned distinction
            endcase
        end
        // I-type instructions
        6'b001000, // addi
        6'b001010: // slti
            begin
                rs_reg = $signed(regA);
                // Immediate is sign-extended in the instruction parsing step
            end
        6'b001001, // addiu
        6'b001011: // sltiu
            begin
                rs_reg = $unsigned(regA);
                // Immediate is zero-extended in the instruction parsing step
            end
    endcase
end


// execute different instructions
always @(*) begin
    // initialize flags
    zero = 0;
    negative = 0;
    overflow = 0;

    // add
    if (opcode == 6'b000000 && funct == 6'b100000) begin
        temp_reg = rs_reg + rt_reg;
        $display("--add--%d = %d + %d", temp_reg, rs_reg, rt_reg);
    end

    // addi
    if (opcode == 6'b001000) begin
        temp_reg = rs_reg + immediate;
        $display("--addi--%d = %d + %d", temp_reg, rs_reg, immediate);
    end

    //addu
    if (opcode == 6'b000000 && funct == 6'b100001) begin
        temp_reg = rs_reg + rt_reg;
        $display("--addu--%d = %d + %d", temp_reg, rs_reg, rt_reg);
    end

    //addiu
    if (opcode == 6'b001001) begin
        temp_reg = rs_reg + immediate;
        $display("--addiu--%d = %d + %d", temp_reg, rs_reg, immediate);
    end

    //sub
    if (opcode == 6'b000000 && funct == 6'b100010) begin
        temp_reg = rs_reg - rt_reg;
        $display("--sub--%d = %d - %d", temp_reg, rs_reg, rt_reg);
    end

    //subu
    if (opcode == 6'b000000 && funct == 6'b100011) begin
        temp_reg = rs_reg - rt_reg;
        $display("--subu--%d = %d - %d", temp_reg, rs_reg, rt_reg);
    end

    //and
    if (opcode == 6'b000000 && funct == 6'b100100) begin
        temp_reg = rs_reg & rt_reg;
        $display("--and--%d = %d & %d", temp_reg, rs_reg, rt_reg);
    end

    //andi
    if (opcode == 6'b001100) begin
        temp_reg = rs_reg & immediate;
        $display("--andi--%d = %d & %d", temp_reg, rs_reg, immediate);
    end

    //nor
    if (opcode == 6'b000000 && funct == 6'b100111) begin
        temp_reg = ~(rs_reg | rt_reg);
        $display("--nor--%d = ~(%d | %d)", temp_reg, rs_reg, rt_reg);
    end

    //or
    if (opcode == 6'b000000 && funct == 6'b100101) begin
        temp_reg = rs_reg | rt_reg;
        $display("--or--%d = %d | %d", temp_reg, rs_reg, rt_reg);
    end

    //ori
    if (opcode == 6'b001101) begin
        temp_reg = rs_reg | immediate;
        $display("--ori--%d = %d | %d", temp_reg, rs_reg, immediate);
    end

    //xor
    if (opcode == 6'b000000 && funct == 6'b100110) begin
        temp_reg = rs_reg ^ rt_reg;
        $display("--xor--%d = %d ^ %d", temp_reg, rs_reg, rt_reg);
    end

    //xori
    if (opcode == 6'b001110) begin
        temp_reg = rs_reg ^ immediate;
        $display("--xori--%d = %d ^ %d", temp_reg, rs_reg, immediate);
    end

    //beq
    if (opcode == 6'b000100) begin
        if (rs_reg == rt_reg) begin
            temp_reg = immediate;
            $display("--beq--%d = %d", temp_reg, immediate);
        end
    end

    //bne
    if (opcode == 6'b000101) begin
        if (rs_reg != rt_reg) begin
            temp_reg = immediate;
            $display("--bne--%d = %d", temp_reg, immediate);
        end
    end

    //slt
    if (opcode == 6'b000000 && funct == 6'b101010) begin
        temp_reg = (rs_reg < rt_reg) ? 1 : 0;
        $display("--slt--%d = %d < %d", temp_reg, rs_reg, rt_reg);
    end

    //slti
    if (opcode == 6'b001010) begin
        temp_reg = (rs_reg < immediate) ? 1 : 0;
        $display("--slti--%d = %d < %d", temp_reg, rs_reg, immediate);
    end

    //sltiu
    if (opcode == 6'b001011) begin
        temp_reg = (rs_reg < immediate) ? 1 : 0;
        $display("--sltiu--%d = %d < %d", temp_reg, rs_reg, immediate);
    end

    //sltu
    if (opcode == 6'b000000 && funct == 6'b101011) begin
        temp_reg = (rs_reg < rt_reg) ? 1 : 0;
        $display("--sltu--%d = %d < %d", temp_reg, rs_reg, rt_reg);
    end

    //lw
    if (opcode == 6'b100011) begin
        temp_reg = regA + immediate;
        $display("--lw--%d = %d + %d", temp_reg, regA, immediate);
    end

    //sw
    if (opcode == 6'b101011) begin
        temp_reg = regA + immediate;
        $display("--sw--%d = %d + %d", temp_reg, regA, immediate);
    end

    //sll
    if (opcode == 6'b000000 && funct == 6'b000000) begin
        temp_reg = rt_reg << shamt;
        $display("--sll--%d = %d << %d", temp_reg, rt_reg, shamt);
    end

    //sllv
    if (opcode == 6'b000000 && funct == 6'b000100) begin
        temp_reg = rt_reg << rs_reg;
        $display("--sllv--%d = %d << %d", temp_reg, rt_reg, rs_reg);
    end

    //srl
    if (opcode == 6'b000000 && funct == 6'b000010) begin
        temp_reg = rt_reg >> shamt;
        $display("--srl--%d = %d >> %d", temp_reg, rt_reg, shamt);
    end

    //srlv
    if (opcode == 6'b000000 && funct == 6'b000110) begin
        temp_reg = rt_reg >> rs_reg;
        $display("--srlv--%d = %d >> %d", temp_reg, rt_reg, rs_reg);
    end

    //sra
    if (opcode == 6'b000000 && funct == 6'b000011) begin
        temp_reg = rt_reg >>> shamt;
        $display("--sra--%d = %d >>> %d", temp_reg, rt_reg, shamt);
    end

    //srav
    if (opcode == 6'b000000 && funct == 6'b000111) begin
        temp_reg = rt_reg >>> rs_reg;
        $display("--srav--%d = %d >>> %d", temp_reg, rt_reg, rs_reg);
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
