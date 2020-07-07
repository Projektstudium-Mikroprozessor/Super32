-- ########################################################{{spacer}}####
-- # Autogenerated @ {{date}} from source: {{source}} #
-- ########################################################{{spacer}}####

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;
USE ieee.numeric_std.ALL;
USE work.definitions.ALL;

ENTITY rom_{{name}} IS
	PORT (
		-- inputs
		addr	: IN word;	-- address

		-- outputs
		data	: OUT word	-- data output
	);
END rom_{{name}};

ARCHITECTURE behavioural OF rom_{{name}} IS
BEGIN
	PROCESS (addr)

		TYPE memory_bank IS ARRAY(0 TO {{mem_size}}) OF word; 		-- memory bank, max length 2**30 (4 * 1GB)
		VARIABLE values	: memory_bank := (			        -- memory values
{{memory}}
		);

	BEGIN
		data <= values(to_integer(unsigned(addr) mod (4 * values'length) / 4));	-- read from address to data output
	END PROCESS;
END behavioural;

LIBRARY ieee;
USE ieee.std_logic_1164.ALL;
USE ieee.std_logic_unsigned.ALL;
USE ieee.numeric_std.ALL;
USE work.definitions.ALL;

ENTITY memory_{{name}} IS
	PORT (
		-- control signals
		clock	: IN std_logic;	-- clock
		rw	: IN std_logic; -- read / write

		-- inputs
		addr	: IN word;	-- address
		data_in	: IN word;	-- data input

		-- outputs
		data	: OUT word	-- data output
	);
END memory_{{name}};

ARCHITECTURE behavioural OF memory_{{name}} IS
BEGIN
	PROCESS (clock, addr)

		TYPE memory_bank IS ARRAY(0 TO 2**20-1) OF word;	-- memory bank, max length 2**30 (4 * 1GB)
		VARIABLE values	: memory_bank := (			        -- memory values
{{memory}},
			OTHERS => (OTHERS => '0')
		);

	BEGIN
		IF clock'event AND clock = '1' THEN
			IF rw = '1' THEN
				values(to_integer(unsigned(addr) mod (4 * values'length) / 4)) := data_in;	-- write data input to address
			END IF;
		END IF;
		
		data <= values(to_integer(unsigned(addr) mod (4 * values'length) / 4));				-- read from address to data output
	END PROCESS;
END behavioural;