`timescale 1ns/1ps

module cpu_test ();
    // clock signal settings
    reg clock;
    parameter time_period = 10;

    // VCD dump settings
    initial begin
        $dumpfile("cpu_test.vcd");
        $dumpvars(0, cpu_test);
    end

    // DUT instantiation
    CPU testedCPU(
        .CLK(clock)
    );

    // generate the clock signal
    initial begin
        clock = 0;
    end

    always begin
        #(time_period / 2) clock = ~clock;
    end

endmodule