; resume.g
; called before a print from SD card is resumed
;
G1 R1 X0 Y0 Z10 F5000    ; go to 2mm above position of the last print move
G1 R1 X0 Y0 Z0          ; go back to the last print move
M83                     ; relative extruder moves
G1 E3 F3600             ; extrude 3mm of filament