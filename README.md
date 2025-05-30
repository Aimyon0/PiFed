graph TD

A[程序启动] --> B[GPIO、UART、Timer 初始化]
B --> C[启动Timer计数器和中断]
C --> D[启用UART1和UART2中断]
D --> E[允许MicroBlaze中断]

E --> F[主循环]
F --> G[UART1_SEND_SWITCH：读取开关状态发送到UART1]
F --> H[UART2_SEND_BUTTON：读取按钮状态发送到UART2]
G --> I[等待100ms]
H --> I

E -->|中断发生| J[My_ISR 总中断处理函数]
J --> K[判断是否为Timer中断 → Seg_TimerCounterHandler]
J --> L[判断是否为UART1中断 → UART_RECV_UART1]
J --> M[判断是否为UART2中断 → UART_RECV_UART2]

K --> K1[更新段码显示内容和位置]
L --> L1[读取接收到的按钮值 → 更新code[]数组]
M --> M1[读取接收到的开关值 → 显示到LED]

J --> N[清除当前中断标志]
