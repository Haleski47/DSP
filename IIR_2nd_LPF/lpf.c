// top module "gyro_adc_dp_v2" for Sinc and Notch filter 
// Authors: Siqi.Hui
// Date: 2025-10-06
// Description: 
//     1. ignore busy and clk signals
//     2. fix bug when mod 32768


#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <string.h>

#define CLIP(x, low, high)   ((x) < (low) ? (low) : ((x) > (high) ? (high) : (x)))
#define DECIMAL_BIT 11

static inline void mul_add(int64_t *sum, int data, int coeff)
{
    *sum += (int64_t)data * coeff;
    return ;
}

void lpf(
    bool        rst_n,
    int         coeffs_0,
    int         coeffs_1,
    int         coeffs_2,
    int         coeffs_3,
    int         coeffs_4,

    int         din_data,

    int*        dout_data,
    int*        dout_frac
){

    // ---------------------------
    // 内部缓存前几拍的旧数据
    // ---------------------------
    
    static int cached_integer_data[4] = {0};  // x[n-1], x[n-2], y[n-1], y[n-2]
    static int cached_y1_decimal_data = 0;
    static int cached_y2_decimal_data = 0;
    // printf("%d, %d, %d, %d \n", cached_integer_data[0], cached_integer_data[1], cached_integer_data[2], cached_integer_data[3]);

    if (!rst_n){
        memset(cached_integer_data, 0, sizeof(cached_integer_data));
        cached_y1_decimal_data = 0;
        cached_y2_decimal_data = 0;
        *dout_data = 0;
        *dout_frac = 0;
        return ;
    }

    // sel = 1, 2, 3 对应通道 x, y, z
    int64_t tmp_sum_val = 0;
    int x = din_data;

    // y1, y2 部分 (反馈)
    mul_add(&tmp_sum_val, cached_y1_decimal_data, coeffs_3);
    mul_add(&tmp_sum_val, cached_y2_decimal_data, coeffs_4);
    // printf("sum1 : %ld \n", tmp_sum_val);
    tmp_sum_val >>= DECIMAL_BIT;
    // printf("--------------- \n");
    // printf("sum2 : %ld \n", tmp_sum_val);

    // x[n], x[n-1], x[n-2], ...
    mul_add(&tmp_sum_val, x,                      coeffs_0);
    mul_add(&tmp_sum_val, cached_integer_data[0], coeffs_1);
    mul_add(&tmp_sum_val, cached_integer_data[1], coeffs_2);
    mul_add(&tmp_sum_val, cached_integer_data[2], coeffs_3);
    mul_add(&tmp_sum_val, cached_integer_data[3], coeffs_4);
    // printf("%d, %d, %d, %d, %d \n", coeffs_0, coeffs_1, coeffs_2, coeffs_3, coeffs_4);
    // printf("%d, %d, %d, %d, %d \n", x, cached_integer_data[0], cached_integer_data[1], cached_integer_data[2], cached_integer_data[3]);
    // printf("sum2 : %ld \n", tmp_sum_val);
    // y2 = -y1
    cached_y2_decimal_data = -cached_y1_decimal_data;
    cached_y1_decimal_data = (((tmp_sum_val % 32768) + 32768) % 32768) >> 4;
    // printf("new frac: %d \n", cached_y1_decimal_data);
    // cached_y1_decimal_data = (tmp_sum_val % 32768) >> 4; 20251015 found bug

    // 小数部分右移
    tmp_sum_val >>= 15;
    // printf("new int: %ld \n", tmp_sum_val);

    // 剪裁输出
    int y = (int)CLIP(tmp_sum_val, -32767, 32767);

    // 更新小数缓存
    if (tmp_sum_val < -32767 || tmp_sum_val > 32767)
            cached_y1_decimal_data = 0;

    // 更新整数缓存
    cached_integer_data[1] = cached_integer_data[0];
    cached_integer_data[0] = x;
    cached_integer_data[3] = -cached_integer_data[2];
    cached_integer_data[2] = y;

    *dout_data = y;                         
    *dout_frac = cached_y1_decimal_data;

    return ;
}
