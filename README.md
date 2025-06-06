```mermaid
graph TD
    Main[main()]
    SegLoop[seg_display_loop()]
    Init1[初始化 GPIO: 开关为输入（GPIO0）]
    Init2[初始化 GPIO: LED 为输出（GPIO0）]
    Init3[初始化 GPIO: 按键为输入（GPIO2）]
    Loop[while(1) 无限循环]

    Main --> Init1
    Main --> Init2
    Main --> Init3
    Init3 --> Loop
    Loop --> SegLoop

    subgraph seg_display_loop() 功能模块
        A1[读取按钮状态]
        A2[按键调速逻辑]
        A3[读取拨码开关数据]
        A4[转换段码（HEX）]
        A5[刷新当前数码管位]
        A6[熄灭当前位]
        A7[current_digit 更新]
        A8[LED走马灯计数+移动]
        A9[更新LED输出]
    end

    SegLoop --> A1 --> A2 --> A3 --> A4 --> A5 --> A6 --> A7 --> A8 --> A9
```
