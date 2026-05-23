```mermaid
graph TD

    Main[main()]
    Init1[Init GPIO0: switches as input]
    Init2[Init GPIO0: LEDs as output]
    Init3[Init GPIO2: buttons as input]
    Loop[while(1)]
    SegLoop[seg_display_loop()]

    BtnRead[Read buttons]
    BtnSpeed[Adjust speed]
    SwRead[Read switches]
    HexConv[Convert to HEX segcode]
    ShowDigit[Display current digit]
    ClearDigit[Clear digit to avoid ghosting]
    NextDigit[Update current digit index]
    LedCount[LED shift counter + update]
    LedOut[Update LED output]

    Main --> Init1
    Main --> Init2
    Main --> Init3
    Init3 --> Loop
    Loop --> SegLoop

    SegLoop --> BtnRead
    BtnRead --> BtnSpeed
    BtnSpeed --> SwRead
    SwRead --> HexConv
    HexConv --> ShowDigit
    ShowDigit --> ClearDigit
    ClearDigit --> NextDigit
    NextDigit --> LedCount
    LedCount --> LedOut
```
