`timescale 1ns / 1ps
module SimpleCPU(clk, rst, data_fromRAM, wrEn, addr_toRAM, data_toRAM, pCounter);
 
parameter ADDR_LEN = 14;

input clk, rst;
input wire [31:0] data_fromRAM;
output reg wrEn;
output reg [ADDR_LEN-1:0] addr_toRAM;
output reg [31:0] data_toRAM;
output reg [ADDR_LEN-1:0] pCounter;

// internal signals
reg [ADDR_LEN-1:0] pCounterNext;
reg [ 3:0] opcode, opcodeNext;
reg [13:0] operand1, operand2, operand1Next, operand2Next;
reg [31:0] num1, num2, num1Next, num2Next;
reg [ 2:0] state, stateNext;


always @(posedge clk)begin
	state    <= #1 stateNext;
	pCounter <= #1 pCounterNext;
	opcode   <= #1 opcodeNext;
	operand1 <= #1 operand1Next;
	operand2 <= #1 operand2Next;
	num1     <= #1 num1Next;
	num2     <= #1 num2Next;
end

always @*begin
	stateNext    = state;
	pCounterNext = pCounter;
	opcodeNext   = opcode;
	operand1Next = operand1;
	operand2Next = operand2;
	num1Next     = num1;
	num2Next     = num2;
	addr_toRAM   = 0;
	wrEn         = 0;
	data_toRAM   = 0;
if(rst)
	begin
	stateNext    = 0;
	pCounterNext = 0;
	opcodeNext   = 0;
	operand1Next = 0;
	operand2Next = 0;
	num1Next     = 0;
	num2Next     = 0;
	addr_toRAM   = 0;
	wrEn         = 0;
	data_toRAM   = 0;
	end
else 
	case(state)                       
		0: begin         // "addr_toRAM = 0" => read first memory location 
			pCounterNext = pCounter;
			opcodeNext   = opcode;
			operand1Next = 0;
			operand2Next = 0;
			addr_toRAM   = pCounter;
			num1Next     = 0;
			num2Next     = 0;
			wrEn         = 0;
			data_toRAM   = 0;
			stateNext    = 1;
		end 
		1:begin          // take opcode and request *A
			pCounterNext = pCounter;
			opcodeNext   = data_fromRAM[31:28];
			operand1Next = data_fromRAM[27:14];
			operand2Next = data_fromRAM[13: 0];
			addr_toRAM   = data_fromRAM[27:14];
			num1Next     = 0;
			num2Next     = 0;
			wrEn         = 0;
			data_toRAM   = 0;
			if(opcodeNext == 4'b1101) // BZJi
				stateNext = 5;
			if(opcodeNext == 4'b0000) // ADD INSTRUCTION
				stateNext = 2;
			if(opcodeNext == 4'b1100) // BZJ
				stateNext = 2;
			if(opcodeNext == 4'b0001) // ADDi INSTRUCTION
				stateNext = 6;
			if(opcodeNext == 4'b1000) begin // CP INSTRUCTION
				addr_toRAM   = data_fromRAM[13: 0];
				stateNext = 3;
			end
			if(opcodeNext == 4'b1001) begin // CPi INSTRUCTION
				wrEn         = 1;
				data_toRAM   = data_fromRAM[13: 0];
				pCounterNext = pCounter + 1;
				stateNext = 0;
			end

		end
		2: begin         // request *B and take *A
			pCounterNext = pCounter;
			opcodeNext   = opcode;
			operand1Next = operand1;
			operand2Next = operand2;
			addr_toRAM   = operand2;
			num1Next     = data_fromRAM;
			num2Next     = 0;
			wrEn         = 0;
			data_toRAM   = 0;
			if(opcode == 4'b1100) begin
				stateNext = 7;	
			end	else begin	
				stateNext = 3;
			end
		end
		3: begin         // take *B 
			pCounterNext = pCounter + 1;
			opcodeNext = opcode;
			operand1Next = operand1;
			operand2Next = operand2;
			addr_toRAM = operand1;
			num1Next = num1;
			num2Next = data_fromRAM;
			wrEn = 1;
			if(opcode == 4'b0000)
				data_toRAM = num1 + data_fromRAM;
			if(opcodeNext == 4'b1000) // CP INSTRUCTION
				data_toRAM   = data_fromRAM;
			stateNext = 0;
		end
		5: begin
			pCounterNext = data_fromRAM + operand2;
			opcodeNext   = opcode;
			operand1Next = operand1;
			operand2Next = operand2;
			addr_toRAM   = operand1;	
			num1Next     = data_fromRAM;
			num2Next     = operand2;
			wrEn         = 0;
			data_toRAM   = 32'hFFFF_FFFF;
			stateNext = 0;
		end
		
		6: begin         // take *A and add with B
			pCounterNext = pCounter + 1;
			opcodeNext   = opcode;
			operand1Next = operand1;
			operand2Next = operand2;
			addr_toRAM   = operand1;
			num1Next     = data_fromRAM;
			num2Next     = operand2;
			wrEn         = 1;
			data_toRAM   = num1Next + num2Next;
			stateNext    = 0;
		end
		
		7: begin         // take *B and set pcounter
			if(data_fromRAM  == 0) begin
				pCounterNext = num1;
			end else begin
				pCounterNext = pCounter + 1;
			end
			stateNext    = 0;
		end		
	
		default: begin
			stateNext    = 0;
			pCounterNext = 0;
			opcodeNext   = 0;
			operand1Next = 0;
			operand2Next = 0;
			num1Next     = 0;
			num2Next     = 0;
			addr_toRAM   = 0;
			wrEn         = 0;
			data_toRAM   = 0;
		end
	endcase

end

endmodule
