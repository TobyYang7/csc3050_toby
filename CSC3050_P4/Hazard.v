
module HAZARD_UNIT (
    /* forward unit */
    input [5:0] Opcode_D,
    input [5:0] Funct_D,
    input [2:0] PC_Src_S,
    input RegWrite_E,
    input RegWrite_M,
    input RegWrite_W,
    input MemtoReg_E,
    input MemtoReg_M,
    input MemtoReg_W,
    input [4:0] WriteReg_E,
    input [4:0] WriteReg_M,
    input [4:0] WriteReg_W,
    input [4:0] Rs_E,
    input [4:0] Rt_E,
    output wire [1:0] ForwardA_E,
    output wire [1:0] ForwardB_E,
    /* stall unit */
    input [4:0] Rs_D,
    input [4:0] Rt_D,
    output wire Stall_F,
    output wire Stall_D,
    output wire Flush_E,
    output wire Flush_D,
    output wire waiting
);
    wire waiting_for_A = Forward_D(
        RegWrite_E, 
        RegWrite_M, 
        RegWrite_W, 
        WriteReg_E,
        WriteReg_M,
        WriteReg_W,
        Rs_D
        );
    wire waiting_for_B = Forward_D(
        RegWrite_E, 
        RegWrite_M, 
        RegWrite_W, 
        WriteReg_E,
        WriteReg_M,
        WriteReg_W,
        Rt_D
        );

    
    assign Flush_D = (PC_Src_S != 3'b000) ? 1 :0;

    assign waiting = (((waiting_for_A | waiting_for_B)) != 2'b0) ? 1: 0;

    assign ForwardA_E = Forward_E(
        RegWrite_M, 
        RegWrite_W, 
        WriteReg_M,
        WriteReg_W,
        Rs_E
        );
    assign ForwardB_E = Forward_E(
        RegWrite_M, 
        RegWrite_W, 
        WriteReg_M,
        WriteReg_W,
        Rt_E
        );
    assign Flush_E = Stall(
        Opcode_D,
        Funct_D,
        MemtoReg_E,
        MemtoReg_M,
        MemtoReg_W,
        Rs_D,
        Rt_D,
        WriteReg_E,
        WriteReg_M,
        WriteReg_W
        );
    assign Stall_F = Flush_E;
    assign Stall_D = Stall_F;

    function [1-1:0] Forward_D;
        input RegWrite_E;
        input RegWrite_M;
        input RegWrite_W;
        input [4:0] WriteReg_E;
        input [4:0] WriteReg_M;
        input [4:0] WriteReg_W;
        input [4:0] R_E;
        begin 
            if (RegWrite_E && WriteReg_E == R_E) begin
                Forward_D = 1'b1;
            end else if (RegWrite_M && WriteReg_M == R_E) begin
                Forward_D = 1'b1;
            end else if (RegWrite_W && WriteReg_W == R_E) begin
                Forward_D = 1'b1;
            end else begin
                Forward_D = 1'b0;
            end
        end
    endfunction

    function [2-1:0] Forward_E;
        input RegWrite_M;
        input RegWrite_W;
        input [4:0] WriteReg_M;
        input [4:0] WriteReg_W;
        input [4:0] R_E;
        begin
            if (RegWrite_M && WriteReg_M == R_E) begin
                Forward_E = 2'b10;
            end else if (RegWrite_W && WriteReg_W == R_E) begin
                Forward_E = 2'b01;
            end else begin
                Forward_E = 2'b00;
            end
        end
    endfunction

    function [1-1:0] Stall;
        input [5:0] Opcode_D;
        input [5:0] Funct_D;
        input MemtoReg_E;
        input MemtoReg_M;
        input MemtoReg_W;
        input [4:0] Rs_D;
        input [4:0] Rt_D;
        input [4:0] WriteReg_E;
        input [4:0] WriteReg_M;
        input [4:0] WriteReg_W;
        begin 
            if ((Opcode_D == 6'b000000 && Funct_D == 6'b001000) || Opcode_D == 6'b000100 || Opcode_D == 6'b000101) begin
                Stall = 1'b0;
            end else if ((MemtoReg_E && (WriteReg_E == Rs_D || WriteReg_E == Rt_D)) || (MemtoReg_M && (WriteReg_M == Rs_D || WriteReg_M == Rt_D)) || (MemtoReg_W && (WriteReg_W == Rs_D || WriteReg_W == Rt_D))) begin
                Stall = 1'b1;
            end else begin
                Stall = 1'b0;
            end
        end
    endfunction

endmodule