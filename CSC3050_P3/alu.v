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

    reg [31:0] temp_reg;
    reg zero, negative, overflow; // flags

    assign opcode = instruction[31:26];

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

    // fetch register values
    always @(*) begin
        // Fetching register values from regA and regB based on rs and rt
        rs_reg = (rs == 5'b00000) ? 0 : regA;
        rt_reg = (rt == 5'b00000) ? 0 : regB;
    end

    // execute different instructions
    always @(*) begin
        zero = 0;
        negative = 0;
        overflow = 0;

        // ALU operations based on opcode and funct
        case (opcode)
            // R-type instructions
            6'b000000: begin
                case (funct)
                    // add, addu, and, or, xor, nor
                    6'b100000, 6'b100001, 6'b100100, 6'b100101, 6'b100110, 6'b100111: begin
                        temp_reg = rs_reg + rt_reg;
                        overflow = (temp_reg[31] != rs_reg[31]) && (temp_reg[31] != rt_reg[31]);
                    end
                    // sub, subu
                    6'b100010, 6'b100011: begin
                        temp_reg = rs_reg - rt_reg;
                        overflow = (temp_reg[31] != rs_reg[31]) && (temp_reg[31] != ~rt_reg[31]);
                    end
                    // sll, sllv, srl, srlv, sra
                    6'b000000, 6'b000010, 6'b000011, 6'b000110, 6'b000111: begin
                        temp_reg = (funct == 6'b000000) ? (rt_reg << shamt) :
                                   (funct == 6'b000010) ? (rt_reg << rs_reg[4:0]) :
                                   (funct == 6'b000011) ? (rt_reg >> shamt) : 
                                   (funct == 6'b000110) ? (rt_reg >> rs_reg[4:0]) :
                                   (funct == 6'b000111) ? ($signed(rt_reg) >>> shamt) : 0;
                    end
                    default: begin
                        temp_reg = 0;
                    end
                endcase
            end

            // I-type instructions
            6'b001000, // addi
            6'b001100, // andi
            6'b001101: // ori
                begin
                    temp_reg = rs_reg + {16'b0, immediate};
                    overflow = (temp_reg[31] != rs_reg[31]) && (temp_reg[31] != immediate[15]);
                end
            6'b001110: // xori
                begin
                    temp_reg = rs_reg ^ {16'b0, immediate};
                end
            6'b000100, // beq
            6'b000101: // bne
                begin
                    zero = (rs_reg == rt_reg) ? 1'b1 : 1'b0;
                    negative = 1'b0; // Reset negative flag for branch instructions
                end
            6'b001010: // slti
                begin
                    temp_reg = (rs_reg < $signed(immediate)) ? 1 : 0;
                    negative = temp_reg;
                end
            6'b001011: // sltiu
                begin
                    temp_reg = ($unsigned(rs_reg) < $unsigned(immediate)) ? 1 : 0;
                end
            6'b101011, // sw
            6'b100011: // lw
                begin
                    temp_reg = rs_reg + {16'b0, immediate};
                end
            default: begin
                temp_reg = 0;
            end
        endcase
    end

    // return result and flags
    always @(*) begin
        result = temp_reg;
        flags = {zero, negative, overflow};
    end
endmodule
