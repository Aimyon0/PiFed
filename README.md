```mermaid
graph TD

    Main[main()]
    Init1[初始化 GPIO: 开关为输入（GPIO0）]
    Init2[初始化 GPIO: LED 为输出（GPIO0）]
    Init3[初始化 GPIO: 按键为输入（GPIO2）]
    Loop[while(1) 无限循环]
    SegLoop[seg_display_loop()]

    A1[读取按钮状态]
    A2[按键调速逻辑]
    A3[读取拨码开关数据]
    A4[转换段码（HEX）]
    A5[刷新当前数码管位]
    A6[熄灭当前位]
    A7[更新 current_digit]
    A8[LED走马灯计数+移动]
    A9[更新LED输出]

    Main --> Init1
    Main --> Init2
    Main --> Init3
    Init3 --> Loop
    Loop --> SegLoop

    SegLoop --> A1
    A1 --> A2
    A2 --> A3
    A3 --> A4
    A4 --> A5
    A5 --> A6
    A6 --> A7
    A7 --> A8
    A8 --> A9
```
