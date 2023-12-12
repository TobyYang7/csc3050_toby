// The ID_EX register, you need to do some implementation here.
module ID_EX (
    input CLOCK,
    /* control unit input */
    input RegWrite_in,
    input MemtoReg_in,
    input MemWrite_in,
    input [5:0] Opcode_in,
    input [5:0] Funct_in,
    input ALUSrc_in,
    input RegDst_in,
    /* register input */
    input [31:0] regA_data_in,
    input [31:0] regB_data_in,
    input [4:0] Rs_in,
    input [4:0] Rt_in,
    input [4:0] Rd_in,
    input [4:0] Sa_in,
    /* others input (3)*/
    input [31:0] se_imme_in,
    input Flush,

    /* control unit output */
    output reg RegWrite_out,
    output reg MemtoReg_out,
    output reg MemWrite_out,
    output reg [5:0] Opcode_out,
    output reg [5:0] Funct_out,
    output reg ALUSrc_out,
    output reg RegDst_out,

    /* register output */
    output reg [31:0] regA_data_out,
    output reg [31:0] regB_data_out,
    output reg [4:0] Rs_out,
    output reg [4:0] Rt_out,
    output reg [4:0] Rd_out,
    output reg [4:0] Sa_out,
    /* others output */
    output reg [31:0] se_imme_out
);
    always@(posedge CLOCK) begin
        RegWrite_out <= RegWrite_in;
        MemtoReg_out <= MemtoReg_in;
        MemWrite_out <= MemWrite_in;
        Opcode_out <= Opcode_in;
        Funct_out <= Funct_in;
        ALUSrc_out <= ALUSrc_in;
        RegDst_out <= RegDst_in;
        regA_data_out <= regA_data_in;
        regB_data_out <= regB_data_in;
        Rs_out <= Rs_in;
        Rt_out <= Rt_in;
        Rd_out <= Rd_in;
        Sa_out <= Sa_in;
        se_imme_out <= se_imme_in;
    end
endmodule


// The ALU unit, you need to do some implementation here.
module ALU (
    input [31:0] SrcA,
    input [31:0] SrcB,
    input [4:0] SrcC, // for shift
    input [5:0] Opcode,
    input [5:0] Funct,
    output [31:0] result,
    output reg zero,
    output reg neg
);
    assign result = result_out(SrcA, SrcB, SrcC, Opcode, Funct);

    function [31:0] result_out;
        input [31:0] SrcA;
        input [31:0] SrcB;
        input [4:0] SrcC;
        input [5:0] Opcode;
        input [5:0] Funct;
    begin
        zero = 0;
        neg = 0;
        result_out = 0;

        // $display("------------\nA  : %b\nB  : %b", SrcA, SrcB);

        //todo: ALU

        //add
        if (Opcode == 6'b000000 && Funct == 6'b100000) begin
            result_out = SrcA + SrcB;
            if (result_out == 0) begin
                zero = 1;
            end
            if (result_out < 0) begin
                neg = 1;
            end
            // $display("A  : %b\nB  : %b\nC  :%d\nRES: %b\n", SrcA, SrcB, SrcC, result_out);
        end
        //addu
        if (Opcode == 6'b000000 && Funct == 6'b100001) begin
            result_out = $unsigned(SrcA) + $unsigned(SrcB);
            if (result_out == 0) begin
                zero = 1;
            end
            if (result_out < 0) begin
                neg = 1;
            end
        end
        //addi
        if (Opcode == 6'b001000) begin
            result_out = $signed(SrcA) + $signed({{16{SrcB[15]}}, SrcB[15:0]});
            if (result_out == 0) begin
                zero = 1;
            end
            if (result_out < 0) begin
                neg = 1;
            end
            // $display("addi\nA  : %d\nB  : %d\nC  :%d\nRES: %d\n", $signed(SrcA), $signed({{16{SrcB[15]}}, SrcB[15:0]}), SrcC, $signed(result_out));
        end
        //addiu
        if (Opcode == 6'b001001) begin
            result_out = $signed(SrcA) + $unsigned({{16{SrcB[15]}}, SrcB[15:0]});
            if (result_out == 0) begin
                zero = 1;
            end
            if (result_out < 0) begin
                neg = 1;
            end
            // $display("addiu\nA  : %b\nB  : %b\nC  :%d\nRES: %d\n", SrcA, SrcB, SrcC, result_out);
        end
        //sub
        if (Opcode == 6'b000000 && Funct == 6'b100010) begin
            result_out = $signed(SrcA) - $signed(SrcB);
            if (result_out == 0) begin
                zero = 1;
            end
            if (result_out < 0) begin
                neg = 1;
            end
            // $display("sub\nA  : %d\nB  : %d\nC  :%d\nRES: %d\n", SrcA, $signed(SrcB), SrcC, $signed(result_out));
        end
        //subu
        if (Opcode == 6'b000000 && Funct == 6'b100011) begin
            result_out = SrcA - SrcB;
            if (result_out == 0) begin
                zero = 1;
            end
            if (result_out < 0) begin
                neg = 1;
            end
        end
        //and
        if (Opcode == 6'b000000 && Funct == 6'b100100) begin
            result_out = SrcA & SrcB;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //andi
        if (Opcode == 6'b001100) begin
            result_out = SrcA & SrcB;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //nor
        if (Opcode == 6'b000000 && Funct == 6'b100111) begin
            result_out = ~(SrcA | SrcB);
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //or
        if (Opcode == 6'b000000 && Funct == 6'b100101) begin
            result_out = SrcA | SrcB;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //ori
        if (Opcode == 6'b001101) begin
            result_out = SrcA | {{24{SrcB[15]}}, SrcB[15:0]};
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //xor
        if (Opcode == 6'b000000 && Funct == 6'b100110) begin
            result_out = SrcA ^ SrcB;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //xori
        if (Opcode == 6'b001110) begin
            result_out = $signed(SrcA) ^ SrcB[15:0];
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //sll
        if (Opcode == 6'b000000 && Funct == 6'b000000) begin
            result_out = SrcB << SrcC;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //sllv
        if (Opcode == 6'b000000 && Funct == 6'b000100) begin
            result_out = SrcB << SrcA;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //srl
        if (Opcode == 6'b000000 && Funct == 6'b000010) begin
            result_out = SrcB >> SrcC;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //srlv
        if (Opcode == 6'b000000 && Funct == 6'b000110) begin
            result_out = SrcB >> SrcA;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //sra
        if (Opcode == 6'b000000 && Funct == 6'b000011) begin
            result_out = $signed(SrcB) >>> SrcC;
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //srav
        if (Opcode == 6'b000000 && Funct == 6'b000111) begin
            result_out = $signed(SrcB) >>> $signed(SrcA);
            if (result_out == 0) begin
                zero = 1;
            end
        end
        //beq
        if (Opcode == 6'b000100) begin
            if (SrcA == SrcB) begin
                result_out = 1;
            end
        end
        //bne
        if (Opcode == 6'b000101) begin
            if (SrcA != SrcB) begin
                result_out = 1;
            end
        end
        //slt
        if (Opcode == 6'b000000 && Funct == 6'b101010) begin
            if ($signed(SrcA) < $signed(SrcB)) begin
                result_out = 1;
            end
        end
        //lw
        if (Opcode == 6'b100011) begin
            result_out = SrcA + $signed({{16{SrcB[15]}}, SrcB[15:0]});
        end
        //sw
        if (Opcode == 6'b101011) begin
            result_out = SrcA + $signed({{16{SrcB[15]}}, SrcB[15:0]});
        end

        // $display("res: %b", result_out);

    end
    endfunction
endmodule