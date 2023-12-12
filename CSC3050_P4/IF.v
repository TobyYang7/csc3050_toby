// PC register storing next PC values. Here the stall input is used to create a stall
module PC (
    input CLOCK,
    input [31:0] PC_in,
    input Stall,
    output reg [31:0] PC_out
);
    initial begin
        PC_out = 32'b0;
    end

    always@(posedge CLOCK) begin
        if (Stall != 1'b1) begin
            PC_out <= PC_in;
        end
    end
endmodule


// add PC by 4
module PC_ADD4 (
    input [31:0] PC_org,
    output wire [31:0] PC_add4
);
    assign PC_add4 = PC_org + 32'd4;
endmodule


// select for PC_pre. Here the branch, jump, waiting inputs are used to handle branch and jump.
module PC_SRC (
    input Branch, 
    input Jump,
    input waiting,
    input [5:0] Opcode,
    input [5:0] Funct,
    input [31:0] regA_val,
    input [31:0] regB_val,
    output wire [2:0] S
);
    assign S = bj_S(
        regA_val, 
        regB_val, 
        Jump, 
        Branch, 
        Opcode, 
        Funct, 
        waiting
        );

    function [3-1:0] bj_S;
        input regA_val;
        input regB_val;
        input Jump;
        input Branch;
        input [5:0] Opcode;
        input [5:0] Funct;
        input waiting;
    begin
        if (Branch == 1'b1) begin // branch
            if ((Opcode == 6'b000100 && regA_val == regB_val)
                || (Opcode == 6'b000101 && regA_val != regB_val)) // beq, bne
            begin
                if (Opcode == 6'b000100) begin
                    // $display("beq");
                end
                if (Opcode == 6'b000101) begin
                    // $display("bne");
                end
                if (waiting == 0) begin
                    bj_S = 3'b001;        
                end
                else if (waiting == 1) begin
                    bj_S = 3'b100;
                end
            end
            else begin
                bj_S = 3'b000;
            end
        end
        else if (Jump == 1'b1) begin // jump
            if ((Opcode == 6'b000010 )
                | (Opcode == 6'b000011 )) // j, jal
            begin
                if(Opcode == 6'b000011) begin
                    // $display("jal");
                end
                if(Opcode == 6'b000010) begin
                    // $display("j");
                end
                if (waiting == 0) begin
                    bj_S = 3'b010;        
                end
                else if (waiting == 1) begin
                    bj_S = 3'b100;
                end
            end
            else if (Opcode == 6'b000000) // jr
            begin
                // $display("jr");
                if (waiting == 0) begin
                    bj_S = 3'b011;
                end
                else if (waiting == 1) begin
                    bj_S = 3'b100;
                end
            end
            else begin
                bj_S = 3'b000;
            end
        end
        else if (Branch == 1'b0 && Jump == 1'b0) begin // normal
            bj_S = 3'b000;
        end
        else begin
            bj_S = 3'b000;
        end
    end
    endfunction

endmodule



// The implementation of some MUX
// The first one is given as an example,
// You should implement the others by yourself.
module MUX2_BIT5 (
    input [4:0] A0,
    input [4:0] A1,
    input S,
    output [4:0] Y
);
    assign Y = Y_out(A0, A1, S);
    function [4:0] Y_out;
        input [4:0] A0;
        input [4:0] A1;
        input S;
        case(S)
        2'b00: Y_out = A0;
        2'b01: Y_out = A1;
        endcase
    endfunction
endmodule


module MUX2_BIT32 (
    input [31:0] A0,
    input [31:0] A1,
    input S,
    output [31:0] Y
);
    assign Y = Y_out(A0, A1, S);
    function [31:0] Y_out;
        input [31:0] A0;
        input [31:0] A1;
        input S;
        begin
            case(S)
                1'b0: Y_out = A0;
                1'b1: Y_out = A1;
            endcase
        end
    endfunction
endmodule

module MUX3_BIT32 (
    input [31:0] A0,
    input [31:0] A1,
    input [31:0] A2,
    input [1:0] S,
    output [31:0] Y
);
    assign Y = Y_out(A0, A1, A2, S);
    function [31:0] Y_out;
        input [31:0] A0;
        input [31:0] A1;
        input [31:0] A2;
        input [1:0] S;
        begin
            case(S)
            2'b00: Y_out = A0;
            2'b01: Y_out = A1;
            2'b10: Y_out = A2;
            endcase
        end
    endfunction
endmodule

module MUX4_BIT32 (
    input [31:0] A0,
    input [31:0] A1,
    input [31:0] A2,
    input [31:0] A3,
    input [1:0] S,
    output [31:0] Y
);
    assign Y = Y_out(A0, A1, A2, A3, S);
    function [31:0] Y_out;
        input [31:0] A0;
        input [31:0] A1;
        input [31:0] A2;
        input [31:0] A3;
        input [1:0] S;
        begin
            case(S)
            2'b00: Y_out = A0;
            2'b01: Y_out = A1;
            2'b10: Y_out = A2;
            2'b11: Y_out = A3;
            endcase
        end
    endfunction
endmodule

module MUX5_BIT32 (
    input [31:0] A0,
    input [31:0] A1,
    input [31:0] A2,
    input [31:0] A3,
    input [31:0] A4,
    input [2:0] S,
    output [31:0] Y
);
    assign Y = Y_out(A0, A1, A2, A3, A4, S);
    function [31:0] Y_out;
        input [31:0] A0;
        input [31:0] A1;
        input [31:0] A2;
        input [31:0] A3;
        input [31:0] A4;
        input [2:0] S;
        begin
            case(S)
            3'b000: Y_out = A0;
            3'b001: Y_out = A1;
            3'b010: Y_out = A2;
            3'b011: Y_out = A3;
            3'b100: Y_out = A4;
            endcase
        end
    endfunction
endmodule


// The instruction memory: fetch instruction based on PC
module INSTR_MEM (
    input CLOCK,
    // instruction mem
    input [31:0] PC_in,
    output reg fin_sign,
    output wire [31:0] inst_out
);
    reg [31:0] RAM [0:512-1]; // RAM
    reg [2:0] cnt = 3'b000; // finish counter
    reg change_sign = 0; // finish
    integer out_file; // output file
    integer i; // iterating number

    // read instr from file
    initial begin
        fin_sign = 0;
        for (i = 0; i <= 512-1; i=i+1) begin
            RAM[i] = 32'b0;
        end
        $readmemb("CPU_instruction.bin", RAM);
    end

    // finish getting instr
    always@(PC_in) begin
        if (!(RAM[PC_in/4] != 32'hffffffff && change_sign == 0)) begin
            change_sign = 1;
        end
        else begin
        end
    end

    // finish help part
    always@(posedge CLOCK) begin
        if (change_sign == 1) begin
            cnt = cnt+1;
        end
        if ( cnt == 3'b111) begin
            fin_sign = 1;
        end
    end

    assign inst_out = RAM[PC_in/4];

endmodule