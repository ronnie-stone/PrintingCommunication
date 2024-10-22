; pause.g
; called when a print from SD card is paused
;
M83					; relative extruder moves
G1 E-3 F2500		; retract 4mm
G91					; set to relative positioning
G1 Z10 F5000			; raise nozzle 2mm
G90					; absolute moves
G1 X150 Y381 F5000	; move head out of the way of the print


M120                ; Push the state of the machine onto a stack.
G91                 ; Set to relative positioning
G1 Z25 F6000        ; raise nozzle 25mm
M121                ; Recover the last state pushed onto the stack.